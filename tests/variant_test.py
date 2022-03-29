"""Test the functionality of gate variants."""
#TODO: install the AER and use unitary matrix simulator.
import unittest
import numpy

from qiskit import *
from qiskit.transpiler.passes import Unroller
from qiskit.transpiler import PassManager
from qiskit.compiler import transpile
from qiskit.providers.aer import UnitarySimulator
from qiskit.test import QiskitTestCase
from qiskit.circuit.library.standard_gates.x import CCXGate
from gate_variants.toffoli_variants import CCX_01_12_Gate, CCX_02_01_Gate, CCX_01_02_Gate, CCX_02_01_h_Gate, CCX_Variant_Gate

class VariantTestCase(QiskitTestCase):
    def assertEqualUnitary(self, circuit, expected):
        """ Compares the unitary matrix of gate variants """
        backend = UnitarySimulator(precision='single')
        circuit_job = execute(circuit, backend)
        expected_job = execute(expected, backend)
        circuit_matrix = circuit_job.result().get_unitary(circuit, decimals=3)
        expected_matrix = expected_job.result().get_unitary(expected, decimals=3)
        numpy.testing.assert_array_equal(circuit_matrix, expected_matrix)

class TestToffoliGate(VariantTestCase):
    def CCX_comparison_circuit(self, tag):
        qr = QuantumRegister(3, 'qr')
        circuit = QuantumCircuit(qr)
        circuit.append(CCX_Variant_Gate(variant_tag=tag), [qr[0], qr[1], qr[2]])
        trans_qc = transpile(circuit, optimization_level=3)

        qr = QuantumRegister(3, 'qr')
        expect_circuit = QuantumCircuit(qr)
        expect_circuit.ccx(qr[0],qr[1], qr[2])
        trans_expect = transpile(expect_circuit, optimization_level=3)
        self.assertEqualUnitary(trans_expect, trans_qc)

    def test_CCX_01_02_s_gate(self):
        TestToffoliGate.CCX_comparison_circuit(self, ('01', '02', 's'))
    def test_CCX_01_12_p_gate(self):
        TestToffoliGate.CCX_comparison_circuit(self, ('01', '12', 'p'))
    def test_CCX_02_01_p_Gate(self):
        TestToffoliGate.CCX_comparison_circuit(self, ('02', '01', 'p'))
    def test_CCX_02_01_s_Gate(self):
        TestToffoliGate.CCX_comparison_circuit(self, ('02', '01', 's'))
    # def test_CCX_01_02_s_Gate(self):
    #     self.assertEqualUnitary(CCXGate(),CCX_Variant_Gate(variant_tag=('01','02','s')))
    # def test_CCX_01_12_p_Gate(self):
    #     self.assertEqualUnitary(CCXGate(),CCX_Variant_Gate(variant_tag=('01','12','p')))
    # def test_CCX_02_01_p_Gate(self):
    #     self.assertEqualUnitary(CCXGate(),CCX_Variant_Gate(variant_tag=('02','01','p')))
    # def test_CCX_02_01_s_Gate(self):
    #     self.assertEqualUnitary(CCXGate(),CCX_Variant_Gate(variant_tag=('02','01','s')))
    #     print(CCX_Variant_Gate(variant_tag=('02','01','s')).__array__())
#
#
# qr = QuantumRegister(3, 'qr')
# circuit = QuantumCircuit(qr)
# circuit.append(CCX_02_01_Gate(), [qr[0],qr[1], qr[2]])
# trans_qc = transpile(circuit, optimization_level=3)
# print(trans_qc)
# gate_02_01 = CCX_02_01_Gate()
# print(gate_02_01.__array__())

# qr = QuantumRegister(3, 'qr')
# circuit = QuantumCircuit(qr)
# circuit.append(CCX_01_02_Gate(), [qr[0],qr[1], qr[2]])
# trans_qc = transpile(circuit, optimization_level=3)
# print(trans_qc)
# qr = QuantumRegister(3, 'qr')
# circuit = QuantumCircuit(qr)
# circuit.append(CCX_Variant_Gate(),[qr[0],qr[1], qr[2]])
# trans_qc = transpile(circuit, optimization_level=3)
# print(trans_qc)
#
# qr = QuantumRegister(3, 'qr')
# circuit = QuantumCircuit(qr)
# circuit.append(CCX_Variant_Gate(variant_tag=('02','01','p')), [qr[0], qr[1], qr[2]])
# trans_qc = transpile(circuit, optimization_level=3)
# print(trans_qc)
#
# qr = QuantumRegister(3, 'qr')
# circuit = QuantumCircuit(qr)
# circuit.append(CCX_Variant_Gate(variant_tag=('01','12','p')), [qr[0], qr[1], qr[2]])
# trans_qc = transpile(circuit, optimization_level=3)
# print(trans_qc)

# qr = QuantumRegister(3, 'qr')
# circuit = QuantumCircuit(qr)
# circuit.append(CCX_Variant_Gate(variant_tag=('01','01','h')), [qr[0], qr[1], qr[2]])
# trans_qc = transpile(circuit, optimization_level=3)
# print(trans_qc)

if __name__ == '__main__':
    unittest.main()

