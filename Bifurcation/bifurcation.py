import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint
from sympy import symbols, Matrix, solve, lambdify

x, y, k_3, k_1, k1, k2, k3 = symbols('x y k_3 k_1 k1 k2 k3')


def get_params(param_dict):
    return [(key, value) for key, value in param_dict.items()]


def set_variable_values(x_array, y_array):
    x_values, y_values = [], []
    for x_value, y_value in zip(x_array, y_array):
        if 0 < y_value < 1 and 0 < x_value + 2 * y_value < 1:
            x_values.append(x_value)
            y_values.append(y_value)
    return x_values, y_values


def perform_one_param_analysis(f1, f2, param_dict,
                               variable_param, updated_param):
    matrix = Matrix([f1, f2])
    variables = Matrix([x, y])
    jacobian = matrix.jacobian(variables)
    det = jacobian.det()
    trace = jacobian.trace()

    y_f2_sol = solve(f2, y)[0]
    param_sol = solve(f1, variable_param)[0]

    del param_dict[variable_param]
    det = det.subs(get_params(param_dict))
    trace = trace.subs(get_params(param_dict))
    y_f2_sol = y_f2_sol.subs(get_params(param_dict))
    param_sol = param_sol.subs(get_params(param_dict))

    x_array = np.linspace(0, 1, 1000)
    y_f2_func = lambdify(x, y_f2_sol, 'numpy')
    y_array = y_f2_func(x_array)
    x_list, y_list = set_variable_values(x_array, y_array)

    param_func = lambdify(variables, param_sol, 'numpy')
    variables = np.append(variables, variable_param)
    det_func = lambdify(variables, det, 'numpy')
    trace_func = lambdify(variables, trace, 'numpy')

    param_list = []
    det_list = []
    trace_list = []
    for i in range(len(x_list)):
        param_list.append(param_func(x_list[i], y_list[i]))
        det_list.append(det_func(x_list[i], y_list[i], param_list[i]))
        trace_list.append(trace_func(x_list[i], y_list[i], param_list[i]))

    saddle_points = []
    hopf_points = []

    for i in range(len(x_list) - 1):
        if det_list[i] * det_list[i + 1] <= 0:
            saddle_points.append([param_list[i], x_list[i]])
            saddle_points.append([param_list[i], y_list[i]])

        if trace_list[i] * trace_list[i + 1] <= 0:
            hopf_points.append([param_list[i], x_list[i]])
            hopf_points.append([param_list[i], y_list[i]])

    plt.plot(param_list, x_list, label=f'x({variable_param})')
    plt.plot(param_list, y_list, label=f'y({variable_param})')

    if hopf_points:
        x_axis, y_axis = np.transpose(hopf_points)
        plt.plot(x_axis, y_axis, 'ro', label='Hopf point')
    if saddle_points:
        x_axis, y_axis = np.transpose(saddle_points)
        plt.plot(x_axis, y_axis, 'go', label='Saddle point')

    plt.xlabel(f'{variable_param}')
    plt.ylabel('x, y')
    plt.xlim(-0.05, 0.2)
    param_str = f'{updated_param} = {param_dict[updated_param]}'
    plt.title('One-parameter analysis, ' + param_str)
    plt.legend()
    plt.show()


def is_zero(item):
    return item < 5e-4


