import qiskit
#benchmark from Revlib: http://www.informatik.uni-bremen.de/rev_lib/function_details.php?id=9
def generate_alu_7_15():
    qc = qiskit.circuit.QuantumCircuit(5)
    qc.cx(4,3)
    qc.cx(1,2)
    qc.cx(2,4)
    qc.ccx(4,2,1)
    qc.cx(1,0)
    qc.ccx(0,3,1)
    qc.x(1)
    return qc