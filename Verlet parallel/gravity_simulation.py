import threading
import numpy as np
import pyopencl as cl
from copy import deepcopy
from pyopencl import cltypes
import multiprocessing as mp
from scipy.integrate import odeint
from verlet_cython import calculate_verlet_cython

NODES = 6


def calculate_system_motion(method_name, particles, max_time, tick_count):
    data = _convert_object_to_array(particles)
    method = _select_method(method_name)
    return method(data, max_time, tick_count)


def calculate_particle_motion(method_name, particles, delta_t):
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
    if 'sequential' in method_name:
        method = calculate_verlet
    elif 'threading' in method_name:
        method = calculate_verlet_threading
    elif 'multiprocessing' in method_name:
        method = calculate_verlet_multiprocessing
    elif 'cython' in method_name:
        method = calculate_verlet_cython
    elif 'opencl' in method_name:
        method = calculate_verlet_opencl
    else:
        method = calculate_odeint
    return method


def _calculate_acceleration(data, index, N):
    G = 6.6743015 * (10 ** -11)
    acc = np.array([.0, .0])

    for i in range(N):
        if i != index:
            dist = data[NODES * i: NODES * i + 2] - data[NODES * index: NODES * index + 2]
            # if np.linalg.norm(dist) > data[NODES * i + 4] + data[NODES * index + 4]:
            acc += G * data[NODES * i + 5] * dist / (np.linalg.norm(dist) ** 3)
    return acc


def calculate_odeint(data, max_time, tick_count):
    shape = (tick_count, len(data), len(data[0]))
    data = data.ravel()
    init = deepcopy(data)
    delta_t = max_time / tick_count
    time_span = np.linspace(delta_t, max_time, tick_count)
    result = odeint(_calculate_derivatives, init, time_span, args=(shape[1],))
    return result.reshape(shape)


def _calculate_derivatives(data, time_span, N):
    result = np.zeros(N * NODES)
    for i in range(N):
        result[NODES * i: NODES * i + 2] = data[NODES * i + 2: NODES * i + 4]
        result[NODES * i + 2: NODES * i + 4] = _calculate_acceleration(data, i, N)
    return result


def calculate_verlet(data, max_time, tick_count):
    delta_t = max_time / tick_count
    shape = (tick_count, len(data), len(data[0]))
    size = shape[1] * shape[2]
    data = data.ravel()
    result = np.zeros((shape[0] * shape[1] * shape[2]))
    result[:size] = deepcopy(data)

    for i in range(1, tick_count):
        _run_verlet(data, delta_t, shape[1])
        result[i * size: (i + 1) * size] = deepcopy(data)
    return result.reshape(shape)


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
        data[NODES * i: NODES * i + 2] += data[NODES * i + 2: NODES * i + 4] * delta_t \
                                          + 0.5 * prev_accs[i] * delta_t ** 2


def _update_speed(data, prev_accs, delta_t, i_start, i_end, N):
    for i in range(i_start, i_end):
        cur_acc = _calculate_acceleration(data, i, N)
        data[NODES * i + 2: NODES * i + 4] += 0.5 * (prev_accs[i] + cur_acc) * delta_t


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


def _run_threading(data, max_time, tick_count, result,
                   barrier, i_start, i_end, size, N):
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
    queue.put([NODES * i_start, NODES * i_end,
               data[NODES * i_start: NODES * i_end]])
    barrier.wait()

    if i_start == 0:
        for i in range(processes_count):
            temp = queue.get()
            shared_data[temp[0]: temp[1]] = temp[2]
    barrier.wait()
    data[:] = np.frombuffer(shared_data.get_obj())


