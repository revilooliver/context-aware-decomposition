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
from qiskit.dagcircuit import DAGCircuit
from qiskit.circuit import QuantumRegister

from qiskit.circuit.library.standard_gates.rx import RXGate
from qiskit.circuit.library.standard_gates.ry import RYGate
from qiskit.circuit.library.standard_gates.rz import RZGate
import numpy as np

from gate_variants.toffoli_variants import CCX_Variant_Gate
from gate_variants.cx_variants import CX_Variant_Gate
import qiskit_superstaq


class UnrollToffoliContextAware_(TransformationPass):
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


                print('The physical qubits for the toffoli are: ', physical_q0, physical_q1, physical_q2)
                print('The required toffoli will be decomposed using a 6 cnot decomposition')

                #create a 6 cnot circuit
                
                predecessors = list(dag.quantum_predecessors(node))
                successors = list(dag.quantum_successors(node))
                blocks = self.property_set["block_list"]
                for block in blocks:
                    string = ""
                    for np in block:
                        string = string + np.name + ","
                    print(string)
                #the variant_tag specifies the gate decomposition. ['predecessor', 'successor', 'linear/fullyconnected', 'heavy on predecessor/successor'] First, check all the predecessors and specify the first tag based on the predecessors. Then traverse the successors and specify the second tag 'successor'. The 'linear/fullyconnected' are specified based on the physical qubit connectivity. The last tag 'heavy' is specified while checking both predecessor. The tags are based on the order of the first CNOT gate. For example, '01' means the first cnot gate's control qubit is 0 and target qubit is 1. The initial value is '00'.
                variant_tag=['00','00','f','p']
                for predecessor in predecessors:
                    print("predecessor", predecessor.name)
                    if predecessor.name in {'ccx', 'ccx_variant'}:
                        #check the number of common wires
                        print("pre qargs", type(predecessor.qargs), predecessor.qargs)
                        print("node qargs", node.qargs)
                        intersect = [value for value in node.qargs if value in predecessor.qargs]
                        print("intersect", intersect)
