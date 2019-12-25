import numpy as np
from copy import deepcopy
from scipy.integrate import odeint


def calculate_system_motion(particles, max_time, tick_count, method_name):
    data = _convert_object_to_array(particles)
    method = _select_method(method_name)
    result = _run_method(data, max_time, tick_count, method)
    return result


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
    for p in particles:
        p.life_time -= 1

    data = _convert_object_to_array(particles)
    method = _select_method(method_name)
    result = method(data, delta_t)
    return _convert_array_to_object(result, particles)


def _select_method(method_name):
    if method_name == 'Verlet':
        method = calculate_verlet
    else:
        method = calculate_odeint
    return method


def _run_method(data, max_time, tick_count, method):
    delta_t = max_time / tick_count
    result = np.zeros((tick_count, len(data), len(data[0])))
    result[0] = deepcopy(data)

    for i in range(1, tick_count):
        method(data, delta_t)
        result[i] = deepcopy(data)
    return result


def _calculate_acceleration(data, index):
    G = 6.6743015 * (10 ** -11)
    acceleration = np.array([.0, .0])

    for i in range(len(data)):
        if i != index:
            dist = data[i, :2] - data[index, :2]
            if np.linalg.norm(dist) > data[i, 4] + data[index, 4]:
                acceleration += G * data[i, 5] * dist / (np.linalg.norm(dist) ** 3)
    return acceleration


def _calculate_derivatives(initial, t, data, index):
    x_coord, y_coord, u_speed, v_speed = initial
    data[index, :2] = [x_coord, y_coord]
    acc_x, acc_y = _calculate_acceleration(data, index)
    return [u_speed, v_speed, acc_x, acc_y]


def calculate_odeint(data, delta_t):
    for i in range(len(data)):
        y_init = data[i, :4]
        solution = odeint(func=_calculate_derivatives, y0=y_init,
                          t=np.linspace(0, delta_t, 2), args=(data, i))
        x_coord, y_coord, u_speed, v_speed = solution[-1]
        data[i, :4] = [x_coord, y_coord, u_speed, v_speed]
    return data


def calculate_verlet(data, delta_t):
    i_start = 0
    i_end = len(data)
    prev_data = deepcopy(data)
    prev_accelerations = np.zeros((len(data), 2))
    _update_coordinates(data, prev_data, prev_accelerations, delta_t, i_start, i_end)
    _update_speed(data, prev_accelerations, delta_t, i_start, i_end)
    return data


def _update_coordinates(data, prev_data,
                        prev_accelerations, delta_t, i_start, i_end):
    for i in range(i_start, i_end):
        d = data[i]
        prev_accelerations[i] = _calculate_acceleration(prev_data, i)
        d[:2] += (d[2:4] * delta_t
                  + 0.5 * prev_accelerations[i] * delta_t ** 2)


def _update_speed(data, prev_accelerations, delta_t, i_start, i_end):
    for i in range(i_start, i_end):
        d = data[i]
        cur_acceleration = _calculate_acceleration(data, i)
        d[2:4] += 0.5 * (prev_accelerations[i] + cur_acceleration) * delta_t


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
