#define different Toffoli variants. There should be 9 combinations. The canonical ccx is CCX_12_01
from typing import Optional, Union
from qiskit.circuit.quantumregister import QuantumRegister
from qiskit.circuit.gate import Gate
from qiskit.circuit.controlledgate import ControlledGate
from qiskit.circuit.library.standard_gates.x import XGate, CXGate
from qiskit.circuit.library.standard_gates.h import HGate
from qiskit.circuit.library.standard_gates.t import TGate, TdgGate

from qiskit.circuit._utils import _compute_control_matrix, _ctrl_state_to_int

class CCX_Variant_Gate(ControlledGate):
    r"""This equals to the inverse of CCX gate, also known as Toffoli gate.

    **Circuit symbol:**

    .. parsed-literal::


    **Matrix representation:**

    .. math::

        CCX q_0, q_1, q_2 =
            I \otimes I \otimes |0 \rangle \langle 0| + CX \otimes |1 \rangle \langle 1| =
           \begin{pmatrix}
                1 & 0 & 0 & 0 & 0 & 0 & 0 & 0\\
                0 & 1 & 0 & 0 & 0 & 0 & 0 & 0\\
                0 & 0 & 1 & 0 & 0 & 0 & 0 & 0\\
                0 & 0 & 0 & 0 & 0 & 0 & 0 & 1\\
                0 & 0 & 0 & 0 & 1 & 0 & 0 & 0\\
                0 & 0 & 0 & 0 & 0 & 1 & 0 & 0\\
                0 & 0 & 0 & 0 & 0 & 0 & 1 & 0\\
                0 & 0 & 0 & 1 & 0 & 0 & 0 & 0
            \end{pmatrix}

    .. note::

        In Qiskit's convention, higher qubit indices are more significant
        (little endian convention). In many textbooks, controlled gates are
        presented with the assumption of more significant qubits as control,
        which in our case would be q_2 and q_1. Thus a textbook matrix for this
        gate will be:

        .. parsed-literal::
                 ┌───┐
            q_0: ┤ X ├
                 └─┬─┘
            q_1: ──■──
                   │
            q_2: ──■──

        .. math::

            CCX\ q_2, q_1, q_0 =
                |0 \rangle \langle 0| \otimes I \otimes I + |1 \rangle \langle 1| \otimes CX =
                \begin{pmatrix}
                    1 & 0 & 0 & 0 & 0 & 0 & 0 & 0\\
                    0 & 1 & 0 & 0 & 0 & 0 & 0 & 0\\
                    0 & 0 & 1 & 0 & 0 & 0 & 0 & 0\\
                    0 & 0 & 0 & 1 & 0 & 0 & 0 & 0\\
                    0 & 0 & 0 & 0 & 1 & 0 & 0 & 0\\
                    0 & 0 & 0 & 0 & 0 & 1 & 0 & 0\\
                    0 & 0 & 0 & 0 & 0 & 0 & 0 & 1\\
                    0 & 0 & 0 & 0 & 0 & 0 & 1 & 0
                \end{pmatrix}

    """

    def __init__(self, label: Optional[str] = None, ctrl_state: Optional[Union[str, int]] = None, variant_tag = ['01', '02', 'p']):
        """Create new CCX gate."""
        super().__init__(
            "ccx_variant", 3, [], num_ctrl_qubits=2, label=label, ctrl_state=ctrl_state, base_gate=XGate()
        )
        print(variant_tag)
        self.variant_tag = variant_tag
        #self._define_variant(variant_tag)

    def _define(self):
        """
        gate ccx a,b,c
        {
        h c; cx b,c; tdg c; cx a,c;
        t c; cx b,c; tdg c; cx a,c;
        t b; t c; h c; cx a,b;
        t a; tdg b; cx a,b;}
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

#     def _define_variant(self, variant_tag):
#         """
#         """
#         # pylint: disable=cyclic-import
#         from qiskit.circuit.quantumcircuit import QuantumCircuit

#         q = QuantumRegister(3, "q")
#         qc = QuantumCircuit(q, name=self.name)
#         if variant_tag == ('12', '01', 's'):
#             return None
#         try:
#             rules = self.get_rules(q, variant_tag)
#         except:
#             raise AttributeError(f"Variant_tag({variant_tag})not defined")

