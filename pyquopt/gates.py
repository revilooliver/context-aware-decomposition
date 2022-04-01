# -*- coding: utf-8 -*-

"""
This module contains unitary gate definitions.
It should be modified for different quantum computer
architectures.
"""
from math import sqrt
import numpy as np


class TwoGates:
    """
    Class containing various 2x2 unitary matrices
    that implement IBM Q native gates (or proposed native gates)
    or produce common entangled states (e.g., the GHZ state).
    """
    CR01 = np.array([
        [0, 0, -0.5+0.5j, -0.5-0.5j],
        [0, 0, -0.5-0.5j, -0.5+0.5j],
        [-0.5+0.5j, 0.5+0.5j, 0, 0],
        [0.5+0.5j, -0.5+0.5j, 0, 0]
    ], dtype=np.complex128)
    
    CX01 = np.array([
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 0, 1],
        [0, 0, 1, 0]
    ], dtype=np.complex128)
    
    CX10 = np.array([
        [1, 0, 0, 0],
        [0, 0, 0, 1],
        [0, 0, 1, 0],
        [0, 1, 0, 0]
    ], dtype=np.complex128)

    GHZ = np.array([
        [1/sqrt(2), 0, 1/sqrt(2), 0],
        [0, 1/sqrt(2), 0, 1/sqrt(2)],
        [0, 1/sqrt(2), 0, -1/sqrt(2)],
        [1/sqrt(2), 0, -1/sqrt(2), 0]
    ], dtype=np.complex128)


class ThreeGates:
    """
    Class containing various 3x3 unitary matrices
    that implement IBM Q native gates (or proposed native gates)
    or produce common entangled states (e.g., the GHZ state).
    """
    CR01 = np.array([
        [0, 0, 0, 0, 0.5-0.5j, 0, 0.5+0.5j, 0],
        [0, 0, 0, 0, 0, 0.5-0.5j, 0, 0.5+0.5j],
        [0, 0, 0, 0, 0.5+0.5j, 0, 0.5-0.5j, 0],
        [0, 0, 0, 0, 0, 0.5+0.5j, 0, 0.5-0.5j],
        [0.5-0.5j, 0, -0.5-0.5j, 0, 0, 0, 0, 0],
        [0, 0.5-0.5j, 0, -0.5-0.5j, 0, 0, 0, 0],
        [-0.5-0.5j, 0, 0.5-0.5j, 0, 0, 0, 0, 0],
        [0, -0.5-0.5j, 0, 0.5-0.5j, 0, 0, 0, 0]
    ], dtype=np.complex128)

    CR02 = np.array([
        [0, 0, 0, 0, 0.5-0.5j, 0.5+0.5j, 0, 0],
        [0, 0, 0, 0, 0.5+0.5j, 0.5-0.5j, 0, 0],
        [0, 0, 0, 0, 0, 0, 0.5-0.5j, 0.5+0.5j],
        [0, 0, 0, 0, 0, 0, 0.5+0.5j, 0.5-0.5j],
        [0.5-0.5j, -0.5-0.5j, 0, 0, 0, 0, 0, 0],
        [-0.5-0.5j, 0.5-0.5j, 0, 0, 0, 0, 0, 0],
        [0, 0, 0.5-0.5j, -0.5-0.5j, 0, 0, 0, 0],
        [0, 0, -0.5-0.5j, 0.5-0.5j, 0, 0, 0, 0]
    ], dtype=np.complex128)

    MCR = np.array([
        [0, 0, 0, 0, 0.5, 0.5j, 0.5j, -0.5],
        [0, 0, 0, 0, 0.5j, 0.5, -0.5, 0.5j],
        [0, 0, 0, 0, 0.5j, -0.5, 0.5, 0.5j],
        [0, 0, 0, 0, -0.5, 0.5j, 0.5j, 0.5],
        [0.5, -0.5j, -0.5j, -0.5, 0, 0, 0, 0],
        [-0.5j, 0.5, -0.5, -0.5j, 0, 0, 0, 0],
        [-0.5j, -0.5, 0.5, -0.5j, 0, 0, 0, 0],
        [-0.5, -0.5j, -0.5j, 0.5, 0, 0, 0, 0]
    ], dtype=np.complex128)

    CV01 = np.array([
        [1, 0, 0, 0, 0, 0, 0, 0],
        [0, 1, 0, 0, 0, 0, 0, 0],
        [0, 0, 1, 0, 0, 0, 0, 0],
        [0, 0, 0, 1, 0, 0, 0, 0],
        [0, 0, 0, 0, 0.5+0.5j, 0, 0.5-0.5j, 0],
        [0, 0, 0, 0, 0, 0.5+0.5j, 0, 0.5-0.5j],
        [0, 0, 0, 0, 0.5-0.5j, 0, 0.5+0.5j, 0],
        [0, 0, 0, 0, 0, 0.5-0.5j, 0, 0.5+0.5j]
    ], dtype=np.complex128)

    CV02 = np.array([
        [1, 0, 0, 0, 0, 0, 0, 0],
        [0, 1, 0, 0, 0, 0, 0, 0],
        [0, 0, 1, 0, 0, 0, 0, 0],
        [0, 0, 0, 1, 0, 0, 0, 0],
        [0, 0, 0, 0, 0.5+0.5j, 0.5-0.5j, 0, 0],
        [0, 0, 0, 0, 0.5-0.5j, 0.5+0.5j, 0, 0],
        [0, 0, 0, 0, 0, 0, 0.5+0.5j, 0.5-0.5j],
        [0, 0, 0, 0, 0, 0, 0.5-0.5j, 0.5+0.5j]
    ], dtype=np.complex128)

    TOFFOLI = np.array([
        [1, 0, 0, 0, 0, 0, 0, 0],
        [0, 1, 0, 0, 0, 0, 0, 0],
        [0, 0, 1, 0, 0, 0, 0, 0],
        [0, 0, 0, 1, 0, 0, 0, 0],
        [0, 0, 0, 0, 1, 0, 0, 0],
        [0, 0, 0, 0, 0, 1, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 1],
        [0, 0, 0, 0, 0, 0, 1, 0]
    ], dtype=np.complex128)  # Toffoli gate unitary matrix

    GHZ = -(1 / sqrt(2)) * np.array([
        [1, 0, 0, 0, 1, 0, 0, 0],
        [0, 1, 0, 0, 0, 1, 0, 0],
        [0, 0, 1, 0, 0, 0, 1, 0],
        [0, 0, 0, 1, 0, 0, 0, 1],
        [0, 0, 0, 1, 0, 0, 0, -1],
        [0, 0, 1, 0, 0, 0, -1, 0],
        [0, 1, 0, 0, 0, -1, 0, 0],
        [1, 0, 0, 0, -1, 0, 0, 0]
    ], dtype=np.complex128)  # GHZ prep circuit unitary matrix (to global phase)

