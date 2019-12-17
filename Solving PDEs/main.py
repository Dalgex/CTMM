import numpy as np
from fenics import *
from mshr import Circle, generate_mesh
from sympy import symbols, diff, sqrt, ccode, sin, cos, tan, exp

x, y, t = symbols('x[0], x[1], t')


def calculate_laplacian(u):
    return diff(u, x, x) + diff(u, y, y)


def calculate_gradient(u):
    return [diff(u, x), diff(u, y)]


def calculate_normal_derivative(u):
    factor = sqrt(x ** 2 + y ** 2)
    x_component = calculate_gradient(u)[0] * x
    y_component = calculate_gradient(u)[1] * y
    return (x_component + y_component) / factor


def check_boundary(x, on_check_boundary):
    return on_check_boundary and x[1] < 0


def solve_poisson_equation(u_e, alpha, title_name):
    domain = Circle(Point(0, 0), 1)
    mesh = generate_mesh(domain, 30)
    V = FunctionSpace(mesh, 'P', 2)

    u_d = Expression(ccode(u_e), degree=2)
    bc = DirichletBC(V, u_d, check_boundary)
    u = TrialFunction(V)
    v = TestFunction(V)

    f = -calculate_laplacian(u_e) + alpha * u_e
    f = Expression(ccode(f), degree=2)
    g = calculate_normal_derivative(u_e)
    g = Expression(ccode(g), degree=2)

    a = dot(grad(u), grad(v)) * dx + alpha * u * v * dx
    L = f * v * dx + g * v * ds
    u = Function(V)
    solve(a == L, u, bc)

    u_e = u_d
    error_L2 = errornorm(u_e, u, 'L2')
    vertex_values_u = u.compute_vertex_values(mesh)
    vertex_values_u_e = u_e.compute_vertex_values(mesh)
    error_max = np.max(np.abs(vertex_values_u_e - vertex_values_u))
    print('Max error = %.3g, L2 error = %.3g' % (error_max, error_L2))


def solve_heat_equation(u_e, steps_number, alpha, title_name):
    domain = Circle(Point(0, 0), 1)
    mesh = generate_mesh(domain, 30)
    V = FunctionSpace(mesh, 'P', 2)

    u_d = Expression(ccode(u_e), t=0, degree=2)
    bc = DirichletBC(V, u_d, check_boundary)
    u_n = interpolate(u_d, V)
    u = TrialFunction(V)
    v = TestFunction(V)

    t = symbols('t')
    f = diff(u_e, t) - alpha * calculate_laplacian(u_e)
    f = Expression(ccode(f), t=0, degree=2)
    g = calculate_normal_derivative(u_e)
    g = Expression(ccode(g), t=0, degree=2)

    T = 2.0
    dt = T / steps_number
    a = u * v * dx + dt * dot(grad(u), grad(v)) * dx
    L = (u_n + dt * f) * v * dx + dt * v * g * ds
    u = Function(V)
    t = 0

    for n in range(steps_number):
        t += dt
        u_d.t = t
        g.t = t
        f.t = t
        solve(a == L, u, bc)
        u_n.assign(u)
        u_e = interpolate(u_d, V)
        error_L2 = errornorm(u_e, u, 'L2')
        error_max = np.abs(u_e.vector().get_local() - u.vector().get_local()).max()
        print('t = %.2f: max error = %.3g, L2 error = %.3g' % (t, error_max, error_L2))


def main():
    set_log_active(False)

    alpha = 1
    solve_poisson_equation(1 - x ** 2 + y, alpha, 'func1')
    solve_poisson_equation(tan(x) * y + x * cos(y), alpha, 'func2')
    solve_poisson_equation(x * exp(y) + sin(y ** 2), alpha, 'func3')

    steps_number = 50
    solve_heat_equation(x * t + y ** 2, steps_number, alpha, 'func1')
    solve_heat_equation(cos(x) * sin(t) * tan(y), steps_number, alpha, 'func2')
    solve_heat_equation(exp(x) * t ** 2 - sin(y * t), steps_number, alpha, 'func3')


if __name__ == '__main__':
    main()