#         for instr, qargs, cargs in rules:
#             qc._append(instr, qargs, cargs)

#         self.definition = qc
    def get_rules(self, q, variant_tag):
        #The Canonical CCX decomposition is ('12', '01', 's').
        variant_rules = {
            ('01', '01', 'f', 's'): [
                (HGate(), [q[2]], []),
                (TGate(), [q[1]], []),
                (TGate(), [q[0]], []),
                (TGate(), [q[2]], []),
                (CXGate(), [q[0], q[1]], []),
                (CXGate(), [q[2], q[0]], []),
                (CXGate(), [q[1], q[2]], []),
                (TdgGate(), [q[0]], []),
                (CXGate(), [q[1], q[0]], []),
                (TdgGate(), [q[1]], []),
                (TdgGate(), [q[0]], []),
                (TGate(), [q[2]], []),
                (CXGate(), [q[2], q[0]], []),
                (CXGate(), [q[1], q[2]], []),
                (CXGate(), [q[0], q[1]], []),
                (HGate(), [q[2]], []),
            ],
            ('10', '10', 'f', 's'): [
                (HGate(), [q[2]], []),
                (TGate(), [q[0]], []),
                (TGate(), [q[1]], []),
                (TGate(), [q[2]], []),
                (CXGate(), [q[1], q[0]], []),
                (CXGate(), [q[2], q[1]], []),
                (CXGate(), [q[0], q[2]], []),
                (TdgGate(), [q[1]], []),
                (CXGate(), [q[0], q[1]], []),
                (TdgGate(), [q[0]], []),
                (TdgGate(), [q[1]], []),
                (TGate(), [q[2]], []),
                (CXGate(), [q[2], q[1]], []),
                (CXGate(), [q[0], q[2]], []),
                (CXGate(), [q[1], q[0]], []),
                (HGate(), [q[2]], []),
            ],
            ('10', '10', 'f', 'p'): [
                (HGate(), [q[2]], []),
                (CXGate(), [q[1], q[0]], []),
                (CXGate(), [q[0], q[2]], []),
                (CXGate(), [q[2], q[1]], []),
                (TdgGate(), [q[2]], []),
                (TGate(), [q[1]], []),
                (TGate(), [q[0]], []),
                (CXGate(), [q[0], q[1]], []),
                (TGate(), [q[1]], []),
                (CXGate(), [q[0], q[2]], []),
                (CXGate(), [q[2], q[1]], []),
                (CXGate(), [q[1], q[0]], []),
                (TdgGate(), [q[0]], []),
                (TdgGate(), [q[1]], []),
                (TdgGate(), [q[2]], []),
                (HGate(), [q[2]], []),
            ],
            ('01', '01', 'f', 'p'): [
                (HGate(), [q[2]], []),
                (CXGate(), [q[0], q[1]], []),
                (CXGate(), [q[1], q[2]], []),
                (CXGate(), [q[2], q[0]], []),
                (TdgGate(), [q[2]], []),
                (TGate(), [q[0]], []),
                (TGate(), [q[1]], []),
                (CXGate(), [q[1], q[0]], []),
                (TGate(), [q[0]], []),
                (CXGate(), [q[1], q[2]], []),
                (CXGate(), [q[2], q[0]], []),
                (CXGate(), [q[0], q[1]], []),
                (TdgGate(), [q[1]], []),
                (TdgGate(), [q[0]], []),
                (TdgGate(), [q[2]], []),
                (HGate(), [q[2]], []),
            ],
            ('10', '02', 'f', 'p'): [
                (CXGate(), [q[1], q[0]], []),
                (TdgGate(), [q[1]], []),
                (TGate(), [q[0]], []),
                (CXGate(), [q[1], q[0]], []),
                (TdgGate(), [q[0]], []),
                (HGate(), [q[2]], []),
                (TdgGate(), [q[2]], []),
                (CXGate(), [q[1], q[2]], []),
                (TGate(), [q[2]], []),
                (CXGate(), [q[0], q[2]], []),
                (TdgGate(), [q[2]], []),
                (CXGate(), [q[1], q[2]], []),
                (TGate(), [q[2]], []),
                (CXGate(), [q[0], q[2]], []),
                (HGate(), [q[2]], []),
            ],
            ('01', '20', 'f', 's'): [
                (HGate(), [q[2]], []),
                (CXGate(), [q[0], q[1]], []),
                (TdgGate(), [q[1]], []),
                (CXGate(), [q[2], q[1]], []),
                (TGate(), [q[1]], []),
                (CXGate(), [q[0], q[1]], []),
                (TdgGate(), [q[1]], []),
                (CXGate(), [q[2], q[1]], []),
                (TGate(), [q[0]], []),
                (TGate(), [q[1]], []),
                (CXGate(), [q[2], q[0]], []),
                (TGate(), [q[2]], []),
                (TdgGate(), [q[0]], []),
                (CXGate(), [q[2], q[0]], []),
                (HGate(), [q[2]], []),
            ],
            ('01', '12', 'f', 'p'): [
                (CXGate(), [q[0], q[1]], []),
                (TdgGate(), [q[0]], []),
                (TGate(), [q[1]], []),
                (CXGate(), [q[0], q[1]], []),
                (TdgGate(), [q[1]], []),
                (HGate(), [q[2]], []),
                (TdgGate(), [q[2]], []),
                (CXGate(), [q[0], q[2]], []),
                (TGate(), [q[2]], []),
                (CXGate(), [q[1], q[2]], []),
                (TdgGate(), [q[2]], []),
                (CXGate(), [q[0], q[2]], []),
                (TGate(), [q[2]], []),
                (CXGate(), [q[1], q[2]], []),
                (HGate(), [q[2]], []),
            ],
            ('20', '01', 'f', 'p'): [
                (HGate(), [q[2]], []),
                (CXGate(), [q[2], q[0]], []),
                (TdgGate(), [q[2]], []),
                (TGate(), [q[0]], []),
                (CXGate(), [q[2], q[0]], []),
                (TdgGate(), [q[0]], []),
                (TdgGate(), [q[1]], []),
                (CXGate(), [q[2], q[1]], []),
                (TGate(), [q[1]], []),
                (CXGate(), [q[0], q[1]], []),
                (TdgGate(), [q[1]], []),
                (CXGate(), [q[2], q[1]], []),
                (TGate(), [q[1]], []),
                (CXGate(), [q[0], q[1]], []),
                (HGate(), [q[2]], []),
            ],
            ('02', '10', 'f', 's'): [
                (HGate(), [q[2]], []),
                (CXGate(), [q[0], q[2]], []),
                (TdgGate(), [q[2]], []),
                (CXGate(), [q[1], q[2]], []),
                (TGate(), [q[2]], []),
                (CXGate(), [q[0], q[2]], []),
                (TdgGate(), [q[2]], []),
                (CXGate(), [q[1], q[2]], []),
                (TGate(), [q[0]], []),
                (TGate(), [q[2]], []),
                (HGate(), [q[2]], []),
                (CXGate(), [q[1], q[0]], []),
                (TGate(), [q[1]], []),
                (TdgGate(), [q[0]], []),
                (CXGate(), [q[1], q[0]], []),
            ],
            ('12', '01', 'f', 's'): [
                (HGate(), [q[2]], []),
                (CXGate(), [q[1], q[2]], []),
                (TdgGate(), [q[2]], []),
                (CXGate(), [q[0], q[2]], []),
                (TGate(), [q[2]], []),
                (CXGate(), [q[1], q[2]], []),
                (TdgGate(), [q[2]], []),
                (CXGate(), [q[0], q[2]], []),
                (TGate(), [q[1]], []),
                (TGate(), [q[2]], []),
                (HGate(), [q[2]], []),
                (CXGate(), [q[0], q[1]], []),
                (TGate(), [q[0]], []),
                (TdgGate(), [q[1]], []),
                (CXGate(), [q[0], q[1]], []),
            ],
            ('01', '12', 'l', 'p'): [
                (HGate(), [q[2]], []),
                (TGate(), [q[0]], []),
                (TGate(), [q[1]], []),
                (TGate(), [q[2]], []),
                (CXGate(), [q[0], q[1]], []),
                (CXGate(), [q[1], q[2]], []),
                (CXGate(), [q[0], q[1]], []),
                (TGate(), [q[2]], []),
                (CXGate(), [q[1], q[2]], []),
                (CXGate(), [q[0], q[1]], []),
                (TdgGate(), [q[1]], []),
                (TdgGate(), [q[2]], []),
                (CXGate(), [q[1], q[2]], []),
                (CXGate(), [q[0], q[1]], []),
                (TdgGate(), [q[2]], []),
                (CXGate(), [q[1], q[2]], []),
                (HGate(), [q[2]], []),
            ],
            ('12', '01', 'l', 's'): [
                (HGate(), [q[2]], []),
                (CXGate(), [q[1], q[2]], []),
                (TGate(), [q[2]], []),
                (CXGate(), [q[0], q[1]], []),
                (CXGate(), [q[1], q[2]], []),
                (TGate(), [q[1]], []),
                (TGate(), [q[2]], []),
                (CXGate(), [q[0], q[1]], []),
                (CXGate(), [q[1], q[2]], []),
                (TdgGate(), [q[2]], []),
                (CXGate(), [q[0], q[1]], []),
                (CXGate(), [q[1], q[2]], []),
                (CXGate(), [q[0], q[1]], []),
                (TdgGate(), [q[0]], []),
                (TdgGate(), [q[1]], []),
                (TdgGate(), [q[2]], []),
                (HGate(), [q[2]], []),
            ]
            }
        return variant_rules[variant_tag]
        #JLTODO: the inverse of t is tdg, so we can't simply inverse the order