def perform_two_param_analysis(f1, f2, param_dict, variable_params):
    matrix = Matrix([f1, f2])
    variables = Matrix([x, y])
    jacobian = matrix.jacobian(variables)
    det = jacobian.det()
    trace = jacobian.trace()

    y_f2_sol = solve(f2, y)[0]
    param2_sol = solve(f1, variable_params[1])[0]
    param2_trace_sol = solve(trace, variable_params[1])[0]
    param1_trace_sol = solve(param2_sol - param2_trace_sol, variable_params[0])[0]
    param2_det_sol = solve(det, variable_params[1])[0]
    param1_det_sol = solve(param2_sol - param2_det_sol, variable_params[0])[0]

    del param_dict[variable_params[0]]
    del param_dict[variable_params[1]]
    param1_trace_sol = param1_trace_sol.subs(get_params(param_dict))
    param1_det_sol = param1_det_sol.subs(get_params(param_dict))
    param2_sol = param2_sol.subs(get_params(param_dict))
    y_f2_sol = y_f2_sol.subs(get_params(param_dict))
    jacobian = jacobian.subs(get_params(param_dict))

    x_array = np.linspace(0, 1, 1000)
    y_f2_func = lambdify(x, y_f2_sol, 'numpy')
    y_array = y_f2_func(x_array)
    x_list, y_list = set_variable_values(x_array, y_array)

    param1_trace_func = lambdify(variables, param1_trace_sol, 'numpy')
    param1_det_func = lambdify(variables, param1_det_sol, 'numpy')
    variables = np.append(variables, variable_params[0])
    param2_func = lambdify(variables, param2_sol, 'numpy')

    param1_trace_list = []
    for i in range(len(x_list)):
        param1_trace_list.append(param1_trace_func(x_list[i], y_list[i]))

    param2_trace_list = []
    for i in range(len(x_list)):
        param2_trace_list.append(param2_func(x_list[i], y_list[i], param1_trace_list[i]))

    param1_det_list = []
    for i in range(len(x_list)):
        param1_det_list.append(param1_det_func(x_list[i], y_list[i]))

    param2_det_list = []
    for i in range(len(x_list)):
        param2_det_list.append(param2_func(x_list[i], y_list[i], param1_det_list[i]))

    eigen1, eigen2 = jacobian.eigenvals()
    variables = np.append(variables, variable_params[1])
    eigen1_func = lambdify(variables, eigen1, 'numpy')
    eigen2_func = lambdify(variables, eigen2, 'numpy')
    tb_points = []
    for i in range(len(x_list)):
        eig1 = eigen1_func(x_list[i], y_list[i], param1_trace_list[i], param2_trace_list[i])
        eig2 = eigen2_func(x_list[i], y_list[i], param1_trace_list[i], param2_trace_list[i])
        if not np.isnan(eig1) and not np.isnan(eig2) and is_zero(eig1) and is_zero(eig2):
            tb_points.append([param2_trace_list[i], param1_trace_list[i]])

    param1_det_diff = param1_det_sol.diff(x)
    param1_det_diff_func = lambdify(variables[:2], param1_det_diff, 'numpy')
    diff_list = []
    for i in range(len(x_list)):
        if is_zero(10 * np.abs(param1_det_diff_func(x_list[i], y_list[i]))):
            diff_list.append(x_list[i])

    x_c = sum(diff_list) / len(diff_list)
    y_c = y_f2_func(x_c)
    param1_c = param1_det_sol.subs({x: x_c, y: y_c})
    param2_c = param2_sol.subs({x: x_c, y: y_c, variable_params[0]: param1_c})

    plt.plot(param2_trace_list, param1_trace_list, '--', label='Neutrality line')
    plt.plot(param2_det_list, param1_det_list, label='Multiplicity line')
    plt.plot(param2_c, param1_c, 'go', label='C root')

    if tb_points:
        x_axis, y_axis = np.transpose(tb_points)
        plt.plot(x_axis, y_axis, 'ro', label='TB root')

    plt.xlabel(f'{variable_params[1]}')
    plt.ylabel(f'{variable_params[0]}')
    plt.ylim(-0.01, 0.02)
    plt.title('Two-parameter analysis')
    plt.legend()
    plt.show()


def pend(start, t, f1, f2):
    f1_subs = f1(start[0], start[1])
    f2_subs = f2(start[0], start[1])
    return [f1_subs, f2_subs]


def plot_auto_oscillations(f1, f2, param_dict):
    t = np.linspace(0, 8000, 4000)
    start = [0.2, 0.2]
    variables = [x, y]

    f1_subs = f1.subs(get_params(param_dict))
    f2_subs = f2.subs(get_params(param_dict))
    f1_func = lambdify(variables, f1_subs, 'numpy')
    f2_func = lambdify(variables, f2_subs, 'numpy')
    sol = odeint(pend, start, t, args=(f1_func, f2_func))

    plt.plot(t, sol[:, 0], label='x(t)')
    plt.plot(t, sol[:, 1], label='y(t)')
    plt.xlabel('time')
    plt.ylabel('x, y')
    plt.title('Auto oscillations')
    plt.legend()
    plt.show()


