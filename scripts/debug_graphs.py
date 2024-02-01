import json
import os
import pickle

import networkx as nx

from schedulebot.utils.load import (
    filling_the_graph,
    graph_edge_1week,
    graph_edge_2week,
    graph_nodes_1week,
    graph_nodes_2week,
)

CURRENT_DPATH = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DPATH, os.pardir))
DATA_DPATH = os.path.join(PROJECT_ROOT, "data")


def main():

    # --- Graph for 1 week --- #
    dictionary = graph_edge_1week()
    G = nx.Graph()
    G = filling_the_graph(dictionary, G)
    # gen_alg = GraphColoringProblem(G, 10)
    graph_path = os.path.join(DATA_DPATH, "graph")
    nodes_1week = graph_nodes_1week()
    fpath_json_edge_1 = os.path.join(graph_path, "1week_edge.json")
    fpath_json_node_1 = os.path.join(graph_path, "1week_node.json")
    with open(fpath_json_edge_1, 'w', encoding='utf-8') as outfile:
        json.dump(dictionary, outfile, ensure_ascii=False)
    with open(fpath_json_node_1, 'w', encoding='utf-8') as outfile:
        json.dump(nodes_1week, outfile, ensure_ascii=False)
    file_path_pickle_1 = os.path.join(graph_path, "1week.pickle")
    pickle.dump(G, open(file_path_pickle_1, 'wb'))
    # nx.write_gexf(G, file_path_1)

    # --- Graph for 2 week --- #
    dictionary = graph_edge_2week()
    H = nx.Graph()
    H = filling_the_graph(dictionary, H)
    nodes_2week = graph_nodes_2week()
    fpath_json_edge_2 = os.path.join(graph_path, "2week_edge.json")
    fpath_json_node_2 = os.path.join(graph_path, "2week_node.json")
    with open(fpath_json_edge_2, 'w', encoding='utf-8') as outfile:
        json.dump(dictionary, outfile, ensure_ascii=False)
    with open(fpath_json_node_2, 'w', encoding='utf-8') as outfile:
        json.dump(nodes_2week, outfile, ensure_ascii=False)
    file_path_pickle_2 = os.path.join(graph_path, "2week.pickle")
    pickle.dump(H, open(file_path_pickle_2, 'wb'))
    # nx.write_gexf(H, os.path.join(graph_path, "2week.gexf"))


if __name__ == "__main__":
    main()
