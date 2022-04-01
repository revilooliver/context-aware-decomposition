# -*- coding: utf-8 -*-

"""
This module contains tools for building unitary matrices from parameterized quantum circuits.
"""
from typing import Dict, List
import numpy as np


class UnitaryBuilder:
    def __init__(self, num_qubits: int, mq_instructions: List[int], mq_dict: Dict[int, np.ndarray]):
        """
        Constructor for UnitaryBuilder object.

        :param num_qubits: number of qubits in quantum circuit from which to build unitary
        :param mq_instructions: number of multi-qubit instructions available in quantum computer ISA
        :param mq_dict: dictionary mapping integers to multi-qubit instructions specified as unitary matrices
        """
        self.num_qubits = num_qubits
        self.mq_instructions = mq_instructions
        self.mq_dict = mq_dict

    def u3(self, theta: float, phi: float, lam: float, qubit: int) -> np.ndarray:
        """
        Generates the unitary matrix for a U3 gate given phi/theta/lambda parameters and the
        qubit on which it is supposed to act.

        :param theta: theta value of U3 gate (see Qiskit documentation)
        :param phi: phi value of U3 gate (see Qiskit documentation)
        :param lam: lambda value of U3 gate (see Qiskit documentation)
        :param qubit: qubit on which U3 gate should act
        """
        if qubit + 1 > self.num_qubits:
            raise Exception("Error: invalid qubit")

        gate = 1
        for i in range(qubit):
            gate = np.kron(gate, np.eye(2))

        gate = np.kron(gate, np.array([
            [np.cos(theta / 2), -np.exp(1j * lam) * np.sin(theta / 2)],
            [np.exp(1j * phi) * np.sin(theta / 2), np.exp(1j * (phi + lam)) * np.cos(theta / 2)]]
        ))

        for i in range(self.num_qubits - qubit - 1):
            gate = np.kron(gate, np.eye(2))

        return gate

    def build_unitary(self, params: np.ndarray) -> np.ndarray:
        """
        Build a Numpy unitary matrix from a list of beta parameters.

        :param params: beta vector specifying U3 values from right to left
        and top to down in theta, phi, lambda order
        :returns: a unitary Numpy matrix
        """
        matrix = np.eye(2 ** self.num_qubits, dtype=np.complex128)

        for qubit in range(self.num_qubits):
            matrix = matrix @ self.u3(params[3 * qubit], params[3 * qubit + 1], params[3 * qubit + 2], qubit)

        for layer in range(len(self.mq_instructions)):
            matrix = matrix @ self.mq_dict[self.mq_instructions[layer]]
            for qubit in range(self.num_qubits):
                layer_start = 3 * self.num_qubits * (layer + 1)
                matrix = matrix @ self.u3(params[layer_start + 3 * qubit],
                                          params[layer_start + 3 * qubit + 1],
                                          params[layer_start + 3 * qubit + 2],
                                          qubit
                                          )

        return matrix

