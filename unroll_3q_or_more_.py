# This code is part of Qiskit.
#
# (C) Copyright IBM 2017, 2018.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

"""Recursively expands 3q+ gates until the circuit only contains 2q or 1q gates."""

from qiskit.transpiler.basepasses import TransformationPass
from qiskit.exceptions import QiskitError
from qiskit.converters.circuit_to_dag import circuit_to_dag


class Unroll3qOrMore_(TransformationPass):
    """Recursively expands 3q+ gates (except Toffoli) until the circuit only contains 2q or 1q gates."""

    def run(self, dag):
        """Run the Unroll3qOrMore pass on `dag`.

        Args:
            dag(DAGCircuit): input dag
        Returns:
            DAGCircuit: output dag with 1, 2 and 3 qubit gates (Toffoli is the only 3 qubit gate)
        Raises:
            QiskitError: if a 3q+ gate (other than Toffoli) is not decomposable
        """
        for node in dag.multi_qubit_ops():

            print(node.op.name)

            #if the node is a Toffoli, then pass
            if node.op.name == 'ccx':
                continue

            #For any other node, decompose it
            else:
                if dag.has_calibration_for(node):
                    continue
                # TODO: allow choosing other possible decompositions
                rule = node.op.definition.data
                if not rule:
                    if rule == []:  # empty node
                        dag.remove_op_node(node)
                        continue
                    raise QiskitError(
                        "Cannot unroll all 3q or more gates. "
                        "No rule to expand instruction %s." % node.op.name
                    )
                decomposition = circuit_to_dag(node.op.definition)
                decomposition = self.run(decomposition)  # recursively unroll
                dag.substitute_node_with_dag(node, decomposition)
        return dag