#         inversed_tag = CCX_Variant_Gate.inverse_tag(variant_tag)
#         print("get rules", inversed_tag)
#         if variant_tag in variant_rules.keys():
#             return variant_rules[variant_tag]
#         #since ccx is a self inversed gate the reversed order of the basic gates is its self inverse
#         elif inversed_tag in variant_rules.keys():
#             return variant_rules[inversed_tag][::-1]
#         else:
#             return None

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
    
    @staticmethod
    def inverse_tag(variant_tag):
        label = 's'
        if variant_tag[-1] == 's':
            label = 'p'
        inversed_tag = (variant_tag[1], variant_tag[0], label)

        return inversed_tag

class CCX_01_12_Gate(ControlledGate):
    r"""This equals to the inverse of CCX gate, also known as Toffoli gate.

    **Circuit symbol:**

    .. parsed-literal::

            ┌───┐
qr_0: ──■───┤ T ├───■─────────■─────────────────────■───────────────────
      ┌─┴─┐┌┴───┴┐┌─┴─┐┌───┐  │                     │
qr_1: ┤ X ├┤ Tdg ├┤ X ├┤ T ├──┼───────────■─────────┼───────────■───────
      ├───┤└┬───┬┘└───┘└───┘┌─┴─┐┌─────┐┌─┴─┐┌───┐┌─┴─┐┌─────┐┌─┴─┐┌───┐
qr_2: ┤ T ├─┤ H ├───────────┤ X ├┤ Tdg ├┤ X ├┤ T ├┤ X ├┤ Tdg ├┤ X ├┤ H ├
      └───┘ └───┘           └───┘└─────┘└───┘└───┘└───┘└─────┘└───┘└───┘

    **Matrix representation:**

    .. math::

        CCX q_0, q_1, q_2 =
            I \otimes I \otimes |0 \rangle \langle 0| + CX \otimes |1 \rangle \langle 1| =
           \begin{pmatrix}
                1 & 0 & 0 & 0 & 0 & 0 & 0 & 0\\
                0 & 1 & 0 & 0 & 0 & 0 & 0 & 0\\
                0 & 0 & 1 & 0 & 0 & 0 & 0 & 0\\
                0 & 0 & 0 & 0 & 0 & 0 & 0 & 1\\
                0 & 0 & 0 & 0 & 1 & 0 & 0 & 0\\
                0 & 0 & 0 & 0 & 0 & 1 & 0 & 0\\
                0 & 0 & 0 & 0 & 0 & 0 & 1 & 0\\
                0 & 0 & 0 & 1 & 0 & 0 & 0 & 0
            \end{pmatrix}

    .. note::

        In Qiskit's convention, higher qubit indices are more significant
        (little endian convention). In many textbooks, controlled gates are
        presented with the assumption of more significant qubits as control,
        which in our case would be q_2 and q_1. Thus a textbook matrix for this
        gate will be:

        .. parsed-literal::
                 ┌───┐
            q_0: ┤ X ├
                 └─┬─┘
            q_1: ──■──
                   │
            q_2: ──■──

        .. math::

            CCX\ q_2, q_1, q_0 =
                |0 \rangle \langle 0| \otimes I \otimes I + |1 \rangle \langle 1| \otimes CX =
                \begin{pmatrix}
                    1 & 0 & 0 & 0 & 0 & 0 & 0 & 0\\
                    0 & 1 & 0 & 0 & 0 & 0 & 0 & 0\\
                    0 & 0 & 1 & 0 & 0 & 0 & 0 & 0\\
                    0 & 0 & 0 & 1 & 0 & 0 & 0 & 0\\
                    0 & 0 & 0 & 0 & 1 & 0 & 0 & 0\\
                    0 & 0 & 0 & 0 & 0 & 1 & 0 & 0\\
                    0 & 0 & 0 & 0 & 0 & 0 & 0 & 1\\
                    0 & 0 & 0 & 0 & 0 & 0 & 1 & 0
                \end{pmatrix}

    """

    def __init__(self, label: Optional[str] = None, ctrl_state: Optional[Union[str, int]] = None):
        """Create new CCX gate."""
        super().__init__(
            "ccx", 3, [], num_ctrl_qubits=2, label=label, ctrl_state=ctrl_state, base_gate=XGate()
        )

    def _define(self):
        """
        gate ccx a,b,c
        {
        h c; cx b,c; tdg c; cx a,c;
        t c; cx b,c; tdg c; cx a,c;
        t b; t c; h c; cx a,b;
        t a; tdg b; cx a,b;}
        """
        # pylint: disable=cyclic-import
        from qiskit.circuit.quantumcircuit import QuantumCircuit

        q = QuantumRegister(3, "q")
        qc = QuantumCircuit(q, name=self.name)
        rules = [
            (CXGate(), [q[0], q[1]], []),
            (TGate(), [q[0]], []),
            (TdgGate(), [q[1]], []),
            (CXGate(), [q[0], q[1]], []),
            (TGate(), [q[1]], []),
            (TGate(), [q[2]], []),
            (HGate(), [q[2]], []),
            (CXGate(), [q[0], q[2]], []),
            (TdgGate(), [q[2]], []),
            (CXGate(), [q[1], q[2]], []),
            (TGate(), [q[2]], []),
            (CXGate(), [q[0], q[2]], []),
            (TdgGate(), [q[2]], []),
            (CXGate(), [q[1], q[2]], []),
            (HGate(), [q[2]], []),
        ]
        for instr, qargs, cargs in rules:
            qc._append(instr, qargs, cargs)

        self.definition = qc

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

