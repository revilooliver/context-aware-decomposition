#define different Toffoli variants. There should be 9 combinations. The canonical ccx is CCX_12_01
from typing import Optional, Union
from qiskit.circuit.quantumregister import QuantumRegister
from qiskit.circuit.gate import Gate
from qiskit.circuit.controlledgate import ControlledGate
from qiskit.circuit.library.standard_gates.x import XGate, CXGate
from qiskit.circuit.library.standard_gates.rx import RXGate
from qiskit.circuit.library.standard_gates.ry import RYGate
from qiskit.circuit.library.standard_gates.rz import RZGate
from qiskit.circuit.library.standard_gates.h import HGate
from qiskit.circuit.library.standard_gates.t import TGate, TdgGate

import numpy as np

from qiskit.circuit._utils import _compute_control_matrix, _ctrl_state_to_int
import qiskit_superstaq


class CX_Variant_Gate(ControlledGate):
    r"""Controlled-X gate.

    **Circuit symbol:**

    .. parsed-literal::

        q_0: ──■──
             ┌─┴─┐
        q_1: ┤ X ├
             └───┘

    **Matrix representation:**

    .. math::

        CX\ q_0, q_1 =
            I \otimes |0\rangle\langle0| + X \otimes |1\rangle\langle1| =
            \begin{pmatrix}
                1 & 0 & 0 & 0 \\
                0 & 0 & 0 & 1 \\
                0 & 0 & 1 & 0 \\
                0 & 1 & 0 & 0
            \end{pmatrix}

    .. note::

        In Qiskit's convention, higher qubit indices are more significant
        (little endian convention). In many textbooks, controlled gates are
        presented with the assumption of more significant qubits as control,
        which in our case would be q_1. Thus a textbook matrix for this
        gate will be:

        .. parsed-literal::
                 ┌───┐
            q_0: ┤ X ├
                 └─┬─┘
            q_1: ──■──

        .. math::

            CX\ q_1, q_0 =
                |0 \rangle\langle 0| \otimes I + |1 \rangle\langle 1| \otimes X =
                \begin{pmatrix}
                    1 & 0 & 0 & 0 \\
                    0 & 1 & 0 & 0 \\
                    0 & 0 & 0 & 1 \\
                    0 & 0 & 1 & 0
                \end{pmatrix}


    In the computational basis, this gate flips the target qubit
    if the control qubit is in the :math:`|1\rangle` state.
    In this sense it is similar to a classical XOR gate.

    .. math::
        `|a, b\rangle \rightarrow |a, a \oplus b\rangle`
    """

    def __init__(self, label=None, ctrl_state=None, variant_tag = ('00', '11', 'd')):
        """Create new CX variant gate."""
        super().__init__(
            "cx_variant", 2, [], num_ctrl_qubits=1, label=label, ctrl_state=ctrl_state, base_gate=XGate()
        )
        print(variant_tag)
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


    def get_rules(self, q, variant_tag):
        variant_rules = {
            ('00', '11', 'd'): [
                (qiskit_superstaq.AceCR("+-"), [q[0], q[1]], []),
                (RYGate(np.pi), [q[0]], []),
                (RXGate(-np.pi/2), [q[1]], []),
                (RZGate(-np.pi/2), [q[0]], []),
            ],
            ('11', '00', 'd'): [
                (RZGate(np.pi/2), [q[0]], []),
                (RYGate(np.pi), [q[0]], []),
                (RXGate(np.pi/2), [q[1]], []),
                (qiskit_superstaq.AceCR("+-"), [q[0], q[1]], []),
            ],
            ('01', '10', 'd'): [
                (RZGate(np.pi/2), [q[0]], []),
                (RXGate(np.pi/2), [q[1]], []),
                (qiskit_superstaq.AceCR("-+"), [q[0], q[1]], []),
                (RXGate(np.pi), [q[0]], []),
            ],
            ('10', '01', 'd'): [
                (RXGate(np.pi/2), [q[0]], []),
                (qiskit_superstaq.AceCR("-+"), [q[0], q[1]], []),
                (RXGate(-np.pi/2), [q[1]], []),
                (RZGate(-np.pi/2), [q[0]], []),
            ],
          
            }
        return variant_rules[variant_tag]

    def control(self, num_ctrl_qubits=1, label=None, ctrl_state=None):
        """Return a controlled-X gate with more control lines.

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
        gate = MCXGate(num_ctrl_qubits=num_ctrl_qubits + 1, label=label, ctrl_state=new_ctrl_state)
        gate.base_gate.label = self.label
        return gate

    def inverse(self):
        """Return inverted CX gate (itself)."""
        return CXGate(ctrl_state=self.ctrl_state)  # self-inverse

    def __array__(self, dtype=None):
        """Return a numpy.array for the CX gate."""
        if self.ctrl_state:
            return numpy.array(
                [[1, 0, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0], [0, 1, 0, 0]], dtype=dtype
            )
        else:
            return numpy.array(
                [[0, 0, 1, 0], [0, 1, 0, 0], [1, 0, 0, 0], [0, 0, 0, 1]], dtype=dtype
            )
    