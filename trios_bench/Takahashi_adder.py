import numpy as np
import qiskit


def TakahashiAdder(qc, A, B, register_size):

        for i in range(1, register_size):
            qc.cx(A[i], B[i])

        for i in reversed(range(1, register_size-1)):
            qc.cx(A[i], A[i+1])

        for i in range(register_size-1):
            qc.ccx(A[i], B[i], A[i+1])

        for i in reversed(range(1, register_size)):
            qc.cx(A[i], B[i])
            qc.ccx(A[i-1], B[i-1], A[i])

        for i in range(1, register_size-1):
            qc.cx(A[i], A[i+1])

        for i in range(register_size):
            qc.cx(A[i], B[i])

                 
def generate_takahashi_adder(n):
    '''
        n: total size of circuit (each register is n / 2 sized)
    '''
    if n % 2 != 0:
        raise ValueError('Odd number of qubits')
    c = qiskit.circuit.QuantumCircuit(n)
    qs = list(range(n))
    a = qs[:int(n / 2)]
    b = qs[int(n / 2):]
    TakahashiAdder(c, a, b, n // 2)
    return c
