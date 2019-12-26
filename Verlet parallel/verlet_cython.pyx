import numpy as np
from copy import deepcopy
cimport numpy as np
DTYPE = np.double
ctypedef np.double_t DTYPE_t


def calculate_verlet_cython(np.ndarray[DTYPE_t, ndim=2] data, double delta_t):
    cdef int N = len(data)
    cdef DTYPE_t[:, :] prev_data = deepcopy(data)
    cdef DTYPE_t[:, :] prev_accs = np.zeros((N, 2), dtype=DTYPE)
    _update_coordinates(data, prev_data, prev_accs, delta_t)
    _update_speed(data, prev_accs, delta_t)
    return data


def _calculate_acceleration(DTYPE_t[:, :] data, int index):
    cdef double G = 6.6743015e-11
    cdef DTYPE_t[:] a = np.zeros((2,), dtype=DTYPE)
    cdef int i, k

    for i in range(len(data)):
        if i != index:
            for k in range(2):
                a[k] += (G * data[i, 5] * (data[i, k] - data[index, k])
                         / _calculate_norm(data, i, index) ** 3)
    return a


def _calculate_norm(DTYPE_t[:, :] data, int i, int j):
    cdef int k
    cdef double temp = 0
    for k in range(2):
        temp += (data[i, k] - data[j, k]) ** 2
    return temp ** 0.5


def _update_coordinates(DTYPE_t[:, :] data, DTYPE_t[:, :] prev_data,
                        DTYPE_t[:, :] prev_accs, double delta_t):
    cdef DTYPE_t[:] temp_acc = np.zeros((2,), dtype=DTYPE)
    cdef int i, k

    for i in range(len(data)):
        temp_acc = _calculate_acceleration(prev_data, i)
        for k in range(2):
            prev_accs[i, k] = temp_acc[k]
            data[i, k] += (prev_data[i, k + 2] * delta_t
                           + 0.5 * prev_accs[i, k] * delta_t ** 2)


def _update_speed(DTYPE_t[:, :] data, DTYPE_t[:, :] prev_accs, double delta_t):
    cdef DTYPE_t[:] cur_acc = np.zeros((2,), dtype=DTYPE)
    cdef int i, k

    for i in range(len(data)):
        cur_acc = _calculate_acceleration(data, i)
        for k in range(2):
            data[i, k + 2] += 0.5 * (prev_accs[i, k] + cur_acc[k]) * delta_t