def plot_phase_portrait(f1, f2, param_dict):
    y_f2_sol = solve(f2, y)[0]
    y_f2_sol = y_f2_sol.subs(get_params(param_dict))

    x_array = np.linspace(0, 1, 1000)
    y_f2_func = lambdify(x, y_f2_sol, 'numpy')
    y_f2_array = y_f2_func(x_array)
    x_array, y_f2_array = np.array(set_variable_values(x_array, y_f2_array))

    y_f1_sol = solve(f1, y)
    y_f1_sol = [y_f1_sol[0].subs(get_params(param_dict)),
                y_f1_sol[1].subs(get_params(param_dict))]
    y_f1_func = lambdify(x, y_f1_sol, 'numpy')
    y_f1_array = y_f1_func(x_array)

    variables = [x, y]
    f1_subs = f1.subs(get_params(param_dict))
    f2_subs = f2.subs(get_params(param_dict))
    f1_func = lambdify(variables, f1_subs, 'numpy')
    f2_func = lambdify(variables, f2_subs, 'numpy')

    t = np.linspace(0, 8000, 2000)
    start_tr1 = [0.1, 0.1]
    solution_tr1 = odeint(pend, start_tr1, t, args=(f1_func, f2_func))
    start_tr2 = [0.5, 0.3]
    # start_tr2 = [0.3, 0.3]
    solution_tr2 = odeint(pend, start_tr2, t, args=(f1_func, f2_func))

    start_osc = [0.2, 0.2]
    solution_osc = odeint(pend, start_osc, t, args=(f1_func, f2_func))
    solution_cycle = odeint(pend, solution_osc[-1], t, args=(f1_func, f2_func))

    plt.figure(figsize=(9, 6))
    plt.plot(x_array, y_f1_array[0], color='blue')
    plt.plot(x_array, y_f1_array[1], color='blue', label='f1(x, y) = 0')
    plt.plot(x_array, y_f2_array, label='f2(x, y) = 0')

    plt.plot(solution_tr1[:, 0], solution_tr1[:, 1], '--',
             solution_tr2[:, 0], solution_tr2[:, 1], '--',
             label='Trajectory', alpha=0.5)

    x_direction = solution_cycle[1:, 0] - solution_cycle[:-1, 0]
    y_direction = solution_cycle[1:, 1] - solution_cycle[:-1, 1]
    plt.quiver(solution_cycle[:-1, 0], solution_cycle[:-1, 1],
               x_direction, y_direction, scale=0.6, color='red', label='Cycle')

    plt.xlabel('x')
    plt.ylabel('y')
    plt.title('Phase portrait')
    plt.xlim(0.1, 0.65)
    plt.ylim(0.07, 0.32)
    plt.legend()
    plt.show()


def get_model():
    z = 1 - x - 2 * y
    param_dict = {k_3: 0.002, k_1: 0.01, k1: 0.12, k2: 0.95, k3: 0.0032}
    dx_dt = k1 * z - k_1 * x - k3 * x * z + k_3 * y - k2 * z ** 2 * x
    dy_dt = k3 * x * z - k_3 * y
    return dx_dt, dy_dt, param_dict


def main():
    dx_dt, dy_dt, param_dict = get_model()
    variable_param = k1

    temp_dict = param_dict.copy()
    updated_param = k_1
    param_values = [0.001, 0.005, 0.01, 0.015, 0.02]
    for value in param_values:
        temp_dict[updated_param] = value
        perform_one_param_analysis(dx_dt, dy_dt, temp_dict.copy(),
                                   variable_param, updated_param)

    temp_dict = param_dict.copy()
    updated_param = k_3
    param_values = [0.0005, 0.001, 0.002, 0.003, 0.004]
    for value in param_values:
        temp_dict[updated_param] = value
        perform_one_param_analysis(dx_dt, dy_dt, temp_dict.copy(),
                                   variable_param, updated_param)

    perform_two_param_analysis(dx_dt, dy_dt, param_dict.copy(), [k_1, k1])

    param_dict[k_1] = 0.009
    param_dict[k1] = 0.114
    plot_auto_oscillations(dx_dt, dy_dt, param_dict.copy())
    plot_phase_portrait(dx_dt, dy_dt, param_dict.copy())


if __name__ == "__main__":
    main()
