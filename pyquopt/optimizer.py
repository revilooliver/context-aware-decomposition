# -*- coding: utf-8 -*-

"""
This module contains tools for discovering quantum circuit implementations of quantum gates/circuits
using numerical optimization techniques.
"""
from typing import Dict, List, Tuple
import multiprocessing
import numpy as np
from scipy.optimize import minimize, least_squares
from .unitary import UnitaryBuilder


class Optimizer:
    def __init__(self, num_qubits: int, mq_instructions: List[int], mq_dict: Dict[int, np.ndarray], target: np.ndarray,
            alpha: float, gamma: float, non_fixed_params: np.ndarray, fixed_params_vals: np.ndarray):
        """
        Constructor for Optimizer class.

        :param num_qubits: number of qubits used by target operation
        :param mq_instructions: a list of multi-qubit instructions defining circuit structure to optimize over
        :param mq_dict: dictionary mapping integers [0, n) to 2^num_qubits x 2^num_qubits complex unitaries
        :param target: 2^num_qubits x 2^num_qubits target complex unitary matrix
        """
        self.num_qubits = num_qubits
        self.mq_instructions = mq_instructions
        self.mq_dict = mq_dict
        self.target = target
        self.unitary_builder = UnitaryBuilder(num_qubits, mq_instructions, mq_dict)
        self.alpha = alpha
        self.gamma = gamma
        self.non_fixed_params = non_fixed_params
        self.fixed_params_vals = fixed_params_vals

    def bfgs_objective_function(self, params: np.ndarray) -> float:
        """
        Calculates a cost measuring how close the parameter-calculated unitary matches the target unitary,
        how large the parameters are, and how "ideal" the angle measures are (i.e., are common angles such as pi/6, pi/4, etc.).

        :param params: Numpy array of parameters completing quantum circuit specification in unitary_builder
        :return: a floating point number
        """
        actual_params = np.multiply(self.non_fixed_params, params) + self.fixed_params_vals
        # actual_params = params

        complex_residuals = np.matrix.flatten(self.unitary_builder.build_unitary(actual_params) - self.target)
        unitary_cost = np.vdot(complex_residuals, complex_residuals).real
        nice_angle_residuals = np.sin(6 * actual_params) * np.sin(4 * actual_params) * np.sin(2 * actual_params) * np.sin(2 * actual_params)
        nice_angle_cost = self.alpha * np.dot(nice_angle_residuals, nice_angle_residuals)
        large_angle_cost = self.gamma * np.dot(params, params)

        return unitary_cost + nice_angle_cost + large_angle_cost

    def least_square_residuals(self, params: np.ndarray) -> np.ndarray:
        """
        Calculates a list of residuals interpreted by SciPy LM optimizer

        :param params: Numpy array of parameters completing quantum circuit specification in unitary_builder
        :return: an array of least-squares residuals (unsquared)
        """
        actual_params = np.multiply(self.non_fixed_params, params) + self.fixed_params_vals
        # print(actual_params)

        complex_residuals = np.matrix.flatten(self.unitary_builder.build_unitary(actual_params) - self.target)
        real_residuals = np.hstack((complex_residuals.real, complex_residuals.imag))
        angle_conform_residuals = self.alpha * (np.sin(6 * params)
                                          * np.sin(4 * params) * np.sin(2 * params)
                                          * np.sin(2 * params))
        real_and_angle_conform_residuals = np.hstack((real_residuals, angle_conform_residuals))
        large_angle_residuals = self.gamma * params ** 2
        all_residuals = np.hstack((real_and_angle_conform_residuals, large_angle_residuals))

        # return real_and_angle_conform_residuals
        return all_residuals

    def find_parameters_bfgs(self, num_guesses: int) -> Tuple[np.ndarray, float]:
        """
        Run BFGS optimization routing num_guesses times on the quantum circuit structure
        specified in construction of this object.

        :param num_guesses: integer for number of random points from which to run BFGS
        :return: Numpy array of parameters that minimize BFGS objective function
        """
        min_fun_val = np.inf
        min_params = None

        for i in range(num_guesses):
            x0_all = np.random.rand((len(self.mq_instructions) + 1) * 3 * self.num_qubits) * 2 * np.pi
            x0 = np.multiply(x0_all, self.non_fixed_params) + self.fixed_params_vals
            opt_results = minimize(self.objective_function_bfgs, x0=x0, method='BFGS', options={'disp': False})
            # print(f"Test {i}: {opt_results.fun}")
            if opt_results.fun < min_fun_val:
                min_fun_val = opt_results.fun
                min_params = np.multiply(opt_results.x, self.non_fixed_params) + self.fixed_params_vals

        return min_params, min_fun_val


    def find_parameters_least_squares(self, num_guesses: int) -> Tuple[np.ndarray, float]:
        """
        Sequentially run trust region-based optimization num_guesses times.

        :param num_guesses: integer
        :return: Numpy array of parameters that minimize least-squares objective function
        """
        min_fun_val = np.inf
        min_params = None

        if num_guesses == 0:
            return min_params, min_fun_val

        for _ in range(num_guesses):
            x0_all = np.random.rand((len(self.mq_instructions) + 1) * 3 * self.num_qubits) * 2 * np.pi
            x0 = np.multiply(x0_all, self.non_fixed_params) + self.fixed_params_vals
            opt_results = least_squares(self.least_square_residuals, x0=x0, method='trf', verbose=0, ftol=1e-100)
            if opt_results.cost < min_fun_val:
                min_fun_val = opt_results.cost
                min_params = np.multiply(opt_results.x, self.non_fixed_params) + self.fixed_params_vals

        return min_params, min_fun_val

    def find_parameters_least_squares_par(self, num_guesses: int, procs: int) -> Tuple[np.ndarray, float]:
        """
        Run trust region-based optimization num_guesses times using parallel processes.

        :param num_guesses: integer
        :param procs: integer number of processes to spawn (procs + 1 may also be spawned)
        :return: Numpy array of parameters that minimize least-squares objective function
        """
        min_fun_val = np.inf
        min_params = None

        with multiprocessing.Pool(procs + 1) as proc_pool:
            task_guesses = [int(num_guesses / procs)] * procs + [num_guesses % procs]
            results = [proc_pool.apply_async(self.find_parameters_least_squares, (guesses, )) for guesses in task_guesses]

            for result in results:
                result_tuple = result.get()
                if result_tuple[1] < min_fun_val:
                    min_fun_val = result_tuple[1]
                    min_params = result_tuple[0]  # find minimum parameters across all processes

        return min_params, min_fun_val

