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

class Bridge_Variant_Gate(ControlledGate):


    def __init__(self, label: Optional[str] = None, ctrl_state: Optional[Union[str, int]] = None, variant_tag = ('12', '01')):
        """Create new CCX gate."""
        super().__init__(
            "bridge", 3, [], num_ctrl_qubits=1, label=label, ctrl_state=ctrl_state, base_gate=XGate()
        )
        print("initialized variant_tag:", variant_tag)
        self.variant_tag = variant_tag
        #self._define_variant(variant_tag)

    def _define(self):
        """

        """
        # pylint: disable=cyclic-import
        from qiskit.circuit.quantumcircuit import QuantumCircuit

        q = QuantumRegister(3, "q")
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
            ('12', '01'): [
                (CXGate(), [q[1], q[2]], []),
                (CXGate(), [q[0], q[1]], []),
                (CXGate(), [q[1], q[2]], []),
                (CXGate(), [q[0], q[1]], []),
            ],
            ('01', '12'): [
                (CXGate(), [q[0], q[1]], []),
                (CXGate(), [q[1], q[2]], []),
                (CXGate(), [q[0], q[1]], []),
                (CXGate(), [q[1], q[2]], []),
            ],
          
            }
        return variant_rules[variant_tag]
                                             
                

    def control(
        self,
        num_ctrl_qubits: int = 1,
        label: Optional[str] = None,
        ctrl_state: Optional[Union[str, int]] = None,
    ):
        """Controlled version of this gate.

        Args:
            num_ctrl_qubits (int): number of control qubits.
            label (str or None): An optional label for the gate [Default: None]
            ctrl_state (int or str or None): control state expressed as integer,
                string (e.g. '110'), or None. If None, use all 1s.

        Returns:
            ControlledGate: controlled version of this gate.
        """
        ctrl_state = _ctrl_state_to_int(ctrl_state, num_ctrl_qubits)
        new_ctrl_state = (self.ctrl_state << num_ctrl_qubits) | ctrl_state
        gate = MCXGate(num_ctrl_qubits=num_ctrl_qubits + 2, label=label, ctrl_state=new_ctrl_state)
        gate.base_gate.label = self.label
        return gate

    def __array__(self, dtype=None):
        """Return a numpy.array for the CCX gate."""
        mat = _compute_control_matrix(
            self.base_gate.to_matrix(), self.num_ctrl_qubits, ctrl_state=self.ctrl_state
        )
        if dtype:
            return numpy.asarray(mat, dtype=dtype)
        return mat
    