class CCX_02_01_Gate(ControlledGate):
    r"""This is a variant of Toffoli gate

    **Circuit symbol:**

    .. parsed-literal::

                                       ┌───┐      ┌───┐┌─────┐┌───┐
qr_0: ───────■─────────────────────■───┤ T ├──────┤ X ├┤ Tdg ├┤ X ├
             │                     │   └───┘      └─┬─┘└┬───┬┘└─┬─┘
qr_1: ───────┼───────────■─────────┼───────────■────■───┤ T ├───■──
      ┌───┐┌─┴─┐┌─────┐┌─┴─┐┌───┐┌─┴─┐┌─────┐┌─┴─┐┌───┐ ├───┤
qr_2: ┤ H ├┤ X ├┤ Tdg ├┤ X ├┤ T ├┤ X ├┤ Tdg ├┤ X ├┤ T ├─┤ H ├──────
      └───┘└───┘└─────┘└───┘└───┘└───┘└─────┘└───┘└───┘ └───┘

    **Matrix representation:**

    .. math::

        CCX q_0, q_1, q_2 =
            I \otimes I \otimes |0 \rangle \langle 0| + CX \otimes |1 \rangle \langle 1| =
           \begin{pmatrix}
                1 & 0 & 0 & 0 & 0 & 0 & 0 & 0\\
                0 & 1 & 0 & 0 & 0 & 0 & 0 & 0\\
                0 & 0 & 1 & 0 & 0 & 0 & 0 & 0\\
                0 & 0 & 0 & 0 & 0 & 0 & 0 & 1\\
                0 & 0 & 0 & 0 & 1 & 0 & 0 & 0\\
                0 & 0 & 0 & 0 & 0 & 1 & 0 & 0\\
                0 & 0 & 0 & 0 & 0 & 0 & 1 & 0\\
                0 & 0 & 0 & 1 & 0 & 0 & 0 & 0
            \end{pmatrix}

    .. note::

        In Qiskit's convention, higher qubit indices are more significant
        (little endian convention). In many textbooks, controlled gates are
        presented with the assumption of more significant qubits as control,
        which in our case would be q_2 and q_1. Thus a textbook matrix for this
        gate will be:

        .. parsed-literal::
                 ┌───┐
            q_0: ┤ X ├
                 └─┬─┘
            q_1: ──■──
                   │
            q_2: ──■──

        .. math::

            CCX\ q_2, q_1, q_0 =
                |0 \rangle \langle 0| \otimes I \otimes I + |1 \rangle \langle 1| \otimes CX =
                \begin{pmatrix}
                    1 & 0 & 0 & 0 & 0 & 0 & 0 & 0\\
                    0 & 1 & 0 & 0 & 0 & 0 & 0 & 0\\
                    0 & 0 & 1 & 0 & 0 & 0 & 0 & 0\\
                    0 & 0 & 0 & 1 & 0 & 0 & 0 & 0\\
                    0 & 0 & 0 & 0 & 1 & 0 & 0 & 0\\
                    0 & 0 & 0 & 0 & 0 & 1 & 0 & 0\\
                    0 & 0 & 0 & 0 & 0 & 0 & 0 & 1\\
                    0 & 0 & 0 & 0 & 0 & 0 & 1 & 0
                \end{pmatrix}

    """

    def __init__(self, label: Optional[str] = None, ctrl_state: Optional[Union[str, int]] = None):
        """Create new CCX gate."""
        super().__init__(
            "ccx", 3, [], num_ctrl_qubits=2, label=label, ctrl_state=ctrl_state, base_gate=XGate()
        )

    def _define(self):
        """
        """
        # pylint: disable=cyclic-import
        from qiskit.circuit.quantumcircuit import QuantumCircuit

        q = QuantumRegister(3, "q")
        qc = QuantumCircuit(q, name=self.name)
        rules = [
            (HGate(), [q[2]], []),
            (CXGate(), [q[0], q[2]], []),
            (TdgGate(), [q[2]], []),
            (CXGate(), [q[1], q[2]], []),
            (TGate(), [q[2]], []),
            (CXGate(), [q[0], q[2]], []),
            (TdgGate(), [q[2]], []),
            (CXGate(), [q[1], q[2]], []),
            (TGate(), [q[0]], []),
            (TGate(), [q[2]], []),
            (HGate(), [q[2]], []),
            (CXGate(), [q[1], q[0]], []),
            (TGate(), [q[1]], []),
            (TdgGate(), [q[0]], []),
            (CXGate(), [q[1], q[0]], []),
        ]
        for instr, qargs, cargs in rules:
            qc._append(instr, qargs, cargs)

        self.definition = qc

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

