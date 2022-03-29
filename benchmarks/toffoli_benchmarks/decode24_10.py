import qiskit
#benchmark from Revlib: http://www.informatik.uni-bremen.de/rev_lib/function_details.php?id=10
def generate_decode24_10():
    qc = qiskit.circuit.QuantumCircuit(4)
    qc.ccx(3,2,0)
    qc.cx(2,3)
    qc.ccx(3,2,1)
    qc.ccx(0,2,3)
    qc.cx(3,2)
    qc.x(3)
    return qc