#                         print("intermediate_node1", dag.next_node_on_wire(node=predecessor, wire = predecessor.qargs[0]).name)
#                         print("intermediate_node2", dag.next_node_on_wire(node=predecessor, wire = predecessor.qargs[1]).name)
#                         print("intermediate_node3", dag.next_node_on_wire(node=predecessor, wire = predecessor.qargs[2]).name)
                        # check length
                        if len(intersect) == 2:
                            cond1 = dag.next_node_on_wire(node=predecessor, wire = intersect[0]) is node
                            cond2 = dag.next_node_on_wire(node=predecessor, wire = intersect[1]) is node
                            print("two intersection conditions", cond1, cond2)
                            #make sure there is no gate between the intersection qargs.
                            if cond1 and cond2:
                                variant_tag[0] = str(node.qargs.index(intersect[0])) + str(node.qargs.index(intersect[1]))
                                #set the tag to 'p' since it can be cancelled with the predecessor
                                variant_tag[-1] = 'p'
                            print(variant_tag)
                            break
                        elif len(intersect) == 3:
                            #make sure there is only one gate in between
                            cond1 = dag.next_node_on_wire(node=predecessor, wire = intersect[0]) is node
                            cond2 = dag.next_node_on_wire(node=predecessor, wire = intersect[1]) is node
                            cond3 = dag.next_node_on_wire(node=predecessor, wire = intersect[2]) is node
                            print("three intersection conditions", cond1, cond2, cond3)
                            if cond1 is True:
                                if cond2 is True:
                                    #All true TTT or first two conditions are true: TTF
                                    variant_tag[0] = str(node.qargs.index(intersect[0])) + str(node.qargs.index(intersect[1]))
                                    #set the tag to 'p' since it can be cancelled with the predecessor
                                    variant_tag[-1] = 'p'
                                    break
                                else:
                                    #TFT
                                    if cond3 is True:
                                        variant_tag[0] = str(node.qargs.index(intersect[0])) + str(node.qargs.index(intersect[2]))
                                        #set the tag to 'p' since it can be cancelled with the predecessor
                                        variant_tag[-1] = 'p'
                                        break
                            else:
                                #FTT
                                if cond2 is True and cond3 is True:
                                    variant_tag[0] = str(node.qargs.index(intersect[1])) + str(node.qargs.index(intersect[2]))
                                    #set the tag to 'p' since it can be cancelled with the predecessor
                                    variant_tag[-1] = 'p'
                                    break
                            print(variant_tag)
                            break
                    if predecessor.name == 'cx':
                        #test the cx condition
                        cond1 = dag.next_node_on_wire(node=predecessor, wire = predecessor.qargs[0]) is node
                        cond2 = dag.next_node_on_wire(node=predecessor, wire = predecessor.qargs[1]) is node
                        if cond1 and cond2:
                            #Makesure the CX is the exact predecessor(no gates in between)
                            index_str = UnrollToffoliContextAware_.check_order(node, predecessor)
                            print(index_str)
                            variant_tag[0] = index_str
                            variant_tag[2] = 'p'
                            break
                for successor in successors:
                    print("successor", successor.name)
                    #Makesure the CX is the exact successor(no gates in between)
                    if successor.name == 'cx' and len(list(dag.quantum_predecessors(successor))) == 1:
                        index_str = UnrollToffoliContextAware_.check_order(node, successor)
                        print(index_str)
                        variant_tag[1] = index_str
                        variant_tag[2] = 's'
                #JLTODO: need to consider the two-qubit block and also include the consideration of CX direction.
                variant_dag = UnrollToffoliContextAware_.get_Toffoli_variant_dag(CCX_Variant_Gate, variant_tag=tuple(variant_tag))
                dag.substitute_node_with_dag(node, variant_dag)

            #if physical qubit 1 is connected to both but zero and two are not connected
            elif bool1 and bool2 and (not bool3):

                print('The physical qubits for the toffoli are: ', physical_q0, physical_q1, physical_q2)
                print('The required toffoli will be decomposed using an 8 cnot decomposition - one in center')

                variant_dag = UnrollToffoliContextAware_.get_Toffoli_variant_dag(CCX_Variant_Gate, variant_tag = ('01', '12', 'l', 'p'), index_order = [0,1,2])
                dag.substitute_node_with_dag(node, variant_dag)

            #if physical qubit 0 is connected to both but one and two are not connected
            elif bool1 and (not bool2) and bool3:

                print('The physical qubits for the toffoli are: ', physical_q0, physical_q1, physical_q2)
                print('The required toffoli will be decomposed using an 8 cnot decomposition - zero in center')

                variant_dag = UnrollToffoliContextAware_.get_Toffoli_variant_dag(CCX_Variant_Gate, variant_tag = ('01', '12', 'l', 'p'), index_order = [1,0,2])
                dag.substitute_node_with_dag(node, variant_dag)

            #if physical qubit 2 is connected to both but 0 and 1 are not connected
            elif (not bool1) and bool2 and bool3:

                print('The physical qubits for the toffoli are: ', physical_q0, physical_q1, physical_q2)
                print('The required toffoli will be decomposed using an 8 cnot decomposition - two in center')

                variant_dag = UnrollToffoliContextAware_.get_Toffoli_variant_dag(CCX_Variant_Gate, variant_tag = ('01', '12', 'l', 'p'), index_order = [0,2,1])
                dag.substitute_node_with_dag(node, variant_dag)


            else:

                print('The routing pass is not correct')

        return dag
    
    @staticmethod
    def check_order(node_orign, node_context):
        """check the index of the context gate's physical qubits"""
        #JLTODO:add the assertion for number of qargs.
        index_str = ""
        for qarg in node_context.qargs:
            index_str += str(node_orign.qargs.index(qarg))
        print(index_str)
        return index_str
    
    @staticmethod
    def get_Toffoli_variant_dag(variant_gate, variant_tag, index_order = [0,1,2]):
        new_dag = DAGCircuit()
        reg = QuantumRegister(3)
        new_dag.add_qreg(reg)
        regList = [reg[index_order[0]], reg[index_order[1]], reg[index_order[2]]]
        new_dag.apply_operation_back(variant_gate(variant_tag=variant_tag), regList)
        return new_dag
    
    
class UnrollCnotContextAware_(TransformationPass):
    """Recursively expands all toffoli gates until the circuit only contains 2q or 1q gates."""

    def __init__(self, coupling_map, orientation_map):
        '''
        Initialize the UnrollToffoli pass. This pass does a layout aware decomposition of the toffoli
        gate. If all three qubits of the toffoli are mapped to each other, we do a 6 qubit decomposition
        else we do an eight qubit decomposition.

        Args:
            coupling_map(CouplingMap) : directed graph representing a coupling map
        '''
        super().__init__()
        self.coupling_map = coupling_map
        self.orientation_map = orientation_map

    def run(self, dag):
        """Run the UnrollCnotContextAware_ pass on `dag`.

        Args:
            dag(DAGCircuit): input dag
        Returns:
            DAGCircuit: output dag with CNOT gate different designs
        Raises:
            QiskitError: 
        """
        canonical_register = dag.qregs["q"]
        trivial_layout = Layout.generate_trivial_layout(canonical_register)
        current_layout = trivial_layout.copy()
            
        orientation_map = self.orientation_map
        for node in dag.two_qubit_ops():
            assert node.op.name == 'cx'