class CCX_01_02_Gate(ControlledGate):
    r"""This is a variant of Toffoli gate

    **Circuit symbol:**

    .. parsed-literal::

                                  ┌───┐           ┌───┐┌─────┐┌───┐
qr_0: ──■─────────────────────■───┤ T ├───────────┤ X ├┤ Tdg ├┤ X ├─────
      ┌─┴─┐┌─────┐┌───┐┌───┐┌─┴─┐┌┴───┴┐┌───┐┌───┐└─┬─┘└─────┘└─┬─┘
qr_1: ┤ X ├┤ Tdg ├┤ X ├┤ T ├┤ X ├┤ Tdg ├┤ X ├┤ T ├──┼───────────┼───────
      ├───┤└─────┘└─┬─┘└───┘└───┘└─────┘└─┬─┘└───┘  │   ┌───┐   │  ┌───┐
qr_2: ┤ H ├─────────■─────────────────────■─────────■───┤ T ├───■──┤ H ├
      └───┘                                             └───┘      └───┘

    **Matrix representation:**

    .. math::

        CCX q_0, q_1, q_2 =
            I \otimes I \otimes |0 \rangle \langle 0| + CX \otimes |1 \rangle \langle 1| =
           \begin{pmatrix}
                1 & 0 & 0 & 0 & 0 & 0 & 0 & 0\\
                0 & 1 & 0 & 0 & 0 & 0 & 0 & 0\\
                0 & 0 & 1 & 0 & 0 & 0 & 0 & 0\\
                0 & 0 & 0 & 0 & 0 & 0 & 0 & 1\\
                0 & 0 & 0 & 0 & 1 & 0 & 0 & 0\\
                0 & 0 & 0 & 0 & 0 & 1 & 0 & 0\\
                0 & 0 & 0 & 0 & 0 & 0 & 1 & 0\\
                0 & 0 & 0 & 1 & 0 & 0 & 0 & 0
            \end{pmatrix}

    .. note::

        In Qiskit's convention, higher qubit indices are more significant
        (little endian convention). In many textbooks, controlled gates are
        presented with the assumption of more significant qubits as control,
        which in our case would be q_2 and q_1. Thus a textbook matrix for this
        gate will be:

        .. parsed-literal::
                 ┌───┐
            q_0: ┤ X ├
                 └─┬─┘
            q_1: ──■──
                   │
            q_2: ──■──

        .. math::

            CCX\ q_2, q_1, q_0 =
                |0 \rangle \langle 0| \otimes I \otimes I + |1 \rangle \langle 1| \otimes CX =
                \begin{pmatrix}
                    1 & 0 & 0 & 0 & 0 & 0 & 0 & 0\\
                    0 & 1 & 0 & 0 & 0 & 0 & 0 & 0\\
                    0 & 0 & 1 & 0 & 0 & 0 & 0 & 0\\
                    0 & 0 & 0 & 1 & 0 & 0 & 0 & 0\\
                    0 & 0 & 0 & 0 & 1 & 0 & 0 & 0\\
                    0 & 0 & 0 & 0 & 0 & 1 & 0 & 0\\
                    0 & 0 & 0 & 0 & 0 & 0 & 0 & 1\\
                    0 & 0 & 0 & 0 & 0 & 0 & 1 & 0
                \end{pmatrix}

    """

    def __init__(self, label: Optional[str] = None, ctrl_state: Optional[Union[str, int]] = None):
        """Create new CCX gate."""
        super().__init__(
            "ccx", 3, [], num_ctrl_qubits=2, label=label, ctrl_state=ctrl_state, base_gate=XGate()
        )

    def _define(self):
        """TODO: is the 01_02 gate switching q[0] and q[1]?
        """
        # pylint: disable=cyclic-import
        from qiskit.circuit.quantumcircuit import QuantumCircuit

        q = QuantumRegister(3, "q")
        qc = QuantumCircuit(q, name=self.name)
        rules = [
            (HGate(), [q[2]], []),
            (CXGate(), [q[0], q[1]], []),
            (TdgGate(), [q[1]], []),
            (CXGate(), [q[2], q[1]], []),
            (TGate(), [q[1]], []),
            (CXGate(), [q[0], q[1]], []),
            (TdgGate(), [q[1]], []),
            (CXGate(), [q[2], q[1]], []),
            (TGate(), [q[0]], []),
            (TGate(), [q[1]], []),
            (CXGate(), [q[2], q[0]], []),
            (TGate(), [q[2]], []),
            (TdgGate(), [q[0]], []),
            (CXGate(), [q[2], q[0]], []),
            (HGate(), [q[2]], []),
        ]
        for instr, qargs, cargs in rules:
            qc._append(instr, qargs, cargs)

        self.definition = qc

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

