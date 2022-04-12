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
from gate_variants.bridge_variants import Bridge_Variant_Gate
from gate_variants.swap_variants import SWAP_Variant_Gate
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
        multi_qubit_op_list = dag.multi_qubit_ops()
        substituted_nodes = []
        substituted_tags = []
        for node in multi_qubit_op_list:

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

            variant_tag = ['00','00','f','p']
            variant_tag_succ = ['00','00','f','p']
            #if all qubits are adjacent to each other
            if bool1 and bool2 and bool3:


                print('The physical qubits for the toffoli are: ', control1, control2, target)
                print('The required toffoli will be decomposed using a 6 cnot decomposition')
                index_order = [0, 1, 2]
                #create a 6 cnot circuit
            #if physical qubit 1 is connected to both but zero and two are not connected
            elif bool1 and bool2 and (not bool3):

                print('The physical qubits for the toffoli are: ', control1, control2, target)
                print('The required toffoli will be decomposed using an 8 cnot decomposition - one in center')
                variant_tag[-2] = variant_tag_succ[-2] = 'l1' #+ str(actual_order.index(control2))
#                     variant_dag = UnrollToffoliContextAware_.get_Toffoli_variant_dag(CCX_Variant_Gate, variant_tag = ('01', '12', 'l1', 'p'), index_order = [0,1,2])
#                     dag.substitute_node_with_dag(node, variant_dag)

            #if physical qubit 0 is connected to both but one and two are not connected
            elif bool1 and (not bool2) and bool3:

                print('The physical qubits for the toffoli are: ', control1, control2, target)
                print('The required toffoli will be decomposed using an 8 cnot decomposition - zero in center')
                variant_tag[-2] = variant_tag_succ[-2] = 'l0' #+ str(actual_order.index(control1))
#                     variant_dag = UnrollToffoliContextAware_.get_Toffoli_variant_dag(CCX_Variant_Gate, variant_tag = ('01', '12', 'l0', 'p'), index_order = [1,0,2])
#                     dag.substitute_node_with_dag(node, variant_dag)

            #if physical qubit 2 is connected to both but 0 and 1 are not connected
            elif (not bool1) and bool2 and bool3:
                print('The physical qubits for the toffoli are: ', control1, control2, target)
                print('The required toffoli will be decomposed using an 8 cnot decomposition - two in center')
                variant_tag[-2] = variant_tag_succ[-2] = 'l2' #+ str(actual_order.index(target))
#                     variant_dag = UnrollToffoliContextAware_.get_Toffoli_variant_dag(CCX_Variant_Gate, variant_tag = ('01', '12', 'l2', 'p'), index_order = [0,2,1])
#                     dag.substitute_node_with_dag(node, variant_dag)


            else:

                print('The routing pass is not correct')
            
            if node in substituted_nodes:
                variant_tag = substituted_tags[substituted_nodes.index(node)]
                variant_tag[-2] = variant_tag_succ[-2]
                print("sub_tag before optimize", variant_tag)
                
                successors = list(dag.quantum_successors(node))
                blocks = self.property_set["block_list"]
                two_qubit_block = []
                for successor in successors:
                    if successor.name in {'ccx'}:
                        variant_tag, variant_tag_succ = UnrollToffoliContextAware_.specify_variant_succ_ccx_tag(dag, variant_tag, variant_tag_succ, node, successor, last_tag = 'p')
                        print("calculated tags for substituted", variant_tag, variant_tag_succ)
                        if variant_tag_succ[0:2] != ['00','00']:
                            #the variant_tag_succ has been specified, add the successor to the substituted nodes
#                             substituted_nodes.append(successor)
#                             substituted_tags.append(variant_tag_succ)

                            variant_tag_succ = ['00','00','f','p']
                            break
