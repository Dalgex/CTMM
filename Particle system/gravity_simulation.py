import numpy as np
from math import pow
from scipy.integrate import odeint


def _calculate_acceleration(particles, index):
    G = 6.67430 * pow(10, -11)
    acceleration = np.array([.0, .0])

    for i in range(len(particles)):
        if i != index:
            dist = np.array(particles[i].coordinates) - np.array(particles[index].coordinates)
            if np.linalg.norm(dist) > particles[i].radius + particles[index].radius:
                acceleration += G * particles[i].mass * dist / ((np.linalg.norm(dist)) ** 3)
    return acceleration


def _calculate_derivatives(initial, t, particles, index):
    x_coord, y_coord, u_speed, v_speed = initial
    particles[index].coordinates = [x_coord, y_coord]
    acc_x, acc_y = _calculate_acceleration(particles, index)
    return [u_speed, v_speed, acc_x, acc_y]


def calculate_odeint(particles, delta_t):
    if not particles:
        return []

    if len(particles) == 1:
        if particles[0].life_time == 0:
            particles.clear()
        else:
            particles[0].coordinates[0] += particles[0].speed[0]
            particles[0].coordinates[1] += particles[0].speed[1]
            particles[0].life_time -= 1
        return particles

    for i, p in enumerate(particles):
        if p.life_time == 0:
            particles.remove(p)
            continue

        y_init = [p.coordinates[0], p.coordinates[1],
                  p.speed[0], p.speed[1]]
        solution = odeint(func=_calculate_derivatives, y0=y_init,
                          t=np.linspace(0, delta_t, 2), args=(particles, i))
        x_coord, y_coord, u_speed, v_speed = solution[-1]
        p.coordinates = [x_coord, y_coord]
        p.speed = [u_speed, v_speed]
        p.life_time -= 1
    return particles