class CCX_02_01_h_Gate(ControlledGate):
    r"""This is a variant of Toffoli gate

    **Circuit symbol:**

    .. parsed-literal::

             ┌───┐ ┌───┐ ┌───┐┌─────┐
qr_0: ───────┤ X ├─┤ T ├─┤ X ├┤ Tdg ├───────■─────────────────────■──
      ┌─────┐└─┬─┘ └───┘ └─┬─┘└┬───┬┘┌───┐┌─┴─┐┌─────┐┌───┐┌───┐┌─┴─┐
qr_1: ┤ Tdg ├──┼───────────┼───┤ X ├─┤ T ├┤ X ├┤ Tdg ├┤ X ├┤ T ├┤ X ├
      └┬───┬┘  │  ┌─────┐  │   └─┬─┘ └───┘└───┘└─────┘└─┬─┘├───┤└───┘
qr_2: ─┤ H ├───■──┤ Tdg ├──■─────■──────────────────────■──┤ H ├─────
       └───┘      └─────┘                                  └───┘
    **Matrix representation:**

    .. math::

        CCX q_0, q_1, q_2 =
            I \otimes I \otimes |0 \rangle \langle 0| + CX \otimes |1 \rangle \langle 1| =
           \begin{pmatrix}
                1 & 0 & 0 & 0 & 0 & 0 & 0 & 0\\
                0 & 1 & 0 & 0 & 0 & 0 & 0 & 0\\
                0 & 0 & 1 & 0 & 0 & 0 & 0 & 0\\
                0 & 0 & 0 & 0 & 0 & 0 & 0 & 1\\
                0 & 0 & 0 & 0 & 1 & 0 & 0 & 0\\
                0 & 0 & 0 & 0 & 0 & 1 & 0 & 0\\
                0 & 0 & 0 & 0 & 0 & 0 & 1 & 0\\
                0 & 0 & 0 & 1 & 0 & 0 & 0 & 0
            \end{pmatrix}

    .. note::

        In Qiskit's convention, higher qubit indices are more significant
        (little endian convention). In many textbooks, controlled gates are
        presented with the assumption of more significant qubits as control,
        which in our case would be q_2 and q_1. Thus a textbook matrix for this
        gate will be:

        .. parsed-literal::
                 ┌───┐
            q_0: ┤ X ├
                 └─┬─┘
            q_1: ──■──
                   │
            q_2: ──■──

        .. math::

            CCX\ q_2, q_1, q_0 =
                |0 \rangle \langle 0| \otimes I \otimes I + |1 \rangle \langle 1| \otimes CX =
                \begin{pmatrix}
                    1 & 0 & 0 & 0 & 0 & 0 & 0 & 0\\
                    0 & 1 & 0 & 0 & 0 & 0 & 0 & 0\\
                    0 & 0 & 1 & 0 & 0 & 0 & 0 & 0\\
                    0 & 0 & 0 & 1 & 0 & 0 & 0 & 0\\
                    0 & 0 & 0 & 0 & 1 & 0 & 0 & 0\\
                    0 & 0 & 0 & 0 & 0 & 1 & 0 & 0\\
                    0 & 0 & 0 & 0 & 0 & 0 & 0 & 1\\
                    0 & 0 & 0 & 0 & 0 & 0 & 1 & 0
                \end{pmatrix}

    """

    def __init__(self, label: Optional[str] = None, ctrl_state: Optional[Union[str, int]] = None):
        """Create new CCX gate."""
        super().__init__(
            "ccx", 3, [], num_ctrl_qubits=2, label=label, ctrl_state=ctrl_state, base_gate=XGate()
        )

    def _define(self):
        """TODO: is the 01_02 gate switching q[0] and q[1]?
        """
        # pylint: disable=cyclic-import
        from qiskit.circuit.quantumcircuit import QuantumCircuit

        q = QuantumRegister(3, "q")
        qc = QuantumCircuit(q, name=self.name)
        rules = [
            (HGate(), [q[2]], []),
            (CXGate(), [q[2], q[0]], []),
            (TdgGate(), [q[2]], []),
            (TGate(), [q[0]], []),
            (CXGate(), [q[2], q[0]], []),
            (TdgGate(), [q[0]], []),
            (TdgGate(), [q[1]], []),
            (CXGate(), [q[2], q[1]], []),
            (TGate(), [q[1]], []),
            (CXGate(), [q[0], q[1]], []),
            (TdgGate(), [q[1]], []),
            (CXGate(), [q[2], q[1]], []),
            (TGate(), [q[1]], []),
            (CXGate(), [q[0], q[1]], []),
            (HGate(), [q[2]], []),
        ]
        for instr, qargs, cargs in rules:
            qc._append(instr, qargs, cargs)

        self.definition = qc

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
    