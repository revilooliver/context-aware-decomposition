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
from qiskit.converters import dag_to_circuit
from qiskit import QuantumCircuit
from qiskit.transpiler.layout import Layout


class UnrollToffoli_(TransformationPass):
    """Recursively expands all toffoli gates until the circuit only contains 2q or 1q gates."""

    def __init__(self, coupling_map):
        '''
        Initialize the UnrollToffoli pass. This pass does a layout aware decomposition of the toffoli
        gate. If all three qubits of the toffoli are mapped to each other, we do a 6 qubit decomposition
        else we do an eight qubit decomposition.

        Args:
            coupling_map(CouplingMap) : directed graph representing a coupling map
        '''
        super().__init__()
        self.coupling_map = coupling_map

    def run(self, dag):
        """Run the UnrollToffoli_ pass on `dag`.

        Args:
            dag(DAGCircuit): input dag
        Returns:
            DAGCircuit: output dag with maximum node degrees of 2
        Raises:
            QiskitError: if a 3q+ gate is not decomposable

        Note: In a toffoli gate, node.qargs is a list of three qubits. The first two qubits are the control qubits and the last qubit is the target qubit.
        i.e. node.qargs[0] and node.qargs[1] are control qubits and node.qargs[2] is the target qubit.
        """
        for node in dag.multi_qubit_ops():

            assert node.op.name == 'ccx'

            if dag.has_calibration_for(node):
                continue
           
            # substitute the toffoli gate with its 6/8 qubit decomposition based on the layout
            #The layout has been applied to the dag. So we do not need that information
            canonical_register = dag.qregs["q"]
            trivial_layout = Layout.generate_trivial_layout(canonical_register)
            current_layout = trivial_layout.copy()
           
            #converting the datatype 'qubit' to the datatype 'int'
            control1 = current_layout[node.qargs[0]]
            control2 = current_layout[node.qargs[1]]
            target = current_layout[node.qargs[2]]

            #print('The arguments for the toffoli node are: ', node.qargs[0], node.qargs[1], node.qargs[2])
            #print('The distances between the toffoli qubits are: ', self.coupling_map.distance(control1, control2), 'between qubits 0 and 1')
            #print('The distances between the toffoli qubits are: ', self.coupling_map.distance(control2, target), 'between qubits 1 and 2')
            #print('The distances between the toffoli qubits are: ', self.coupling_map.distance(control1, target), 'between qubits 0 and 2')

            #now compute the distances
            bool1 = self.coupling_map.distance(control1, control2) == 1
            bool2 = self.coupling_map.distance(control2, target) == 1
            bool3 = self.coupling_map.distance(control1, target) == 1

            #distances
            d1 = self.coupling_map.distance(control1, control2)
            d2 = self.coupling_map.distance(control2, target)
            d3 = self.coupling_map.distance(control1, target)


            #if all qubits are adjacent to each other
            if bool1 and bool2 and bool3:

                #print('Case 0: ', control1, control2, target)
                #print('distance between control 1 and control 2: ', d1)
                #print('distance between control 2 and target: ', d2)
                #print('distance between control 1 and target: ', d3)

                # print('The physical qubits for the toffoli are: ', control1, control2, target)
                # print('The required toffoli will be decomposed using a 6 cnot decomposition')

                #create a 6 cnot circuit
                #print('6 cnot toffoli: ', control1, control2, target)
                circuit = QuantumCircuit(3)
                circuit.h(2)
                circuit.cx(1, 2)
                circuit.tdg(2)
                circuit.cx(0, 2)
                circuit.t(2)
                circuit.cx(1, 2)
                circuit.tdg(2)
                circuit.cx(0, 2)
                circuit.t(1)
                circuit.t(2)
                circuit.cx(0, 1)
                circuit.t(0)
                circuit.tdg(1)
                circuit.cx(0, 1)
                circuit.h(2)

                dag_6c_toffoli = circuit_to_dag(circuit)
                dag.substitute_node_with_dag(node, dag_6c_toffoli, wires = [dag_6c_toffoli.wires[0], dag_6c_toffoli.wires[1], dag_6c_toffoli.wires[2]])

            #if physical qubit 1 is connected to both but zero and two are not connected
            elif bool1 and bool2 and (not bool3):

                # print('The physical qubits for the toffoli are: ', control1, control2, target)
                # print('The required toffoli will be decomposed using an 8 cnot decomposition - one in center')

                #create an 8 cnot circuit
                #print('Case 1: ', control1, control2, target)
                #print('distance between control 1 and control 2: ', d1)
                #print('distance between control 2 and target: ', d2)
                #print('distance between control 1 and target: ', d3)


                circuit = QuantumCircuit(3)
                circuit.h(2)
                circuit.t([0, 1, 2])
                circuit.cx(0, 1)
                circuit.cx(1, 2)
                circuit.cx(0, 1)
                circuit.t(2)
                circuit.cx(1, 2)
                circuit.cx(0, 1)
                circuit.tdg([1, 2])
                circuit.cx(1, 2)
                circuit.cx(0, 1)
                circuit.tdg(2)
                circuit.cx(1, 2)
                circuit.h(2)

                dag_8c_toffoli = circuit_to_dag(circuit)
                dag.substitute_node_with_dag(node, dag_8c_toffoli, wires = [dag_8c_toffoli.wires[0], dag_8c_toffoli.wires[1], dag_8c_toffoli.wires[2]])

            #if physical qubit 0 is connected to both but one and two are not connected
            elif bool1 and (not bool2) and bool3:

                # print('The physical qubits for the toffoli are: ', control1, control2, target)
                # print('The required toffoli will be decomposed using an 8 cnot decomposition - zero in center')

                #create an 8 cnot circuit
                #print('Case 2: ', control1, control2, target)
                #print('distance between control 1 and control 2: ', d1)
                #print('distance between control 2 and target: ', d2)
                #print('distance between control 1 and target: ', d3)

                circuit = QuantumCircuit(3)
                circuit.h(2)
                circuit.t([0, 1, 2])
                circuit.cx(0, 1)
                circuit.cx(1, 2)
                circuit.cx(0, 1)
                circuit.t(2)
                circuit.cx(1, 2)
                circuit.cx(0, 1)
                circuit.tdg([1, 2])
                circuit.cx(1, 2)
                circuit.cx(0, 1)
                circuit.tdg(2)
                circuit.cx(1, 2)
                circuit.h(2)

                dag_8c_toffoli = circuit_to_dag(circuit)
                dag.substitute_node_with_dag(node, dag_8c_toffoli, wires = [dag_8c_toffoli.wires[1], dag_8c_toffoli.wires[0], dag_8c_toffoli.wires[2]])
               
            #if physical qubit 2 is connected to both but 0 and 1 are not connected
            elif (not bool1) and bool2 and bool3:

                # print('The physical qubits for the toffoli are: ', control1, control2, target)
                # print('The required toffoli will be decomposed using an 8 cnot decomposition - two in center')

                #create a 8 cnot circuit
                #print('Case 3: ', control1, control2, target)
                #print('distance between control 1 and control 2: ', d1)
                #print('distance between control 2 and target: ', d2)
                #print('distance between control 1 and target: ', d3)
               
                circuit = QuantumCircuit(3)
                circuit.h(1)
                circuit.t([0, 1, 2])
                circuit.cx(0, 1)
                circuit.cx(1, 2)
                circuit.cx(0, 1)
                circuit.t(2)
                circuit.cx(1, 2)
                circuit.cx(0, 1)
                circuit.tdg([1, 2])
                circuit.cx(1, 2)
                circuit.cx(0, 1)
                circuit.tdg(2)
                circuit.cx(1, 2)
                circuit.h(1)

                dag_8c_toffoli = circuit_to_dag(circuit)
                dag.substitute_node_with_dag(node, dag_8c_toffoli, wires = [dag_8c_toffoli.wires[0], dag_8c_toffoli.wires[2], dag_8c_toffoli.wires[1]])
                #node.qargs[1], node.qargs[2] = node.qargs[2], node.qargs[1]

            else:

                print('The routing pass is not correct')


            # rule = node.op.definition.data
            # if not rule:
            #     if rule == []:  # empty node
            #         dag.remove_op_node(node)
            #         continue
            #     raise QiskitError(
            #         "Cannot unroll all toffoli gates. "
            #         "No rule to expand instruction %s." % node.op.name
            #     )
            # decomposition = circuit_to_dag(node.op.definition)
            # decomposition = self.run(decomposition)  # recursively unroll
            # dag.substitute_node_with_dag(node, decomposition)
        return dag