#                     if successor.name in {'cx', 'swap'}:
#                         variant_tag = UnrollToffoliContextAware_.specify_variant_succ_cx_tag(dag, variant_tag, node, successor, last_tag = 'p')
#                     #search for two qubit blocks:
#                     for block in blocks:
#                         if successor in block:
#                             suc_index = successors.index(successor)
#                             if suc_index != len(successors) - 1: #if it's not the last one
#                                 for successor2 in successors[suc_index + 1:]:
#                                     if successor2 in block:
#                                         two_qubit_block = [successor, successor2]
#                                         break
#                     if len(two_qubit_block) != 0:
#                         print("identified two_qubit block for successor")
#                         print(successor.qargs, successor2.qargs)
#                         intersect = [value for value in node.qargs if value in successor.qargs or value in successor2.qargs]
#                         variant_tag[1] = str(node.qargs.index(intersect[0])) + str(node.qargs.index(intersect[1]))
#                         two_qubit_block = []
                        
                print("the optimized substituted tag", variant_tag)
                variant_dag = UnrollToffoliContextAware_.get_Toffoli_variant_dag(CCX_Variant_Gate, variant_tag=tuple(variant_tag))
                dag.substitute_node_with_dag(node, variant_dag)
                pass
            else:
#                 order_list = [control1, control2, target]
#                 orign_list = [control1, control2, target]
#                 order_list.sort()
                
#                 index_order = [orign_list.index(order_list[0]),orign_list.index(order_list[1]),orign_list.index(order_list[2]) ]
#                 print("index_order",index_order)
                predecessors = list(dag.quantum_predecessors(node))
                successors = list(dag.quantum_successors(node))
                blocks = self.property_set["block_list"]
                #the variant_tag specifies the gate decomposition. ['predecessor', 'successor', 'linear/fullyconnected', 'heavy on predecessor/successor'] First, check all the predecessors and specify the first tag based on the predecessors. Then traverse the successors and specify the second tag 'successor'. The 'linear/fullyconnected' are specified based on the physical qubit connectivity. The last tag 'heavy' is specified while checking both predecessor. The tags are based on the order of the first CNOT gate. For example, '01' means the first cnot gate's control qubit is 0 and target qubit is 1. The initial value is '00'.
                #first we need to consider the successors to identify the gate cancellation with inversed gates
                two_qubit_block = []
                for successor in successors:
                    #print(successor.name)
                    if successor.name in {'ccx'}:
                        variant_tag, variant_tag_succ = UnrollToffoliContextAware_.specify_variant_succ_ccx_tag(dag, variant_tag, variant_tag_succ, node, successor)
                        print("calculated tags", variant_tag, variant_tag_succ)
                        if variant_tag_succ[0:2] != ['00','00']:
                            #the variant_tag_succ has been specified, add the successor to the substituted nodes
                            substituted_nodes.append(successor)
                            substituted_tags.append(variant_tag_succ)
