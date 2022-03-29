# This code is part of Qiskit.
#
# (C) Copyright IBM 2019.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

"""Evaluate how good the layout selection was.

No CX direction is considered.
Saves in `property_set['layout_score']` the sum of distances for each circuit CX.
The lower the number, the better the selection.
Therefore, 0 is a perfect layout selection.
"""

from qiskit.transpiler.basepasses import AnalysisPass


class Layout2qPlusDistance_(AnalysisPass):
    """Evaluate how good the layout selection was.

    Saves in `property_set['layout_score']` (or the property name in property_name)
    the sum of distances for each circuit CX.
    The lower the number, the better the selection. Therefore, 0 is a perfect layout selection.
    No CX direction is considered.
    """

    def __init__(self, coupling_map, property_name="layout_score"):
        """Layout2qDistance initializer.

        Args:
            coupling_map (CouplingMap): Directed graph represented a coupling map.
            property_name (str): The property name to save the score. Default: layout_score
        """
        super().__init__()
        self.coupling_map = coupling_map
        self.property_name = property_name

    def run(self, dag):
        """
        Run the Layout2qDistance pass on `dag`.
        Args:
            dag (DAGCircuit): DAG to evaluate.
        """
        layout = self.property_set["layout"]

        if layout is None:
            return

        sum_distance = 0

        for gate in dag.two_qubit_ops():
            physical_q0 = layout[gate.qargs[0]]
            physical_q1 = layout[gate.qargs[1]]

            #the distance being returned is the undirected distance between physical 
            #qubits q0 and q1.
            sum_distance += self.coupling_map.distance(physical_q0, physical_q1) - 1

        #evaluting the distance for toffoli gates
        for gate in dag.multi_qubit_ops():

            #make sure that the only multi qubit gate that stays in the circuit is a ccx gate
            assert gate.op.name == 'ccx'

            #get the physical qubits corresponding to the virtual qubits from the layout
            physical_q0 = layout[gate.qargs[0]]
            physical_q1 = layout[gate.qargs[1]]
            physical_q2 = layout[gate.qargs[2]]

            #find the total distance cost for implementing the toffoli gate

            #the trios paper prescribes treating the toffoli as its 6-cnot decomposition
            #for determining the best mapping. If the 6 cnot decomposition is to work, then all 
            #three physical qubits need to be near to each other.

            #Note that a topology aware mapping scheme would have performed better (i.e. find out
            #the topology of the device and based on that treat the toffoli as its 6/8 cnot decomposition)
            sum_distance += self.coupling_map.distance(physical_q0, physical_q1) - 1
            sum_distance += self.coupling_map.distance(physical_q1, physical_q2) - 1
            sum_distance += self.coupling_map.distance(physical_q0, physical_q2) - 1 


        self.property_set[self.property_name] = sum_distance