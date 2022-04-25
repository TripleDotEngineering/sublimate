 
import sys 
sys.path.append('..')

import pytest
from sublimate.sublimate import Network
import networkx as nx
import json
import math
 
def test_disconnected_graph():
    with open('tests/disconnected_graph.json', 'r') as f:
        data = f.read()
    network = Network(data, ['212.209.235.224'], '135.22.112.220', {'diagramName': 'disconnected_graph'})
    network.Sublimate(2)
    assert len(network.victimNodes[0].compromisePaths) == 0
 
 
def complete_graph(n):
    G = nx.Graph()
    for i in range(n):
        G.add_node(str(i), distill_score=0.9, id=str(i), ip=str(i))
        for j in range(i):
            G.add_edge(str(i), str(j))
    return G

def test_complete_3_graph():
    size = 3
    expected_value = math.floor(math.e * math.factorial(size-2))
    graph = complete_graph(size)
    data = json.dumps(nx.readwrite.node_link_data(graph))
    network = Network(data, ['0'], '1', {'diagramName': 'disconnected_graph'})
    network.Sublimate(math.factorial(size))
    assert len(network.victimNodes[0].compromisePaths) == expected_value


def test_complete_graphs():
    for size in range(4, 7):
        expected_value = math.floor(math.e * math.factorial(size-2))
        graph = complete_graph(size)
        data = json.dumps(nx.readwrite.node_link_data(graph))
        network = Network(data, ['0'], '1', {'diagramName': 'disconnected_graph'})
        network.Sublimate(math.factorial(size))
        assert len(network.victimNodes[0].compromisePaths) == expected_value

 
def test_find_0_paths():
    with open('tests/demo_graph.json', 'r') as f:
        data = f.read()
    network = Network(data, ['212.209.235.224'], '135.22.112.220', {'diagramName': 'demo_graph'})
    network.Sublimate(0)
    assert len(network.victimNodes[0].compromisePaths) == 0

def test_demo_graph():
    with open('tests/demo_graph.json', 'r') as f:
        data = f.read()
    network = Network(data, ['212.209.235.224'], '135.22.112.220', {'diagramName': 'demo_graph'})
    network.Sublimate(3)
    paths = network.victimNodes[0].compromisePaths
    print(paths[0].weight)
    print(paths[1].weight)
    print(paths[2].weight)

    assert (len(paths) == 3 
        and math.isclose(paths[0].weight, 1)
        and math.isclose(paths[1].weight, 0.22948468672526573)
        and math.isclose(paths[0].weight, 1))
