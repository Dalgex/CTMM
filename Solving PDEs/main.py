import imageio
import numpy as np
from fenics import *
from mshr import Circle, generate_mesh
from matplotlib import tri, pyplot as plt
from sympy import symbols, diff, sqrt, ccode, sin, cos, exp

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
    image = plot_solutions(u_e, u, mesh)
    imageio.imsave(f'poisson_{title_name}.png', image)


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

    T = 5.0
    dt = T / steps_number
    a = u * v * dx + dt * dot(grad(u), grad(v)) * dx
    L = (u_n + dt * f) * v * dx + dt * v * g * ds
    u = Function(V)
    t = 0
    plots = []
    errors_L2 = []
    errors_max = []

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
        plots.append(plot_solutions(u_e, u, mesh))
        errors_max.append(error_max)
        errors_L2.append(error_L2)

    imageio.imsave(f'heat_{title_name}.png', plots[-1])
    write_video(plots, f'heat_{title_name}')
    time_interval = np.linspace(dt, T, steps_number)
    plt.plot(time_interval, errors_max, label='Max error')
    plt.plot(time_interval, errors_L2, label='L2 error')
    plt.legend()
    plt.savefig(f'errors_{title_name}.png')
    plt.close()


def write_video(images, title_name, fps=10):
    with imageio.get_writer(f'{title_name}.avi', fps=fps) as writer:
        for image in images:
            writer.append_data(image)


def plot_solutions(u_e, u, mesh):
    n = mesh.num_vertices()
    d = mesh.geometry().dim()
    mesh_coordinates = mesh.coordinates().reshape((n, d))
    triangles = np.asarray([cell.entities(0) for cell in cells(mesh)])
    triangulation = tri.Triangulation(mesh_coordinates[:, 0],
                                      mesh_coordinates[:, 1], triangles)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4))
    z_faces = np.asarray([u_e(cell.midpoint()) for cell in cells(mesh)])
    ax1_plot = ax1.tripcolor(triangulation, facecolors=z_faces, edgecolors='k')
    z_faces = np.asarray([u(cell.midpoint()) for cell in cells(mesh)])
    ax2_plot = ax2.tripcolor(triangulation, facecolors=z_faces, edgecolors='k')
    
    ax1.set_title('Real solution')
    ax2.set_title('Approximate solution')
    fig.colorbar(ax1_plot, ax=ax1)
    fig.colorbar(ax2_plot, ax=ax2)
    fig.canvas.draw()
    fig_plot = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
    fig_plot = fig_plot.reshape(fig.canvas.get_width_height()[::-1] + (3,))
    plt.close()
    return fig_plot


def main():
    set_log_active(False)

    alpha = 1
    solve_poisson_equation(1 - x ** 2 + y, alpha, 'func1')
    solve_poisson_equation(sin(x) * y + x * cos(y), alpha, 'func2')
    solve_poisson_equation(sin(y ** 2) - x * exp(y), alpha, 'func3')

    steps_number = 50
    solve_heat_equation(t * (y - x * t), steps_number, alpha, 'func1')
    solve_heat_equation(x ** 2 * t - cos(y * t), steps_number, alpha, 'func2')
    solve_heat_equation(x * cos(t ** 2) + t * sin(y), steps_number, alpha, 'func3')


if __name__ == '__main__':
    main()
