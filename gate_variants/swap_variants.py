#define different Toffoli variants. There should be 9 combinations. The canonical ccx is CCX_12_01
import numpy
from typing import Optional, Union
from qiskit.circuit.quantumregister import QuantumRegister
from qiskit.circuit.gate import Gate
from qiskit.circuit.controlledgate import ControlledGate
from qiskit.circuit.library.standard_gates.x import XGate, CXGate
from qiskit.circuit.library.standard_gates.h import HGate
from qiskit.circuit.library.standard_gates.t import TGate, TdgGate

from qiskit.circuit._utils import _compute_control_matrix, _ctrl_state_to_int



class SWAP_Variant_Gate(Gate):


    def __init__(self, label=None, variant_tag = ('01')):
        """Create new SWAP gate."""
        super().__init__("swap_variant", 2, [], label=label)
        self.variant_tag = variant_tag

    def _define(self):
        """

        """
        # pylint: disable=cyclic-import
        from qiskit.circuit.quantumcircuit import QuantumCircuit

        q = QuantumRegister(2, "q")
        qc = QuantumCircuit(q, name=self.name)
        variant_tag = self.variant_tag

        try:
            rules = self.get_rules(q, variant_tag)
        except:
            raise AttributeError(f"Variant_tag({variant_tag})not defined")

        for instr, qargs, cargs in rules:
            qc._append(instr, qargs, cargs)

        self.definition = qc


    @staticmethod
    def get_rules(q, variant_tag):
        variant_rules = {
            ('01'): [
                (CXGate(), [q[0], q[1]], []),
                (CXGate(), [q[1], q[0]], []),
                (CXGate(), [q[0], q[1]], []),
            ],
            ('10'): [
                (CXGate(), [q[1], q[0]], []),
                (CXGate(), [q[0], q[1]], []),
                (CXGate(), [q[1], q[0]], []),
            ],
          
            }
        return variant_rules[variant_tag]
                                             
                

    def control(self, num_ctrl_qubits=1, label=None, ctrl_state=None):
        """Return a (multi-)controlled-SWAP gate.

        One control returns a CSWAP (Fredkin) gate.

        Args:
            num_ctrl_qubits (int): number of control qubits.
            label (str or None): An optional label for the gate [Default: None]
            ctrl_state (int or str or None): control state expressed as integer,
                string (e.g. '110'), or None. If None, use all 1s.

        Returns:
            ControlledGate: controlled version of this gate.
        """
        if num_ctrl_qubits == 1:
            gate = CSwapGate(label=label, ctrl_state=ctrl_state)
            gate.base_gate.label = self.label
            return gate
        return super().control(num_ctrl_qubits=num_ctrl_qubits, label=label, ctrl_state=ctrl_state)

    def inverse(self):
        """Return inverse Swap gate (itself)."""
        return SwapGate()  # self-inverse

    def __array__(self, dtype=None):
        """Return a numpy.array for the SWAP gate."""
        return numpy.array([[1, 0, 0, 0], [0, 0, 1, 0], [0, 1, 0, 0], [0, 0, 0, 1]], dtype=dtype)
    
