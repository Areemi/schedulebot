from typing import Tuple

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np


class GraphColoringProblem:
    """This class encapsulates the Graph Coloring problem
    """

    def __init__(self, graph, hard_constraint_penalty):
        self.graph = graph
        self.hard_constraint_penalty = hard_constraint_penalty

        self.node_list = list(self.graph.nodes)

        # adjacency matrix of the nodes -
        # matrix[i,j] equals '1' if nodes i and j are connected, or '0' otherwise:
        self.adj_matrix = nx.adjacency_matrix(graph).todense()

    def __len__(self) -> int:
        """Get the number of nodes in the graph."""

        return nx.number_of_nodes(self.graph)

    def get_cost(self, color_arrangement) -> float:
        """
        Calculates the cost of the suggested color arrangement
        :param colorArrangement: a list of integers representing the
        suggested color arrangement for the nodes,
        one color per node in the graph
        :return: Calculated cost of the arrangement.
        """
        penalty = self.hard_constraint_penalty
        violation_count = self.get_violations_count(color_arrangement)
        colors_number = self.get_color_number(color_arrangement)

        return (penalty * violation_count + colors_number)

    def get_violations_count(self, color_arrangement) -> int:
        """
        Calculates the number of violations in the given color arrangement.
        Each pair of interconnected nodes
        with the same color counts as one violation.
        :param colorArrangement: a list of integers representing the
        suggested color arrangement for the nodes,
        one color per node in the graph
        :return: the calculated value
        """

        if len(color_arrangement) != self.__len__():
            raise ValueError("size of color arrangement should be equal to ", self.__len__())

        violations = 0

        # iterate over every pair of nodes and find if they are adjacent AND share the same color:
        for i in range(len(color_arrangement)):
            for j in range(i + 1, len(color_arrangement)):

                if self.adj_matrix[i, j]:    # these are adjacent nodes
                    if color_arrangement[i] == color_arrangement[j]:
                        violations += 1

        return violations

    def get_color_number(self, color_arrangement):
        """
        returns the number of different colors in the suggested color arrangement
        :param colorArrangement: a list of integers representing the
        suggested color arrangement fpo the nodes,
        one color per node in the graph
        :return: number of different colors
        """
        return len(set(color_arrangement))

    def get_color_graph(self, color_arrangement, figsize: Tuple[int, int] = (10, 7)):
        """
        Plots the graph with the nodes colored according to the given color arrangement
        :param colorArrangement: a list of integers representing the
        suggested color arrangement fpo the nodes,
        one color per node in the graph
        """

        if len(color_arrangement) != self.__len__():
            raise ValueError(f"The size of color list should be equal to {self.__len__()}")

        # create a list of the unique colors in the arrangement:
        color_list = list(set(color_arrangement))

        # create the actual colors for the integers in the color list:
        colors = plt.cm.rainbow(np.linspace(0, 1, len(color_list)))

        # iterate over the nodes, and give each one of them its corresponding color:
        color_map = []
        for i in range(self.__len__()):
            color = colors[color_list.index(color_arrangement[i])]
            color_map.append(color)

        # plot the nodes with their labels and matching colors:
        graph_fig = plt.figure(figsize=figsize)
        nx.draw_kamada_kawai(self.graph, node_color=color_map, with_labels=True)

        return graph_fig.get_figure()
