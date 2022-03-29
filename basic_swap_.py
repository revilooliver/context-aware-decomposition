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

"""Map (with minimum effort) a DAGCircuit onto a `coupling_map` adding swap gates."""

from qiskit.transpiler.basepasses import TransformationPass
from qiskit.transpiler.exceptions import TranspilerError
from qiskit.dagcircuit import DAGCircuit
from qiskit.transpiler.layout import Layout
from qiskit.circuit.library.standard_gates import SwapGate
import networkx as nx
import qiskit


class BasicSwap_(TransformationPass):
    """Map (with minimum effort) a DAGCircuit onto a `coupling_map` adding swap gates.

    The basic mapper is a minimum effort to insert swap gates to map the DAG onto
    a coupling map. When a cx is not in the coupling map possibilities, it inserts
    one or more swaps in front to make it compatible.
    """

    def __init__(self, coupling_map, fake_run=False):
        """BasicSwap initializer.

        Args:
            coupling_map (CouplingMap): Directed graph represented a coupling map.
            fake_run (bool): if true, it only pretend to do routing, i.e., no
                swap is effectively added.
        """
        super().__init__()
        self.coupling_map = coupling_map
        self.fake_run = fake_run

    def run(self, dag):
        """Run the BasicSwap pass on `dag`.

        Args:
            dag (DAGCircuit): DAG to map.

        Returns:
            DAGCircuit: A mapped DAG.

        Raises:
            TranspilerError: if the coupling map or the layout are not
            compatible with the DAG.
        """

        #the graph connectivity
        # connectivity = nx.Graph()
        # qr = qiskit.circuit.QuantumRegister(self.coupling_map.size())
        # for pair in self.coupling_map.graph.weighted_edge_list(): #the edge list contains elements of the form (source, target, weight)
        #     connectivity.add_edge(qr[pair[0]], qr[pair[1]])

        if self.fake_run:
            return self.fake_run(dag)

        #copy the metadata (the circuit global phase, the duration, classical and quantum registers etc)
        #and keep the dag empty (that is do not copy the content)
        new_dag = dag._copy_circuit_metadata()

        if len(dag.qregs) != 1 or dag.qregs.get("q", None) is None:
            raise TranspilerError("Basic swap runs on physical circuits only")

        if len(dag.qubits) > len(self.coupling_map.physical_qubits):
            raise TranspilerError("The layout does not match the amount of qubits in the DAG")

        canonical_register = dag.qregs["q"]
        trivial_layout = Layout.generate_trivial_layout(canonical_register)
        
        #a diciontary of |dag.qregs['q']| terms which has integers as keys and qubits as values.
        #Eg - {0: Qubit(QuantumRegister(6, 'q'), 0), 1: Qubit(QuantumRegister(6, 'q'), 1), ..., 5: Qubit(QuantumRegister(6, 'q'), 5)}
        current_layout = trivial_layout.copy()
        #print('The starting layout is: ', current_layout)
        #print('#######################################################################################################################################################################################')

        for layer in dag.serial_layers():
            subdag = layer["graph"]

            #route two qubit gates
            #for all two qubit gates in the layer
            for gate in subdag.two_qubit_ops():

                
                physical_q0 = current_layout[gate.qargs[0]]
                physical_q1 = current_layout[gate.qargs[1]]

                #print('The virtual qubits for the cnot are: ', gate.qargs[0], gate.qargs[1])
                #print('The physical qubits for the cnot are: ', physical_q0, physical_q1)

                #if the qubits are not adjacent to each other
                if self.coupling_map.distance(physical_q0, physical_q1) != 1:
                    
                    # Insert a new layer with the SWAP(s).
                    swap_layer = DAGCircuit()
                    swap_layer.add_qreg(canonical_register)

                    #compute the shortest undirected path from physical qubit 0 to physical qubit 1
                    #the list 'path' consists of the indices from qubit 0 to qubit 1
                    path = self.coupling_map.shortest_undirected_path(physical_q0, physical_q1)
                    #print('The routing path for the cx gate is: ')
                    #print([idx for idx in path])
                    for swap in range(len(path) - 2):
                        
                        #'connected_wire_1' is the first end and 'connected_wire_2' is the 
                        #second end of the path between two adjacent qubits
                        connected_wire_1 = path[swap]
                        connected_wire_2 = path[swap + 1]

                        #convert the data type from 'int' to 'qiskit.circuit.quantumregister.Qubit'
                        qubit_1 = current_layout[connected_wire_1]
                        qubit_2 = current_layout[connected_wire_2]

                        #create the swap operation to route the qubits for the particular layer
                        swap_layer.apply_operation_back(
                            SwapGate(), qargs=[qubit_1, qubit_2], cargs=[]
                        )

                    # layer insertion
                    order = current_layout.reorder_bits(new_dag.qubits)
                    new_dag.compose(swap_layer, qubits=order)

                    # update current_layout
                    for swap in range(len(path) - 2):
                        current_layout.swap(path[swap], path[swap + 1])

                #print('The new layout is: ', current_layout)
                #print('#######################################################################################################################################################################################')

            # #for all the multi qubit gates in the layer
            for gate in subdag.multi_qubit_ops():

                #assert that the only multi qubit gate is the toffoli gate
                assert gate.op.name == 'ccx'

                #extract the physical qubits corresponding to the virtual qubits
                physical_q0 = current_layout[gate.qargs[0]]
                physical_q1 = current_layout[gate.qargs[1]]
                physical_q2 = current_layout[gate.qargs[2]]

                # print('qargs_0: ', gate.qargs[0], ' qargs_1: ', gate.qargs[1], ' qargs_2: ', gate.qargs[2])

                #a dictioanry that defines what the final 'destination' qubit would be and what the other two 'starting' qubits would be
                #maintains the initial 'virtual qubit-physical qubit' mapping and also tracks the order in which the 'starting' qubits are routed
                # route_dict = {}
                # route_dict[gate.qargs[0]] = None
                # route_dict[gate.qargs[1]] = None
                # route_dict[gate.qargs[2]] = None

                #print('The virtual qubits for the toffoli are: ', gate.qargs[0], gate.qargs[1], gate.qargs[2])
                #print('The physical qubits for the toffoli: ', physical_q0, physical_q1, physical_q2)

                #if the qubits are not adjacent to each other
                if self.coupling_map.distance(physical_q0, physical_q1) != 1 or self.coupling_map.distance(physical_q0, physical_q2) != 1 or self.coupling_map.distance(physical_q1, physical_q2) != 1:

                    #Insert a new layer with the SWAP(s)
                    swap_layer = DAGCircuit()
                    swap_layer.add_qreg(canonical_register)

                    #compute the convenient path
                    #the initial locations for the Toffoli
                    initial_locs = [physical_q0, physical_q1, physical_q2]

                    #we have the minimum length and the paths leading to the minimum length
                    min_length = float('inf')
                    min_paths = None

                    for index_, i in enumerate(initial_locs):
                        paths = []

                        for j in initial_locs:

                            if i == j:
                                continue

                            paths.append(self.coupling_map.shortest_undirected_path(j, i))

                        length = sum([len(path) - 2 for path in paths])
                        #print(i, ': length of paths: ', length)

                        if min_length > length:
                            min_length = length
                            min_paths = paths

                            # if index_ == 0:
                            #     route_dict[gate.qargs[0]] = ('destination')
                            #     route_dict[gate.qargs[1]] = ('path-1-starting-point')
                            #     route_dict[gate.qargs[2]] = ('path-2-starting-point')

                            # elif index_ == 1:
                            #     route_dict[gate.qargs[1]] = ('destination')
                            #     route_dict[gate.qargs[0]] = ('path-1-starting-point')
                            #     route_dict[gate.qargs[2]] = ('path-2-starting-point')

                            # elif index_ == 2:
                            #     route_dict[gate.qargs[2]] = ('destination')
                            #     route_dict[gate.qargs[0]] = ('path-1-starting-point')
                            #     route_dict[gate.qargs[1]] = ('path-2-starting-point')

                        
                    #the minimum paths chosen for each toffoli
                    #print('The min paths are: ')
                    #print('path 1: ', [idx for idx in min_paths[0]])
                    #print('path 2: ', [idx for idx in min_paths[1]])

                    #first path
                    path = min_paths[0]
                    for swap in range(len(path) - 2):

                        #get the two qubits
                        connected_wire_1 = path[swap]
                        connected_wire_2 = path[swap + 1]

                        #qubits
                        qubit_1 = current_layout[connected_wire_1]
                        qubit_2 = current_layout[connected_wire_2]

                        #create the swap operation to route the qubits for the particular layer
                        swap_layer.apply_operation_back(
                            SwapGate(), qargs=[qubit_1, qubit_2], cargs=[]
                        )

                    # layer insertion
                    # order = current_layout.reorder_bits(new_dag.qubits)
                    # print('order: ', order)
                    # new_dag.compose(swap_layer, qubits=order)

                    # # update current_layout
                    # for swap in range(len(min_paths[0]) - 2):
                    #     current_layout.swap(min_paths[0][swap], min_paths[0][swap + 1])

                    

                    # swap_layer = DAGCircuit()
                    # swap_layer.add_qreg(canonical_register)
                    # path = self.coupling_map.shortest_undirected_path(current_layout[list(route_dict.keys())[list(route_dict.values()).index('path-2-starting-point')]], current_layout[list(route_dict.keys())[list(route_dict.values()).index('destination')]])

                    # #second path
                    path = min_paths[1]
                    for swap in range(len(path) - 2):

                        #get the two qubits
                        connected_wire_1 = path[swap]
                        connected_wire_2 = path[swap + 1]

                        #qubits
                        qubit_1 = current_layout[connected_wire_1]
                        qubit_2 = current_layout[connected_wire_2]

                        #create the swap operation to route the qubits for the particular layer
                        swap_layer.apply_operation_back(
                            SwapGate(), qargs=[qubit_1, qubit_2], cargs=[]
                        )

                    # layer insertion
                    order = current_layout.reorder_bits(new_dag.qubits)
                    #print('order: ', order)
                    new_dag.compose(swap_layer, qubits=order)

                    #update current_layout
                    for swap in range(len(min_paths[0]) - 2):
                        current_layout.swap(min_paths[0][swap], min_paths[0][swap + 1])

                    for swap in range(len(path) - 2):
                        current_layout.swap(path[swap], path[swap + 1])

                #print('Current layout: ', current_layout)
                #print('#######################################################################################################################################################################################')


            order = current_layout.reorder_bits(new_dag.qubits)
            new_dag.compose(subdag, qubits=order)

        return new_dag


    def _fake_run(self, dag):
        """Do a fake run the BasicSwap pass on `dag`.

        Args:
            dag (DAGCircuit): DAG to improve initial layout.

        Returns:
            DAGCircuit: The same DAG.

        Raises:
            TranspilerError: if the coupling map or the layout are not
            compatible with the DAG.
        """
        if len(dag.qregs) != 1 or dag.qregs.get("q", None) is None:
            raise TranspilerError("Basic swap runs on physical circuits only")

        if len(dag.qubits) > len(self.coupling_map.physical_qubits):
            raise TranspilerError("The layout does not match the amount of qubits in the DAG")

        canonical_register = dag.qregs["q"]
        trivial_layout = Layout.generate_trivial_layout(canonical_register)
        current_layout = trivial_layout.copy()

        for layer in dag.serial_layers():
            subdag = layer["graph"]
            for gate in subdag.two_qubit_ops():
                physical_q0 = current_layout[gate.qargs[0]]
                physical_q1 = current_layout[gate.qargs[1]]
                if self.coupling_map.distance(physical_q0, physical_q1) != 1:
                    path = self.coupling_map.shortest_undirected_path(physical_q0, physical_q1)
                    # update current_layout
                    for swap in range(len(path) - 2):
                        current_layout.swap(path[swap], path[swap + 1])

        self.property_set["final_layout"] = current_layout
        return dag





