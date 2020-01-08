import threading
import numpy as np
from copy import deepcopy
import multiprocessing as mp
from scipy.integrate import odeint
from verlet_cython import calculate_verlet_cython

NODES = 6


def calculate_system_motion(particles, max_time, tick_count, method_name):
    data = _convert_object_to_array(particles)
    method = _select_method(method_name)
    return method(data, max_time, tick_count)


def calculate_particle_motion(particles, delta_t, method_name):
    if not particles:
        return []

    if len(particles) == 1:
        if particles[0].life_time == 0:
            particles.clear()
        else:
            p = particles[0]
            p.coordinates += np.array(p.speed)
            p.life_time -= 1
        return particles

    particles = [p for p in particles if p.life_time > 0]
    if not particles:
        return []
    for p in particles:
        p.life_time -= 1

    data = _convert_object_to_array(particles)
    method = _select_method(method_name)
    tick_count = 2
    max_time = tick_count * delta_t
    result = method(data, max_time, tick_count)[1]
    return _convert_array_to_object(result, particles)


def _select_method(method_name):
    if method_name == 'verlet':
        method = calculate_verlet
    elif method_name == 'verlet-threading':
        method = calculate_verlet_threading
    elif method_name == 'verlet-multiprocessing':
        method = calculate_verlet_multiprocessing
    elif method_name == 'verlet-cython':
        method = calculate_verlet_cython
    else:
        method = calculate_odeint
    return method


def _run_method(data, max_time, tick_count, method):
    delta_t = max_time / tick_count
    shape = (tick_count, len(data), len(data[0]))
    size = shape[1] * shape[2]
    data = data.ravel()
    result = np.zeros((shape[0] * shape[1] * shape[2]))
    result[:size] = deepcopy(data)

    for i in range(1, tick_count):
        method(data, delta_t, shape[1])
        result[i * size: (i + 1) * size] = deepcopy(data)
    return result.reshape(shape)


def _calculate_acceleration(data, index, N):
    G = 6.6743015 * (10 ** -11)
    acc = np.array([.0, .0])

    for i in range(N):
        if i != index:
            dist_x = data[i * NODES] - data[index * NODES]
            dist_y = data[i * NODES + 1] - data[index * NODES + 1]
            dist = np.array([dist_x, dist_y])
            # if np.linalg.norm(dist) > data[i * NODES + 4] + data[index * NODES + 4]:
            acc += G * data[i * NODES + 5] * dist / (np.linalg.norm(dist) ** 3)
    return acc


def _calculate_derivatives(initial, t, data, index, N):
    x_coord, y_coord, u_speed, v_speed = initial
    data[index * NODES: index * NODES + 2] = [x_coord, y_coord]
    acc_x, acc_y = _calculate_acceleration(data, index, N)
    return [u_speed, v_speed, acc_x, acc_y]


def calculate_odeint(data, max_time, tick_count):
    return _run_method(data, max_time, tick_count, _run_odeint)


def _run_odeint(data, delta_t, N):
    for i in range(N):
        y_init = data[i * NODES: i * NODES + 4]
        solution = odeint(func=_calculate_derivatives, y0=y_init,
                          t=np.linspace(0, delta_t, 2), args=(data, i, N))
        x_coord, y_coord, u_speed, v_speed = solution[-1]
        data[i * NODES: i * NODES + 4] = [x_coord, y_coord, u_speed, v_speed]
    return data


def calculate_verlet(data, max_time, tick_count):
    return _run_method(data, max_time, tick_count, _run_verlet)


def _run_verlet(data, delta_t, N):
    i_start = 0
    i_end = N
    prev_data = deepcopy(data)
    prev_accs = np.zeros((N, 2))
    _update_coordinates(data, prev_data, prev_accs, delta_t, i_start, i_end, N)
    _update_speed(data, prev_accs, delta_t, i_start, i_end, N)
    return data


def _update_coordinates(data, prev_data, prev_accs, delta_t, i_start, i_end, N):
    for i in range(i_start, i_end):
        prev_accs[i] = _calculate_acceleration(prev_data, i, N)
        for k in range(2):
            data[i * NODES + k] += data[i * NODES + k + 2] * delta_t \
                                   + 0.5 * prev_accs[i][k] * delta_t ** 2


def _update_speed(data, prev_accs, delta_t, i_start, i_end, N):
    for i in range(i_start, i_end):
        cur_acc = _calculate_acceleration(data, i, N)
        for k in range(2):
            data[i * NODES + k + 2] += 0.5 * (prev_accs[i][k] + cur_acc[k]) * delta_t