#                             variant_dag_succ = UnrollToffoliContextAware_.get_Toffoli_variant_dag(CCX_Variant_Gate, variant_tag=tuple(variant_tag_succ))
#                             dag.substitute_node_with_dag(successor, variant_dag_succ)
                            variant_tag_succ = ['00','00','f','p']
                            break
                    if successor.name in {'cx', 'swap'}:
                        variant_tag = UnrollToffoliContextAware_.specify_variant_succ_cx_tag(dag, variant_tag, node, successor)
                    #search for two qubit blocks:
                    for block in blocks:
                        if successor in block:
                            suc_index = successors.index(successor)
                            if suc_index != len(successors) - 1: #if it's not the last one
                                for successor2 in successors[suc_index + 1:]:
                                    if successor2 in block:
                                        two_qubit_block = [successor, successor2]
                                        break
                    if len(two_qubit_block) != 0:
                        print("identified two_qubit block for successor")
                        print(successor.qargs, successor2.qargs)
                        intersect = [value for value in node.qargs if value in successor.qargs or value in successor2.qargs]
                        variant_tag[1] = str(node.qargs.index(intersect[0])) + str(node.qargs.index(intersect[1]))
                        variant_tag[-1] = 's'
                        two_qubit_block = []
                two_qubit_block = []


                for predecessor in predecessors:
                    if predecessor.name in {'cx', 'swap'}:
                        variant_tag = UnrollToffoliContextAware_.specify_variant_pre_cx_tag(dag, variant_tag, node, predecessor)
                        
                    #search for two qubit blocks:
                    for block in blocks:
                        if predecessor in block:
                            pre_index = predecessors.index(predecessor)
                            if pre_index != len(predecessors) - 1: #if it's not the last one
                                for predecessor2 in predecessors[pre_index + 1:]:
                                    if predecessor2 in block:
                                        two_qubit_block = [predecessor, predecessor2]
                                        break
                    if len(two_qubit_block) != 0:
                        print("identified two_qubit block for predecessor")
                        print(predecessor.qargs, predecessor2.qargs)
                        intersect = [value for value in node.qargs if value in predecessor.qargs or value in predecessor2.qargs]
                        variant_tag[0] = str(node.qargs.index(intersect[0])) + str(node.qargs.index(intersect[1]))
                        variant_tag[-1] = 'p'
                        two_qubit_block = []
               
                
                variant_dag = UnrollToffoliContextAware_.get_Toffoli_variant_dag(CCX_Variant_Gate, variant_tag=tuple(variant_tag),index_order = [0,1,2])
                return_val = dag.substitute_node_with_dag(node, variant_dag)

        return dag
    @staticmethod
    def specify_variant_pre_cx_tag(dag, variant_tag, node, predecessor):
        intersect = [value for value in node.qargs if value in predecessor.qargs]
        # check length
        if len(intersect) == 2:
            cond1 = dag.next_node_on_wire(node=predecessor, wire = intersect[0]) is node
            cond2 = dag.next_node_on_wire(node=predecessor, wire = intersect[1]) is node
            print("predecessor {} two intersection conditions:{}{}".format(predecessor.name, cond1, cond2))
            #make sure there is no gate between the intersection qargs.
            if cond1 and cond2:
                variant_tag[0] = str(node.qargs.index(intersect[0])) + str(node.qargs.index(intersect[1]))
                #don't need to set the last tag since it's already been set to 'p'
        return variant_tag
    @staticmethod
    def specify_variant_succ_cx_tag(dag, variant_tag, node, successor, last_tag = 's'):
        intersect = [value for value in node.qargs if value in successor.qargs]
        # check length
        if len(intersect) == 2:
            cond1 = dag.next_node_on_wire(node=node, wire = intersect[0]) is successor
            cond2 = dag.next_node_on_wire(node=node, wire = intersect[1]) is successor
            print("successor {} two intersection conditions:{}{}".format(successor.name, cond1, cond2))
            #make sure there is no gate between the intersection qargs.
            if cond1 and cond2:
                variant_tag[1] = str(node.qargs.index(intersect[0])) + str(node.qargs.index(intersect[1]))
                #set the tag to 's' since it can be cancelled with the successor
                variant_tag[-1] = last_tag
        return variant_tag

