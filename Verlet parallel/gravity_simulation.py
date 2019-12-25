import numpy as np
from copy import deepcopy
from scipy.integrate import odeint


def _calculate_acceleration(particles, index):
    G = 6.6743015 * (10 ** -11)
    acceleration = np.array([.0, .0])

    for i, p in enumerate(particles):
        if i != index:
            dist = np.array(p.coordinates) - np.array(particles[index].coordinates)
            if np.linalg.norm(dist) > p.radius + particles[index].radius:
                acceleration += G * p.mass * dist / (np.linalg.norm(dist) ** 3)
    return acceleration


def _calculate_derivatives(initial, t, particles, index):
    x_coord, y_coord, u_speed, v_speed = initial
    particles[index].coordinates = [x_coord, y_coord]
    acc_x, acc_y = _calculate_acceleration(particles, index)
    return [u_speed, v_speed, acc_x, acc_y]


def calculate_system_motion(particles, delta_t, method_name):
    if not particles:
        return []

    if len(particles) == 1:
        if particles[0].life_time == 0:
            particles.clear()
        else:
            p = particles[0]
            p.coordinates += np.array(p.speed)
            particles[0].life_time -= 1
        return particles

    particles = [p for p in particles if p.life_time > 0]

    if method_name == 'Verlet':
        _calculate_verlet(particles, delta_t)
    else:
        _calculate_odeint(particles, delta_t)
    return particles


def _calculate_odeint(particles, delta_t):
    for i, p in enumerate(particles):
        p = particles[i]
        y_init = [p.coordinates[0], p.coordinates[1],
                  p.speed[0], p.speed[1]]
        solution = odeint(func=_calculate_derivatives, y0=y_init,
                          t=np.linspace(0, delta_t, 2), args=(particles, i))
        x_coord, y_coord, u_speed, v_speed = solution[-1]
        p.coordinates = [x_coord, y_coord]
        p.speed = [u_speed, v_speed]
        p.life_time -= 1


def _calculate_verlet(particles, delta_t):
    i_start = 0
    i_end = len(particles)
    prev_particles = deepcopy(particles)
    prev_accelerations = np.zeros((len(particles), 2))
    _update_coordinates(particles, prev_particles, prev_accelerations, delta_t, i_start, i_end)
    _update_speed(particles, prev_accelerations, delta_t, i_start, i_end)


def _update_coordinates(particles, prev_particles,
                        prev_accelerations, delta_t, i_start, i_end):
    for i in range(i_start, i_end):
        p = particles[i]
        prev_accelerations[i] = _calculate_acceleration(prev_particles, i)
        p.coordinates += (np.array(p.speed) * delta_t
                          + 0.5 * prev_accelerations[i] * delta_t ** 2)


def _update_speed(particles, prev_accelerations, delta_t, i_start, i_end):
    for i in range(i_start, i_end):
        p = particles[i]
        cur_acceleration = _calculate_acceleration(particles, i)
        p.speed += 0.5 * (prev_accelerations[i] + cur_acceleration) * delta_t
        p.life_time -= 1