def calculate_verlet_opencl(data, max_time, tick_count):
    N = np.array(len(data))
    M = np.array(tick_count)
    nodes = np.array(NODES)
    delta_t = max_time / tick_count
    delta_t = np.array(delta_t)

    platform = cl.get_platforms()
    devices = platform[0].get_devices(device_type=cl.device_type.CPU)
    ctx = cl.Context(devices=devices)
    queue = cl.CommandQueue(ctx)

    prev_data = np.array(data, dtype=cltypes.double)
    cur_data = deepcopy(prev_data)
    result = np.zeros((M, N, NODES), dtype=cltypes.double)
    prev_accs = np.zeros((N, 2), dtype=cltypes.double)
    cur_accs = np.zeros((N, 2), dtype=cltypes.double)

    mf = cl.mem_flags
    M_buff = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=M)
    N_buff = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=N)
    nodes_buff = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=nodes)
    delta_t_buff = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=delta_t)
    prev_data_buff = cl.Buffer(ctx, mf.READ_WRITE | mf.COPY_HOST_PTR, hostbuf=prev_data)
    cur_data_buff = cl.Buffer(ctx, mf.READ_WRITE | mf.COPY_HOST_PTR, hostbuf=cur_data)
    prev_accs_buff = cl.Buffer(ctx, mf.READ_WRITE | mf.COPY_HOST_PTR, hostbuf=prev_accs)
    cur_accs_buff = cl.Buffer(ctx, mf.READ_WRITE | mf.COPY_HOST_PTR, hostbuf=cur_accs)
    result_buff = cl.Buffer(ctx, mf.WRITE_ONLY, result.nbytes)

    source = """
             #pragma OPENCL EXTENSION cl_khr_fp64 : enable

             double calculate_norm(__global double *data, int nodes, int i, int j)
             {
                 double temp = 0;
                 for (int k = 0; k < 2; ++k)
                     temp += pow((data[nodes * i + k] - data[nodes * j + k]), 2);
                 return sqrt(temp);
             }

             void calculate_acceleration(__global double *data, __global double *accs,
                                         int N, int nodes, int index)
             {
                 double G = 6.6743015 * pow(10.0, -11);

                 for (int k = 0; k < 2; ++k)
                     accs[2 * index + k] = 0;

                 for (int i = 0; i < N; ++i)
                     if (i != index)
                         for (int k = 0; k < 2; ++k)
                             accs[2 * index + k] += (G * data[nodes * i + 5]
                                                     * (data[nodes * i + k] - data[nodes * index + k])
                                                     / pow(calculate_norm(data, nodes, i, index), 3));
             }

             void update_coordinates(__global double *prev_data, __global double *cur_data,
                                     __global double *accs, double delta_t, int N, int nodes)
             {
                 for (int j = 0; j < N; ++j)
                     for (int k = 0; k < 2; ++k)
                         cur_data[nodes * j + k] = (prev_data[nodes * j + k]
                                                    + prev_data[nodes * j + k + 2] * delta_t
                                                    + 0.5 * accs[2 * j + k] * pow(delta_t, 2));
             }

             void update_speed(__global double *prev_data, __global double *cur_data,
                               __global double *prev_accs, __global double *cur_accs,
                               double delta_t, int N, int nodes)
             {
                 for (int j = 0; j < N; ++j)
                     for (int k = 0; k < 2; ++k)
                         cur_data[nodes * j + k + 2] = (prev_data[nodes * j + k + 2]
                                                        + 0.5 * (prev_accs[2 * j + k]
                                                                 + cur_accs[2 * j + k]) * delta_t);
             }

             __kernel void verlet_opencl(__global double *prev_data, __global double *cur_data,
                                         __global double *prev_accs, __global double *cur_accs,
                                         __global double *result, __global double *delta_t_buff,
                                         __global int *M_buff, __global int *N_buff, __global int *nodes_buff)
             {
                 int M = *M_buff;
                 int N = *N_buff;
                 int nodes = *nodes_buff;
                 double delta_t = *delta_t_buff;

                 for (int j = 0; j < N; ++j)
                     for (int k = 0; k < 4; ++k)
                         result[nodes * j + k] = prev_data[nodes * j + k];

                 for (int i = 1; i < M; ++i)
                 {
                     for (int j = 0; j < N; ++j)
                         calculate_acceleration(prev_data, prev_accs, N, nodes, j);

                     update_coordinates(prev_data, cur_data, prev_accs, delta_t, N, nodes);

                     for (int j = 0; j < N; ++j)
                         calculate_acceleration(cur_data, cur_accs, N, nodes, j);

                     update_speed(prev_data, cur_data, prev_accs, cur_accs, delta_t, N, nodes);

                     for (int j = 0; j < N; ++j)
                         for (int k = 0; k < 2; ++k)
                         {
                             prev_data[nodes * j + k] = cur_data[nodes * j + k];
                             prev_data[nodes * j + k + 2] = cur_data[nodes * j + k + 2];
                             prev_accs[2 * j + k] = cur_accs[2 * j + k];
                             result[nodes * (N * i + j) + k] = cur_data[nodes * j + k];
                             result[nodes * (N * i + j) + k + 2] = cur_data[nodes * j + k + 2];
                         }
                 }
             }"""

    program = cl.Program(ctx, source)
    program.build()
    program.verlet_opencl(queue, (1,), None, prev_data_buff, cur_data_buff, prev_accs_buff,
                          cur_accs_buff, result_buff, delta_t_buff, M_buff, N_buff, nodes_buff)
    cl.enqueue_copy(queue, result, result_buff).wait()
    return result
