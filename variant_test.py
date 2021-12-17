"""Test the functionality of gate variants."""
#TODO: The testcases for unitary matrix equivalence, use unitest
# TODO: It seems that there are multiple versions of 01_02: either the two cnot is at the beginning or at the end
import unittest

from qiskit import QuantumRegister, QuantumCircuit
from qiskit.transpiler.passes import Unroller
from qiskit.transpiler import PassManager
from qiskit.compiler import transpile
from gate_variants.toffoli_variants import CCX_01_12_Gate, CCX_02_01_Gate, CCX_01_02_Gate, CCX_02_01_h_Gate, CCX_Variant_Gate

# qr = QuantumRegister(3, 'qr')
# circuit = QuantumCircuit(qr)
# circuit.append(CCX_01_12_Gate(), [qr[0],qr[1], qr[2]])
# trans_qc = transpile(circuit, optimization_level=3)
# print(trans_qc)
# gate_01_12 = CCX_01_12_Gate()
# print(gate_01_12.__array__())
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
qr = QuantumRegister(3, 'qr')
circuit = QuantumCircuit(qr)
circuit.append(CCX_Variant_Gate(),[qr[0],qr[1], qr[2]])
trans_qc = transpile(circuit, optimization_level=3)
print(trans_qc)

qr = QuantumRegister(3, 'qr')
circuit = QuantumCircuit(qr)
circuit.append(CCX_Variant_Gate(variant_tag=('02','01','p')), [qr[0], qr[1], qr[2]])
trans_qc = transpile(circuit, optimization_level=3)
print(trans_qc)

qr = QuantumRegister(3, 'qr')
circuit = QuantumCircuit(qr)
circuit.append(CCX_Variant_Gate(variant_tag=('01','12','p')), [qr[0], qr[1], qr[2]])
trans_qc = transpile(circuit, optimization_level=3)
print(trans_qc)

# qr = QuantumRegister(3, 'qr')
# circuit = QuantumCircuit(qr)
# circuit.append(CCX_Variant_Gate(variant_tag=('01','01','h')), [qr[0], qr[1], qr[2]])
# trans_qc = transpile(circuit, optimization_level=3)
# print(trans_qc)

