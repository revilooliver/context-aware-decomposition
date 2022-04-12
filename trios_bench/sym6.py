import numpy as np
import qiskit


                 
def generate_sym6():


    c = qiskit.circuit.QuantumCircuit(10)
    c.ccx(0,1,6)
    c.cx(0,1)
    c.ccx(2,6,7)
    c.ccx(1,2,6)
    c.cx(1,2)
    c.ccx(3,7,8)
    c.ccx(3,6,7)
    c.ccx(2,3,6)
    c.cx(2,3)
    
    c.ccx(4,8,9)
    c.ccx(4,7,8)
    c.ccx(4,6,7)
    c.ccx(3,4,6)
    c.cx(3,4)
    
    c.ccx(5,8,9)
    c.ccx(5,7,8)
    c.ccx(4,5,6)
    c.cx(4,5)
    c.cx(6,9)
    c.cx(8,9)
    return c