#             if dag.has_calibration_for(node):
#                 continue
            if node.op.name == 'cx':
                #print((node.qargs[0].index, node.qargs[1].index), orientation_map[(node.qargs[0].index, node.qargs[1].index)])
                #converting the datatype 'qubit' to the datatype 'int'
                control = current_layout[node.qargs[0]]
                target = current_layout[node.qargs[1]]
                #set the orientation based on the orientation map
                orientation = orientation_map[(control, target)]
                predecessors = list(dag.quantum_predecessors(node))
                successors = list(dag.quantum_successors(node))
                for successor in successors:
                    if successor.name in {'cx'}:
                        intersect = [value for value in node.qargs if value in successor.qargs]
                        print("intersect", intersect)
                        # check length
                        if len(intersect) == 2:
                            #these two CNOTs apply to the same qubits, first check the direction of the link. Then check if two CNOTs have the same controll qubit.
                            #TODOJL: need to identify the case with single-qubit gates in between
                            control_succ = current_layout[successor.qargs[0]]
                            target_succ = current_layout[successor.qargs[1]]
                            orientation_succ = orientation_map[(control_succ, target_succ)]
                            #these two CNOTs have the same direction or different direction we just need to set the orientation accordingly
                            variant_tag = ['00', '11'] + [orientation]
                            variant_tag_succ = ['11', '00'] + [orientation_succ]
                            variant_dag = UnrollCnotContextAware_.get_CNOT_variant_dag(variant_tag = tuple(variant_tag))
                            dag.substitute_node_with_dag(node, variant_dag)  
                            variant_dag_succ = UnrollCnotContextAware_.get_CNOT_variant_dag(variant_tag = tuple(variant_tag_succ))                   
                            dag.substitute_node_with_dag(successor, variant_dag_succ)
        return dag
    
    
    
    @staticmethod
    def get_CNOT_variant_dag(variant_tag = ('00', '11', 'd'), index_order = [0,1]):
        
        q = QuantumRegister(2, "q")
        qc = QuantumCircuit(q)
        
        try:
            rules = UnrollCnotContextAware_.get_rules(q, variant_tag)
        except:
            raise AttributeError(f"Variant_tag({variant_tag})not defined")

        for instr, qargs, cargs in rules:
            qc._append(instr, qargs, cargs)
        new_dag = circuit_to_dag(qc)
        return new_dag

    @staticmethod
    def get_rules(q, variant_tag):
        print(variant_tag)
        variant_rules = {
            ('00', '11', 'f'): [
                (qiskit_superstaq.AceCR("+-"), [q[0], q[1]], []),
                (RYGate(np.pi), [q[0]], []),
                (RXGate(-np.pi/2), [q[1]], []),
                (RZGate(-np.pi/2), [q[0]], []),
            ],
            ('11', '00', 'f'): [
                (RZGate(np.pi/2), [q[0]], []),
                (RYGate(np.pi), [q[0]], []),
                (RXGate(np.pi/2), [q[1]], []),
                (qiskit_superstaq.AceCR("+-"), [q[0], q[1]], []),
            ],
            ('01', '10', 'f'): [
                (RZGate(np.pi/2), [q[0]], []),
                (RXGate(np.pi/2), [q[1]], []),
                (qiskit_superstaq.AceCR("-+"), [q[0], q[1]], []),
                (RXGate(np.pi), [q[0]], []),
            ],
            ('10', '01', 'f'): [
                (RXGate(np.pi/2), [q[0]], []),
                (qiskit_superstaq.AceCR("-+"), [q[0], q[1]], []),
                (RXGate(-np.pi/2), [q[1]], []),
                (RZGate(-np.pi/2), [q[0]], []),
            ],
            
            
            
            ('00', '11', 'b'): [
                (RZGate(np.pi), [q[0]], []),
                (RYGate(np.pi/2), [q[0]], []),
                (RZGate(np.pi/2), [q[1]], []),
                (RXGate(np.pi/2), [q[1]], []),
                (qiskit_superstaq.AceCR("+-"), [q[1], q[0]], []),
                (RZGate(np.pi/2), [q[0]], []),
                (RXGate(np.pi/2), [q[0]], []),
                (RYGate(-np.pi/2), [q[1]], []),
            ],
            ('11', '00', 'b'): [
                (RYGate(np.pi/2), [q[1]], []),
                (RXGate(-np.pi/2), [q[0]], []),
                (RZGate(-np.pi/2), [q[0]], []),
                (qiskit_superstaq.AceCR("+-"), [q[1], q[0]], []),
                (RXGate(-np.pi/2), [q[1]], []),
                (RZGate(-np.pi/2), [q[1]], []),
                (RYGate(-np.pi/2), [q[0]], []),
                (RZGate(-np.pi), [q[0]], []),
            ],
            
          
            }
        return variant_rules[variant_tag]