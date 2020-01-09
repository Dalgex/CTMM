import numpy as np
from time import time
from copy import deepcopy
import matplotlib.pyplot as plt

from emitter import Emitter
from loading import load_data
from gravity_simulation import calculate_system_motion


def compare_methods_accuracy(method_names, max_time, tick_count, particles_count=None):
    emitter = Emitter()
    if particles_count is None:
        file_to_read = 'solar_system.json'
        load_data(file_to_read, emitter)
        particles = emitter.particles
    else:
        particles = emitter.generate_particles(particles_count)

    ticks = range(tick_count)
    total_metric_list = []
    runtime = []
    results = []

    for name in method_names:
        print(f'{name} is executed')
        start_time = time()
        result = calculate_system_motion(name, deepcopy(particles), max_time, tick_count)
        runtime.append(time() - start_time)
        results.append(result)

    for i in range(len(results)):
        local_metric_list = []
        for j in range(len(results[0])):
            metric = .0
            for k in range(len(results[0][0])):
                dist = results[0][j][k][:2] - results[i][j][k][:2]
                metric += np.linalg.norm(dist)
            local_metric_list.append(metric)
        total_metric_list.append(local_metric_list)

    delta_t = max_time / tick_count
    _built_metric_plot(method_names, ticks, total_metric_list, delta_t)
    test_file = 'test.txt'
    _write_to_file(test_file, method_names, len(particles),
                   runtime, total_metric_list, delta_t)


def compare_methods_runtime(method_names, count_list, max_time, tick_count, iter_count=3):
    particles = []
    emitter = Emitter()
    for count in count_list:
        particles.append(emitter.generate_particles(count))

    runtime = []
    for name in method_names:
        print(f'{name} is executed')
        result = calculate_method_runtime(name, particles, max_time, tick_count, iter_count)
        runtime.append(result)

    ylabel = 'time'
    _build_time_plot(method_names, count_list, runtime, ylabel)
    speedups = calculate_methods_speedup(method_names, runtime)
    ylabel = 'speedup'
    _build_time_plot(method_names, count_list, speedups, ylabel)


def calculate_methods_speedup(method_names, runtime):
    speedups = []
    for i in range(len(method_names)):
        speedups.append(np.divide(runtime[0], runtime[i]))
    return speedups


def calculate_method_runtime(method_name, particles, max_time, tick_count, iter_count=3):
    results = []
    for i in range(len(particles)):
        print(f'{len(particles[i])} particles are calculated')
        runtime = []
        for j in range(iter_count):
            start_time = time()
            calculate_system_motion(method_name, particles[i], max_time, tick_count)
            runtime.append(time() - start_time)
        results.append(np.mean(runtime))
    return results


def _build_time_plot(method_names, count_list, results, ylabel):
    for i in range(len(method_names)):
        plt.plot(count_list, results[i], label=method_names[i])
    plt.xlabel('particles')
    plt.ylabel(ylabel)
    plt.legend()
    plt.grid()
    title_name = f'compare_{ylabel}'
    plt.title(title_name)
    plt.savefig(f'{title_name}_{count_list}.png')
    plt.show()


def _built_metric_plot(method_names, ticks, metric_list, delta_t):
    for i in range(1, len(method_names)):
        plt.plot(ticks, metric_list[i], label=method_names[i])
    plt.xlabel('ticks')
    plt.ylabel('metric')
    plt.legend()
    plt.grid()
    title_name = f'compare_with_{method_names[0]}'
    plt.title(title_name)
    plt.savefig(f'{title_name}_{delta_t}.png')
    plt.show()


def _write_to_file(file_name, method_names, particles_count,
                   exec_time, metric_list, delta_t):
    with open(file_name, 'a') as file:
        result = f'Particles count: {particles_count}, '
        result += f'delta_t: {delta_t}, '
        result += f'tick count: {len(metric_list[0])}\n'
        file.write(result)

        for i in range(len(method_names)):
            result = f'Method: {method_names[i]}, '
            result += f'time: {exec_time[i]}, '
            result += f'metric: {np.mean(metric_list[i])}\n'
            file.write(result)
        file.write('\n')


def main():
    max_time = 10
    tick_count = 100
    particles_count = 50
    method_names = ['odeint', 'verlet_sequential', 'verlet_threading',
                    'verlet_multiprocessing', 'verlet_cython', 'verlet_opencl']
    compare_methods_accuracy(method_names, max_time, tick_count, particles_count)
    iter_count = 5
    del method_names[0]
    count_list = [50, 100, 200, 400]
    compare_methods_runtime(method_names, count_list, max_time, tick_count, iter_count)


if __name__ == "__main__":
    main()