def _convert_object_to_array(particles):
    data = []
    for p in particles:
        temp_list = [p.coordinates[0], p.coordinates[1],
                     p.speed[0], p.speed[1], p.radius, p.mass]
        data.append(temp_list)
    return np.array(data)


def _convert_array_to_object(data, particles):
    for i in range(len(data)):
        particles[i].coordinates[0] = data[i, 0]
        particles[i].coordinates[1] = data[i, 1]
        particles[i].speed[0] = data[i, 2]
        particles[i].speed[1] = data[i, 3]
    return particles


def calculate_verlet_threading(data, max_time, tick_count, threads_count=4):
    block = len(data) // threads_count
    shape = (tick_count, len(data), len(data[0]))
    size = shape[1] * shape[2]
    data = data.ravel()
    result = np.zeros((shape[0] * size))
    result[:size] = deepcopy(data)
    barrier = threading.Barrier(threads_count)

    threads = []
    for i in range(threads_count):
        i_start = i * block
        i_end = (i + 1) * block if i < threads_count - 1 else shape[1]
        args = [data, max_time, tick_count, result,
                barrier, i_start, i_end, size, shape[1]]
        thread = threading.Thread(target=_run_threading, args=(*args,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()
    return result.reshape(shape)


def _run_threading(data, max_time, tick_count, result, barrier, i_start, i_end, size, N):
    delta_t = max_time / tick_count
    for i in range(1, tick_count):
        _update_particles_threading(data, delta_t, barrier, i_start, i_end, N)
        result[i * size: (i + 1) * size] = deepcopy(data)


def _update_particles_threading(data, delta_t, barrier, i_start, i_end, N):
    prev_data = deepcopy(data)
    prev_accs = np.zeros((len(data), 2))
    barrier.wait()
    _update_coordinates(data, prev_data, prev_accs, delta_t, i_start, i_end, N)
    barrier.wait()
    _update_speed(data, prev_accs, delta_t, i_start, i_end, N)


def calculate_verlet_multiprocessing(data, max_time, tick_count):
    processes_count = mp.cpu_count()
    block = len(data) // processes_count
    shape = (tick_count, len(data), len(data[0]))
    size = shape[1] * shape[2]
    data = data.ravel()
    shared_data = mp.Array('d', np.zeros(size))
    result = mp.Array('d', np.zeros(shape[0] * size))
    result[:size] = deepcopy(data)
    barrier = mp.Barrier(processes_count)
    queue = mp.Queue()

    processes = []
    for i in range(processes_count):
        i_start = i * block
        i_end = (i + 1) * block if i < processes_count - 1 else shape[1]
        args = [data, max_time, tick_count, result, shared_data, barrier,
                queue, processes_count, i_start, i_end, size, shape[1]]
        process = mp.Process(target=_run_multiprocessing, args=(*args,))
        processes.append(process)
        process.start()

    for process in processes:
        process.join()
    return np.frombuffer(result.get_obj()).reshape(shape)


def _run_multiprocessing(data, max_time, tick_count, result, shared_data,
                         barrier, queue, processes_count, i_start, i_end, size, N):
    delta_t = max_time / tick_count
    for i in range(1, tick_count):
        _update_particles_multiprocessing(data, delta_t, shared_data, barrier,
                                          queue, processes_count, i_start, i_end, N)
        result[i * size: (i + 1) * size] = deepcopy(data)


def _update_particles_multiprocessing(data, delta_t, shared_data, barrier,
                                      queue, processes_count, i_start, i_end, N):
    prev_data = deepcopy(data)
    prev_accs = np.zeros((N, 2))
    _update_coordinates(data, prev_data, prev_accs, delta_t, i_start, i_end, N)
    _exchange_data_multiprocessing(data, shared_data, barrier, queue,
                                   processes_count, i_start, i_end)
    _update_speed(data, prev_accs, delta_t, i_start, i_end, N)
    _exchange_data_multiprocessing(data, shared_data, barrier, queue,
                                   processes_count, i_start, i_end)


def _exchange_data_multiprocessing(data, shared_data, barrier, queue,
                                   processes_count, i_start, i_end):
    queue.put([i_start * NODES, i_end * NODES,
               data[i_start * NODES: i_end * NODES]])
    barrier.wait()
    if mp.current_process().name[-1] == '1':
        for i in range(processes_count):
            temp = queue.get()
            shared_data[temp[0]: temp[1]] = temp[2]
    barrier.wait()
    data[:] = np.frombuffer(shared_data.get_obj())
