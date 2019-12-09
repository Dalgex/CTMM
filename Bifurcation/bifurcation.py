import numpy as np
import matplotlib.pyplot as plt
from sympy import symbols, Matrix, solve, re

x, y, k_3, k_1, k1, k2, k3 = symbols('x y k_3 k_1 k1 k2 k3')


def perform_one_param_analysis(f1, f2, param_dict, param):
    matrix = Matrix([f1, f2])
    variables = Matrix([x, y])
    jacobian = matrix.jacobian(variables)

    del param_dict[param]
    f1_subs = f1.subs([(key, value) for key, value in param_dict.items()])
    f2_subs = f2.subs([(key, value) for key, value in param_dict.items()])
    sol = solve([f1_subs, f2_subs], x, param, dict=True)[0]

    jac_subs = jacobian.subs([(key, value) for key, value in param_dict.items()])
    jac_subs = jac_subs.subs([(param, sol[param]), (x, sol[x])])
    eigenvalues = jac_subs.eigenvals().keys()

    y_arr = np.linspace(0.001, 1, 100)
    y_bifurc = []

    for value in eigenvalues:
        eigen_arr = [re(value.subs(y, item)) for item in y_arr]
        y_points = [y_arr[j] for j in range(len(eigen_arr) - 1) if eigen_arr[j] * eigen_arr[j + 1] < 0]
        y_bifurc.extend(y_points)

    x_arr = [re(sol[x].subs(y, item)) for item in y_arr]
    param_arr = [re(sol[param].subs(y, item)) for item in y_arr]
    plt.plot(param_arr, x_arr, label=f'x({param})')
    plt.plot(param_arr, y_arr, label=f'y({param})')

    x_bifurc = [re(sol[x].subs(y, item)) for item in y_bifurc]
    param_bifurc = [re(sol[param].subs(y, item)) for item in y_bifurc]
    plt.plot(param_bifurc, x_bifurc, 'rx')
    plt.plot(param_bifurc, y_bifurc, 'g*')

    plt.xlim([0, 10])
    plt.ylim([0, 1])
    plt.xlabel(f'{param}')
    plt.ylabel('x, y')
    plt.legend(loc='upper right')
    plt.show()


def main():
    param_dict = {k_3: 0.002, k_1: 0.01, k1: 0.12, k2: 0.95, k3: 0.0032}
    z = 1 - x - 2 * y
    dx_dt = k1 * z - k_1 * x - k3 * x * z + k_3 * y - k2 * x * (z ** 2)
    dy_dt = k3 * x * z - k_3 * y
    param = k2
    perform_one_param_analysis(dx_dt, dy_dt, param_dict, param)


if __name__ == "__main__":
    main()
