import numpy as np
from time import time
from copy import deepcopy
import matplotlib.pyplot as plt

from emitter import Emitter
from loading import load_data
from gravity_simulation import calculate_system_motion


def compare_methods(method_names=['Odeint', 'Verlet']):
    emitter = Emitter()
    file_to_read = 'solar_system.json'
    load_data(file_to_read, emitter)
    particles_1 = emitter.particles
    particles_2 = deepcopy(particles_1)

    delta_t = 0.1
    tick_count = 100
    metric_list = []
    exec_time = {method_names[0]: .0, method_names[1]: .0}

    for i in range(tick_count):
        if not particles_1 or not particles_2:
            break

        start_time = time()
        particles_1 = calculate_system_motion(particles_1, delta_t, method_names[0])
        exec_time[method_names[0]] += time() - start_time

        start_time = time()
        particles_2 = calculate_system_motion(particles_2, delta_t, method_names[1])
        exec_time[method_names[1]] += time() - start_time

        metric = .0
        for p_1, p_2 in zip(particles_1, particles_2):
            dist = np.array(p_1.coordinates) - np.array(p_2.coordinates)
            metric += np.linalg.norm(dist)
        metric_list.append(metric)

    ticks = range(len(metric_list))
    _built_plot(ticks, metric_list, method_names, delta_t)
    test_file = 'test.txt'
    _write_to_file(test_file, exec_time, metric_list, delta_t)


def _built_plot(ticks, metric_list, method_names, delta_t):
    plt.plot(ticks, metric_list)
    plt.grid()
    plt.xlabel('ticks')
    plt.ylabel('metric')
    plt.savefig(f'compare_{method_names[0]}_{method_names[1]}_{delta_t}.png')
    plt.show()


def _write_to_file(file_name, exec_time, metric_list, delta_t):
    with open(file_name, 'a') as file:
        mean_metric = np.mean(metric_list)
        result = f'{exec_time}\n'
        result += f'Delta_t: {delta_t}, tick count: {len(metric_list)}\n'
        result += f'Mean metric: {mean_metric}\n'
        result += f'{metric_list}\n\n'
        file.write(result)


if __name__ == "__main__":
    compare_methods()
