import numpy as np
import qiskit
"""reference:
https://reversiblebenchmarks.github.io/9symd2.html
"""
                 
def generate_sym9():


    c = qiskit.circuit.QuantumCircuit(12)
    c.ccx(0,1,9)
    c.cx(0,1)
    
    c.ccx(2,9,10)
    c.ccx(1,2,9)
    c.cx(1,2)
    
    c.ccx(3,10,11)
    c.ccx(3,9,10)
    c.ccx(2,3,9)
    c.cx(2,3)
    
    c.ccx(4,10,11)
    c.ccx(4,9,10)
    c.ccx(3,4,9)
    c.cx(3,4)
    
    c.ccx(5,10,11)
    c.ccx(5,9,10)
    c.ccx(4,5,9)
    c.cx(4,5)
    
    c.ccx(6,10,11)
    c.ccx(6,9,10)
    c.ccx(5,6,9)
    c.cx(5,6)
    
    c.ccx(7,10,11)
    c.ccx(7,9,10)
    c.ccx(6,7,9)
    c.cx(6,7)
    
    c.ccx(8,10,11)
    c.ccx(8,9,10)
    c.cx(10,11)
    return c

