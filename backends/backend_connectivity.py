"""Customizable Backend Connectivity"""

import numpy as np
import networkx as nx

def star(nbits = 4, bidirectional_link = True):
    """
        Return a coupling map for the STAR shape connectivity. For an n-qubit star shape connectivity, only one qubit
        is connected with the other n-1 qubits
    """
    coupling_map = []
    if nbits == 0:
        return []
    else:
        for i in range(1, nbits):
            coupling_map.append([0,i])
            if bidirectional_link is True:
                coupling_map.append([i,0])
        return coupling_map

def LNN(nbits = 4, bidirectional_link = True):
    """
        Return a coupling map for the Linear Nearest Neighbour(LNN) shape connectivity. An n-qubit LNN shape connectivity
        corresponds to a graph of a line with n vertices and an edge between each pair of neighbouring vertices.
    """
    coupling_map = []
    if nbits == 0:
        return []
    else:
        for i in range(0, nbits-1):
            coupling_map.append([i, i + 1])
            if bidirectional_link is True:
                coupling_map.append([i + 1, i])
        return coupling_map

def cycle(nbits = 4, bidirectional_link = True):
    """
        Return a coupling map for the cycle shape connectivity. A cycle shape connectivity
        corresponds to a LNN shape graph with one extra edge connecting the first vertice and the last vertice
    """
    coupling_map = []
    if nbits == 0:
        return []
    else:
        for i in range(0, nbits-1):
            coupling_map.append([i, i + 1])
            if bidirectional_link is True:
                coupling_map.append([i + 1,i])
        coupling_map.append([0, nbits-1])
        if bidirectional_link is True:
            coupling_map.append([nbits-1, 0])
        return coupling_map

def twoDSL(nbits = 16, width = 4, bidirectional_link = True):
    """
        Return a coupling map for the 2DSL shape connectivity.
        nbits specifies the total number of nodes, width specifies the maximum width.
    """
    coupling_map = []
    if nbits == 0:
        return []
    else:
        for i in range(nbits):
            right, bottom = edge_check(i, nbits, width)
            if right is False:
                coupling_map.append([i, i + 1])
                if bidirectional_link is True:
                    coupling_map.append([i + 1, i])
            if bottom is False:
                coupling_map.append([i, i + width])
                if bidirectional_link is True:
                    coupling_map.append([i + width, i])
        return coupling_map


def edge_check(i, nbits, width):
    """
         Edge_checking function for 2DSL shape connectivity, returns Ture and Ture if the node is the right most and the bottom most node.
     """
    right = False
    bottom = False
    if i > nbits - 1:
        raise ValueError("ERROR: id greater than the total number of nodes")
    # check if it is the right most node
    if (i + 1) % width == 0 or i == nbits - 1:
        right = True

    max_row = int(nbits / width)
    condition1 = int(i / width) == max_row
    condition2 = int((i + width) / width) == max_row and i + width >= nbits
    # check if it is the bottom most node
    if condition1 or condition2:
        bottom = True
    return right, bottom


def cluster(k_inner, k_outer):
    coupling_map = []
    qid = 0
    for i in range(0, k_inner):
        for j in range(0, k_outer):
            qid = k_outer * i + j
            for j2 in range(0, k_outer):
                if j != j2:
                    coupling_map.append([qid, k_outer * i + j2])
                
        for i2 in range(0, k_inner):
            if i != i2:
                coupling_map.append([i*k_outer, i2*k_outer])

    return coupling_map

    
def couplingmap_to_graph(couplingmap, Draw = False):
    graph = nx.Graph()
    graph.add_edges_from(couplingmap)
    if Draw is True:
        nx.draw_networkx(graph)
    return graph

def orientation_from_coupling(couplingmap):
    orientation_map = {}
    for link in couplingmap:
        if link[0] > link[1]:
            orientation_map[tuple(link)] = 'f'
        elif link[0] < link[1]:
            orientation_map[tuple(link)] = 'b'
        else:
            print("error, incorrect couplingmap")
    return orientation_map
    