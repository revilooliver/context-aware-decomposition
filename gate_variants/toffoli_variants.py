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

    def __init__(self, label: Optional[str] = None, ctrl_state: Optional[Union[str, int]] = None, variant_tag = ['01', '12', 'f', 'p']):
        """Create new CCX gate."""
        super().__init__(
            "ccx_variant", 3, [], num_ctrl_qubits=2, label=label, ctrl_state=ctrl_state, base_gate=XGate()
        )
        print("initialized variant_tag:", variant_tag)
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


    def get_rules(self, q, variant_tag):
        #The Canonical CCX decomposition is ('12', '01','f', 's').
        #Note: the inverse of t is tdg, so we can't simply inverse the order
        # fully connected:
        # 12, 01, s
        # 01, 12, p
        # switch control 0 and control 1:
        # 02, 10, s
        # 10, 02, p
        # switch control 1 and target 2:
        # 01, 20, s
        # 20, 01, p
        # switch control 0 and target 2:
        # 10, 21, s
        # 21, 10, p
        variant_rules = {
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
           ('10', '21', 'f', 's'): [
                (HGate(), [q[2]], []),
                (CXGate(), [q[1], q[0]], []),
                (TdgGate(), [q[0]], []),
                (CXGate(), [q[2], q[0]], []),
                (TGate(), [q[0]], []),
                (CXGate(), [q[1], q[0]], []),
                (TdgGate(), [q[0]], []),
                (CXGate(), [q[2], q[0]], []),
                (TGate(), [q[1]], []),
                (TGate(), [q[1]], []),
                (CXGate(), [q[2], q[1]], []),
                (TGate(), [q[2]], []),
                (TdgGate(), [q[1]], []),
                (CXGate(), [q[2], q[1]], []),
                (HGate(), [q[2]], []),
            ],
            ('21', '10', 'f', 'p'): [
                (HGate(), [q[2]], []),
                (CXGate(), [q[2], q[1]], []),
                (TdgGate(), [q[2]], []),
                (TGate(), [q[1]], []),
                (CXGate(), [q[2], q[1]], []),
                (TdgGate(), [q[1]], []),
                (TdgGate(), [q[0]], []),
                (CXGate(), [q[2], q[0]], []),
                (TGate(), [q[0]], []),
                (CXGate(), [q[1], q[0]], []),
                (TdgGate(), [q[0]], []),
                (CXGate(), [q[2], q[0]], []),
                (TGate(), [q[0]], []),
                (CXGate(), [q[1], q[0]], []),
                (HGate(), [q[2]], []),
            ],
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
            ('10', '02', 'l0', 'p'): [
                (HGate(), [q[2]], []),
                (TGate(), [q[1]], []),
                (TGate(), [q[0]], []),
                (TGate(), [q[2]], []),
                (CXGate(), [q[1], q[0]], []),
                (CXGate(), [q[0], q[2]], []),
                (CXGate(), [q[1], q[0]], []),
                (TGate(), [q[2]], []),
                (CXGate(), [q[0], q[2]], []),
                (CXGate(), [q[1], q[0]], []),
                (TdgGate(), [q[0]], []),
                (TdgGate(), [q[2]], []),
                (CXGate(), [q[0], q[2]], []),
                (CXGate(), [q[1], q[0]], []),
                (TdgGate(), [q[2]], []),
                (CXGate(), [q[0], q[2]], []),
                (HGate(), [q[2]], []),
            ],
            ('02', '10', 'l0', 's'): [
                (HGate(), [q[2]], []),
                (CXGate(), [q[0], q[2]], []),
                (TGate(), [q[2]], []),
                (CXGate(), [q[1], q[0]], []),
                (CXGate(), [q[0], q[2]], []),
                (TGate(), [q[0]], []),
                (TGate(), [q[2]], []),
                (CXGate(), [q[1], q[0]], []),
                (CXGate(), [q[0], q[2]], []),
                (TdgGate(), [q[2]], []),
                (CXGate(), [q[1], q[0]], []),
                (CXGate(), [q[0], q[2]], []),
                (CXGate(), [q[1], q[0]], []),
                (TdgGate(), [q[1]], []),
                (TdgGate(), [q[0]], []),
                (TdgGate(), [q[2]], []),
                (HGate(), [q[2]], []),
            ],
            ('01', '12', 'l1', 'p'): [
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
            ('12', '01', 'l1', 's'): [
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
            ],
            ('02', '21', 'l2', 'p'): [
                (HGate(), [q[2]], []),
                (TGate(), [q[2]], []),
                (TGate(), [q[1]], []),
                (TGate(), [q[0]], []),
                (CXGate(), [q[0], q[2]], []),
                (CXGate(), [q[2], q[1]], []),
                (CXGate(), [q[0], q[2]], []),
                (TGate(), [q[1]], []),
                (CXGate(), [q[2], q[1]], []),
                (CXGate(), [q[0], q[2]], []),
                (TdgGate(), [q[1]], []),
                (TdgGate(), [q[2]], []),
                (CXGate(), [q[2], q[1]], []),
                (CXGate(), [q[0], q[2]], []),
                (TdgGate(), [q[1]], []),
                (CXGate(), [q[2], q[1]], []),
                (HGate(), [q[2]], []),
            ],
            ('21', '02', 'l2', 's'): [
                (HGate(), [q[2]], []),
                (CXGate(), [q[2], q[1]], []),
                (TGate(), [q[1]], []),
                (CXGate(), [q[0], q[2]], []),
                (CXGate(), [q[2], q[1]], []),
                (TGate(), [q[2]], []),
                (TGate(), [q[1]], []),
                (CXGate(), [q[0], q[2]], []),
                (CXGate(), [q[2], q[1]], []),
                (TdgGate(), [q[1]], []),
                (CXGate(), [q[0], q[2]], []),
                (CXGate(), [q[2], q[1]], []),
                (CXGate(), [q[0], q[2]], []),
                (TdgGate(), [q[0]], []),
                (TdgGate(), [q[1]], []),
                (TdgGate(), [q[2]], []),
                (HGate(), [q[2]], []),
            ],
            ('12', '20', 'l2', 'p'): [
                (HGate(), [q[2]], []),
                (TGate(), [q[2]], []),
                (TGate(), [q[1]], []),
                (TGate(), [q[0]], []),
                (CXGate(), [q[1], q[2]], []),
                (CXGate(), [q[2], q[0]], []),
                (CXGate(), [q[1], q[2]], []),
                (TGate(), [q[0]], []),
                (CXGate(), [q[2], q[0]], []),
                (CXGate(), [q[1], q[2]], []),
                (TdgGate(), [q[0]], []),
                (TdgGate(), [q[2]], []),
                (CXGate(), [q[2], q[0]], []),
                (CXGate(), [q[1], q[2]], []),
                (TdgGate(), [q[0]], []),
                (CXGate(), [q[2], q[0]], []),
                (HGate(), [q[2]], []),
            ],
            ('20', '12', 'l2', 's'): [
                (HGate(), [q[2]], []),
                (CXGate(), [q[2], q[0]], []),
                (TGate(), [q[0]], []),
                (CXGate(), [q[1], q[2]], []),
                (CXGate(), [q[2], q[0]], []),
                (TGate(), [q[2]], []),
                (TGate(), [q[0]], []),
                (CXGate(), [q[1], q[2]], []),
                (CXGate(), [q[2], q[0]], []),
                (TdgGate(), [q[0]], []),
                (CXGate(), [q[1], q[2]], []),
                (CXGate(), [q[2], q[0]], []),
                (CXGate(), [q[1], q[2]], []),
                (TdgGate(), [q[0]], []),
                (TdgGate(), [q[1]], []),
                (TdgGate(), [q[2]], []),
                (HGate(), [q[2]], []),
            ],
            }
        try:
            print("look for variant_rules", variant_tag)
            return variant_rules[variant_tag]
        except:
            variant_tag = list(variant_tag)
            pre_tag = variant_tag[0]
            pre_tag_inv = variant_tag[0][::-1]
            suc_tag = variant_tag[1]
            suc_tag_inv = variant_tag[1][::-1]
            two_match_tags = []
            one_match_tags = []
            for tag in variant_rules.keys():
                if tag[-2] == variant_tag[-2]:
                    if tag[0] == pre_tag or tag[0] == pre_tag_inv:
                        if tag[1] == suc_tag or tag[1] == suc_tag_inv:
                            if tag[-1] == variant_tag[-1]:
                                #found three match tag, return the value
                                print("final tag, three match", tag)
                                return variant_rules[tuple(tag)]
                            else:
                                #found two match tag, record it
                                two_match_tags.append(tag)
                        else:
                            #found one match tag, record it
                            one_match_tags.append(tag)
                    else:
                        if tag[1] == suc_tag or tag[1] == suc_tag_inv:
                            #found one match tag, record it
                            one_match_tags.append(tag) 
                else:
                    #the topology flags are different, pass
                    pass
            if len(two_match_tags) != 0:
                print("final tag, two match", two_match_tags[0])
                return variant_rules[tuple(two_match_tags[0])]
            elif len(one_match_tags) != 0:
                print("final tag, one match", one_match_tags[0])
                return variant_rules[tuple(one_match_tags[0])]
                
              
            
            
            
#             variant_tag = list(variant_tag)
#             #based on the last tag 's' or 'p', find the corresponding tag:
#             possible_tags = ['01', '10', '02', '20', '12', '21']
#             if variant_tag[-1] == 's':
#                 if variant_tag[1] == '00':
#                     print("unexpected case")
#                 else:
#                     #specify the successor tag first
#                     #move the same tags to the end
#                     possible_tags.append(possible_tags.pop(possible_tags.index(variant_tag[1])))
#                     possible_tags.append(possible_tags.pop(possible_tags.index(variant_tag[1][::-1])))
#                     for tag in possible_tags:
#                         new_tag = tuple([tag] + variant_tag[1:])
#                         if new_tag in variant_rules.keys():
#                             print("s new_tag", variant_tag, new_tag)
#                             return variant_rules[new_tag]
#                         new_tag_inverse = tuple([tag] + [variant_tag[1][::-1]] + variant_tag[2:])
#     #                     print("inversed tag in rules:", new_tag_inverse in variant_rules.keys())
#                         if new_tag_inverse in variant_rules.keys():
#                             print("s new_tag_inverse", variant_tag, new_tag_inverse)
#                             return variant_rules[new_tag_inverse]

#             elif variant_tag[-1] == 'p':
#                 if variant_tag[0] == '00':
#                     if variant_tag[1] != '00':
#                         possible_tags.append(possible_tags.pop(possible_tags.index(variant_tag[1])))
#                         possible_tags.append(possible_tags.pop(possible_tags.index(variant_tag[1][::-1])))
#                         for tag in possible_tags:
#                             new_tag = tuple([tag] + variant_tag[1:])
#                             if new_tag in variant_rules.keys():
#                                 print("s new_tag", variant_tag, new_tag)
#                                 return variant_rules[new_tag]
#                             new_tag_inverse = tuple([tag] + [variant_tag[1][::-1]] + variant_tag[2:])
#         #                     print("inversed tag in rules:", new_tag_inverse in variant_rules.keys())
#                             if new_tag_inverse in variant_rules.keys():
#                                 print("s new_tag_inverse", variant_tag, new_tag_inverse)
#                                 return variant_rules[new_tag_inverse]
#                     else:
#                         pass 
#                 else:
#                     #move the same tag to the end
#                     possible_tags.append(possible_tags.pop(possible_tags.index(variant_tag[0])))
#                     possible_tags.append(possible_tags.pop(possible_tags.index(variant_tag[0][::-1])))
#                     #specify the predecessor tag first
#                     for tag in possible_tags:
#                         new_tag = tuple([variant_tag[0]] + [tag] + variant_tag[2:])
#                         if new_tag in variant_rules.keys():
#                             print("p new_tag", new_tag)
#                             return variant_rules[new_tag]
#                         new_tag_inverse = tuple([variant_tag[0][::-1]] + [tag] + variant_tag[2:])
#                         if new_tag_inverse in variant_rules.keys():
#                             print("p new_tag_inverse", new_tag_inverse)
#                             return variant_rules[new_tag_inverse]
#             else:
#                 raise AttributeError(f"Unexpcted tag value{variant_tag[-1]}")

        #if both of them are not found:
        print("didn't find match tag")
        if variant_tag[-2] == 'f':
            return variant_rules[('01', '12', 'f', 'p')]
        elif variant_tag[-2] == 'l0':
            print("l0", variant_tag)
            return variant_rules[('02', '10', 'l0', 's')]
        elif variant_tag[-2] == 'l1':
            print("l1", variant_tag)
            return variant_rules[('01', '12', 'l1', 'p')]
        elif variant_tag[-2] == 'l2':
            print("l2", variant_tag)
            return variant_rules[('12', '20', 'l2', 'p')]
                                             
                                             
                

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
