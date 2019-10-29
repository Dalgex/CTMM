import numpy as np
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
    prev_particles = particles.copy()

    for i, p in enumerate(particles):
        if method_name == 'Verlet':
            _calculate_verlet(particles, prev_particles, i, delta_t)
        else:
            _calculate_odeint(particles, i, delta_t)
        p.life_time -= 1
    return particles


def _calculate_odeint(particles, index, delta_t):
    p = particles[index]
    y_init = [p.coordinates[0], p.coordinates[1],
              p.speed[0], p.speed[1]]
    solution = odeint(func=_calculate_derivatives, y0=y_init,
                      t=np.linspace(0, delta_t, 2), args=(particles, index))
    x_coord, y_coord, u_speed, v_speed = solution[-1]
    p.coordinates = [x_coord, y_coord]
    p.speed = [u_speed, v_speed]


def _calculate_verlet(upd_particles, prev_particles, index, delta_t):
    p = upd_particles[index]
    p.coordinates += (delta_t * np.array(p.speed)
                      + delta_t * _calculate_acceleration(upd_particles, index) / 2)
    p.speed += (delta_t * (_calculate_acceleration(upd_particles, index)
                           + _calculate_acceleration(prev_particles, index)) / 2)