#     @staticmethod
#     def specify_variant_succ_tag(dag, variant_tag):
#         #search for two qubit blocks:
#         for block in blocks:
#             if successor in block:
#                 suc_index = successors.index(successor)
#                 if suc_index != len(successors) - 1: #if it's not the last one
#                     for successor2 in successors[suc_index + 1:]:
#                         if successor2 in block:
#                             two_qubit_block = [successor, successor2]
#                             break
#         if len(two_qubit_block) != 0:
#             print("identified two_qubit block for successor")
#             print(successor.qargs, successor2.qargs)
#             intersect = [value for value in node.qargs if value in successor.qargs or value in successor2.qargs]
#             variant_tag[1] = str(node.qargs.index(intersect[0])) + str(node.qargs.index(intersect[1]))
#             variant_tag[-1] = 's'
#             two_qubit_block = []
#         return variant_tag
    
    @staticmethod
    def specify_variant_succ_ccx_tag(dag, variant_tag, variant_tag_succ, node, successor, last_tag = 's'):
        intersect = [value for value in node.qargs if value in successor.qargs]
        # check length
        if len(intersect) == 2:
            cond1 = dag.next_node_on_wire(node=node, wire = intersect[0]) is successor
            cond2 = dag.next_node_on_wire(node=node, wire = intersect[1]) is successor
            print("two intersection conditions", cond1, cond2)
            #make sure there is no gate between the intersection qargs.
            if cond1 and cond2:
                variant_tag[1] = str(node.qargs.index(intersect[0])) + str(node.qargs.index(intersect[1]))
                #set the tag to 's' since it can be cancelled with the successor
                variant_tag[-1] = last_tag
                variant_tag_succ[0] = str(successor.qargs.index(intersect[0])) + str(successor.qargs.index(intersect[1]))
                #variant_tag_succ[1] = 
                variant_tag_succ[-1] = 'p'
                return variant_tag, variant_tag_succ
        elif len(intersect) == 3:
            #make sure there is only one gate in between
            cond1 = dag.next_node_on_wire(node=node, wire = intersect[0]) is successor
            cond2 = dag.next_node_on_wire(node=node, wire = intersect[1]) is successor
            cond3 = dag.next_node_on_wire(node=node, wire = intersect[2]) is successor
            print("three intersection conditions", cond1, cond2, cond3)
            print("three qargs", intersect[0], intersect[1], intersect[2])
            if cond1 is True:
                if cond2 is True:
                    #All true TTT or first two conditions are true: TTF
                    variant_tag[1] = str(node.qargs.index(intersect[0])) + str(node.qargs.index(intersect[1]))
                    #set the tag to 's' since it can be cancelled with the successor
                    variant_tag[-1] = last_tag
                    variant_tag_succ[0] = str(successor.qargs.index(intersect[0])) + str(successor.qargs.index(intersect[1]))
                    variant_tag_succ[-1] = 'p'
                else:
                    #TFT
                    if cond3 is True:
                        variant_tag[1] = str(node.qargs.index(intersect[0])) + str(node.qargs.index(intersect[2]))
                        #set the tag to 's' since it can be cancelled with the successor
                        variant_tag[-1] = last_tag
                        variant_tag_succ[0] = str(successor.qargs.index(intersect[0])) + str(successor.qargs.index(intersect[2]))
                        variant_tag_succ[-1] = 'p'
            else:
                #FTT
                if cond2 is True and cond3 is True:
                    variant_tag[1] = str(node.qargs.index(intersect[1])) + str(node.qargs.index(intersect[2]))
                    #set the tag to 's' since it can be cancelled with the successor
                    variant_tag[-1] = last_tag
                    variant_tag_succ[0] = str(successor.qargs.index(intersect[1])) + str(successor.qargs.index(intersect[2]))
                    variant_tag_succ[-1] = 'p'
        return variant_tag, variant_tag_succ
    
#     @staticmethod
#     def check_order(node_orign, node_context):
#         """check the index of the context gate's physical qubits"""
#         #JLTODO:add the assertion for number of qargs.
#         index_str = ""
#         for qarg in node_context.qargs:
#             index_str += str(node_orign.qargs.index(qarg))
#         print(index_str)
#         return index_str
    
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
        substituted_nodes = []
        for node in dag.two_qubit_ops():
            assert node.op.name == 'cx'
            if node in substituted_nodes:
                pass
            else:
                if node.op.name == 'cx':
                    #print((node.qargs[0].index, node.qargs[1].index), orientation_map[(node.qargs[0].index, node.qargs[1].index)])
                    #converting the datatype 'qubit' to the datatype 'int'
                    control = current_layout[node.qargs[0]]
                    target = current_layout[node.qargs[1]]
                    #set the orientation based on the orientation map
                    orientation = orientation_map[(control, target)]
                    predecessors = list(dag.quantum_predecessors(node))
                    successors = list(dag.quantum_successors(node))
                    flag = True
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
                                substituted_nodes.append(successor)
                                substituted_nodes.append(node)
                                flag = False
                                break
                    if flag == True:
                        #the CNOT has not been decomposed

                        variant_tag = ['11', '00', 'f']
                        if orientation == 'b':
                            variant_tag = ['00', '11', 'b']
                        variant_dag = UnrollCnotContextAware_.get_CNOT_variant_dag(variant_tag = tuple(variant_tag))
                        dag.substitute_node_with_dag(node, variant_dag)
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
    
    
class UnrollCnot_(TransformationPass):
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
                variant_tag = ['11', '00'] + [orientation]
                if orientation == 'b':
                    variant_tag = ['00', '11', 'b']
                variant_dag = UnrollCnot_.get_CNOT_variant_dag(variant_tag = tuple(variant_tag))
                dag.substitute_node_with_dag(node, variant_dag)
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
    
class SWAPContextAware_(TransformationPass):
    """change SWAP to bridge gate and perform context-aware decompose"""

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
            
