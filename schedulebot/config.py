from dataclasses import dataclass


@dataclass
class Paths:
    data_dpath: str
    graph_dpath: str
    output_dpath: str


@dataclass
class Files:
    odd_graph: str
    odd_graph_nodes: str
    even_graph: str
    even_graph_nodes: str


@dataclass
class Params:
    random_seed: int
    hard_constraint_penalty: float
    max_colors: int
    population_size: int
    hall_of_fame_size: int
    p_crossover: float
    p_mutation: float
    max_generations: int


@dataclass
class GeneticConfig:
    params: Params
    paths: Paths
    files: Files
