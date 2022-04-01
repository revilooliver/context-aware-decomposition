# -*- coding: utf-8 -*-

"""
Module with various useful utilities related to numerical discovery
of unitary gate quantum circuit implementations.
"""
import numpy as np


def get_unitary_infidelity(matrix1: np.ndarray, matrix2: np.ndarray, dim: int):
    """
    Calculates notion of infidelity between a target unitary matrix and another unitary matrix.

    :param matrix1: target matrix
    :param matrix2: matrix to compare with target
    :param dim: dimension of Hilbert space on which matrix1 and matrix2 operate
    :return: a float between 0 and 1 (inclusive)
    """

    return 1 - np.abs(np.trace(np.asmatrix(matrix1).getH() @ np.asmatrix(matrix2)) / dim) ** 2


def round_params(params: np.ndarray) -> np.ndarray:
    """
    Rounds parameters in radians to parameters in degrees in the range [0, 360) which
    are multiples of five.

    :param params: a Numpy array of parameters in radians
    :return: a Numpy array of rounded parameters in degrees
    """

    deg_params = params * 180 / np.pi  # convert to degrees 
    int_deg_params = 5 * np.rint(deg_params / 5)  # round to nearest 5-degree increments
    mod_int_deg_params = np.mod(int_deg_params, 360)  # clip to [0, 360) domain

    return mod_int_deg_params