#        orientation_map = self.orientation_map
        substituted_nodes = []
        for node in dag.two_qubit_ops():
            #assert node.op.name == 'cx'
            if node in substituted_nodes:
                pass
            else:
                if node.op.name == 'swap':
                    predecessors = list(dag.quantum_predecessors(node))
                    successors = list(dag.quantum_successors(node))
                    flag = True
                    for successor in successors:
                        if successor.name in {'swap', 'cx'}:
                            intersect = [value for value in node.qargs if value in successor.qargs]
                            print("intersect", intersect)
                            # check length
                            if len(intersect) == 2:
                                next_node_wire0 = dag.next_node_on_wire(node=node, wire = intersect[0])
                                next_node_wire1 = dag.next_node_on_wire(node=node, wire = intersect[1])
                                cond0 = next_node_wire0 is successor
                                cond1 = next_node_wire1 is successor
                                print("two intersection conditions", cond0, cond1)
                                #make sure there is only one CX between the intersection qargs.
                                if cond0 and next_node_wire1.op.name == 'cx' and dag.next_node_on_wire(node=next_node_wire1, wire = intersect[1]) is successor and next_node_wire1.qargs[0] == intersect[1]:
                                    print("bridge Gate10")
                                    dag.substitute_node(node, SWAP_Variant_Gate(variant_tag = ('10')))
                                    dag.substitute_node(successor, SWAP_Variant_Gate(variant_tag = ('10')))
                                    substituted_nodes += [node, successor]
                                elif cond1 and next_node_wire0.op.name == 'cx' and dag.next_node_on_wire(node=next_node_wire0, wire = intersect[0]) is successor and next_node_wire1.qargs[0] == intersect[0]:
                                    print("bridge Gate01")
                                    dag.substitute_node(node, SWAP_Variant_Gate(variant_tag = ('01')))
                                    dag.substitute_node(successor, SWAP_Variant_Gate(variant_tag = ('01')))
                                    substituted_nodes += [node, successor]
                                elif cond0 and cond1 and successor.name in {'cx'}:
                                    if intersect[0] == successor.qargs[0]:
                                        dag.substitute_node(node, SWAP_Variant_Gate(variant_tag = ('01')))
                                        substituted_nodes += [node]
                                    elif intersect[0] == successor.qargs[1]:
                                        dag.substitute_node(node, SWAP_Variant_Gate(variant_tag = ('10')))
                                        substituted_nodes += [node]
                                    else:
                                        raise AttributeError(f"incorrect qargs")
                    if node in substituted_nodes:
                        pass
                    else:
                        for predecessor in predecessors:
                            if predecessor.name in {'cx'}:
                                intersect = [value for value in node.qargs if value in predecessor.qargs]
                                print("intersect", intersect)
                                # check length
                                if len(intersect) == 2:
                                    next_node_wire0 = dag.next_node_on_wire(node=predecessor, wire = intersect[0])
                                    next_node_wire1 = dag.next_node_on_wire(node=predecessor, wire = intersect[1])
                                    cond0 = next_node_wire0 is node
                                    cond1 = next_node_wire1 is node
                                    print("two intersection conditions", cond0, cond1)
                                    if cond0 and cond1:
                                        if intersect[0] == predecessor.qargs[0]:
                                            dag.substitute_node(node, SWAP_Variant_Gate(variant_tag = ('01')))
                                            substituted_nodes += [node]
                                        elif intersect[0] == predecessor.qargs[1]:
                                            dag.substitute_node(node, SWAP_Variant_Gate(variant_tag = ('10')))
                                            substituted_nodes += [node]
                                        else:
                                            raise AttributeError(f"incorrect qargs")
                                    
        return dag
    
    @staticmethod
    def get_bridge_variant_dag(variant_tag = ('12', '01'), index_order = [0,1]):
        
        q = QuantumRegister(3, "q")
        qc = QuantumCircuit(q)
        
        try:
            rules = SWAPContextAware_.get_rules(q, variant_tag)
        except:
            raise AttributeError(f"Bridge Gate Variant_tag({variant_tag})not defined")

        for instr, qargs, cargs in rules:
            qc._append(instr, qargs, cargs)
        new_dag = circuit_to_dag(qc)
        return new_dag

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
    