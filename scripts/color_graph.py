import logging
import random
from collections import defaultdict, namedtuple
from itertools import product
from pathlib import Path
from time import time

import hydra
import numpy
import pandas as pd
from deap import base, creator, tools
from hydra.core.config_store import ConfigStore
from omegaconf import OmegaConf

from schedulebot.config import GeneticConfig
from schedulebot.genetic import elitism, graphs
from schedulebot.utils.date_generation import get_date_string
from schedulebot.utils.fs import load_graph, read_json
from schedulebot.utils.load import get_days, get_groups, get_time_intervals
from schedulebot.utils.viz import plot_fitness

CURRENT_DPATH = Path(__file__).parent.resolve()
PROJECT_DPATH = CURRENT_DPATH.parent
CONFIG_DPATH = PROJECT_DPATH / "configs"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__file__)

ScheduleSolution = namedtuple("ScheduleSolution", field_names=["gcp", "best_individual", "logbook"])
cfg_store = ConfigStore.instance()
cfg_store.store(name="genetic_config", node=GeneticConfig)


def generate_schedule(graph, config: GeneticConfig) -> ScheduleSolution:
    toolbox = base.Toolbox()

    max_colors = config.params.max_colors - 1

    # create the graph coloring problem instance to be used
    gcp = graphs.GraphColoringProblem(graph, config.params.hard_constraint_penalty)
    # define a single objective, minimizing fitness strategy
    creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
    # create the Individual class based on list:
    creator.create("Individual", list, fitness=creator.FitnessMin)
    # create an operator that randomly returns an integer in the range of participating colors
    toolbox.register("Integers", random.randint, 0, max_colors)
    # create the individual operator to fill up an Individual instance
    toolbox.register(
        "individualCreator", tools.initRepeat, creator.Individual, toolbox.Integers, len(gcp)
    )
    # create the population operator to generate a list of individuals:
    toolbox.register("populationCreator", tools.initRepeat, list, toolbox.individualCreator)

    # fitness calculation: cost of the suggested solution
    def get_cost(individual) -> tuple:
        # NOTE: return a tuple
        return (gcp.get_cost(individual),)

    toolbox.register("evaluate", get_cost)

    # genetic operators
    toolbox.register("select", tools.selTournament, tournsize=2)
    toolbox.register("mate", tools.cxTwoPoint)
    toolbox.register(
        "mutate",
        tools.mutUniformInt,
        low=0,
        up=max_colors,
        indpb=1.0 / len(gcp)
    )

    # create initial population (generation 0):
    population = toolbox.populationCreator(n=config.params.population_size)

    # prepare the statistics object:
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("min", numpy.min)
    stats.register("avg", numpy.mean)

    # define the hall-of-fame object:
    hof = tools.HallOfFame(config.params.hall_of_fame_size)

    start_ts = time()
    # perform the Genetic Algorithm flow with elitism:
    population, logbook = elitism.ea_simple_with_elitism(
        population,
        toolbox,
        cxpb=config.params.p_crossover,
        mutpb=config.params.p_mutation,
        ngen=config.params.max_generations,
        stats=stats,
        halloffame=hof,
        verbose=True
    )
    logger.info(f"Genetic algorithm is completed: {round(time() - start_ts, 3)} s")

    # print info for best solution found:
    best_individual = hof.items[0]
    logger.info(f"Best Individual: {best_individual}")
    logger.info(f"Best Fitness: {best_individual.fitness.values[0]}")
    logger.info(f"The number of colors: {gcp.get_color_number(best_individual)}")
    logger.info(f"The number of violations: {gcp.get_violations_count(best_individual)}")
    logger.info(f"The cost: {gcp.get_cost(best_individual)}")

    solution = ScheduleSolution(
        gcp=gcp,
        best_individual=best_individual,
        logbook=logbook
    )

    return solution


def convert_to_dataframe(best_individual, nodes) -> pd.DataFrame:
    day_names = get_days()
    # NOTE: the first and the last intervals are excluded
    time_intervals = get_time_intervals()[1:-1]

    day_time_intervals = list(map(" ".join, product(day_names, time_intervals)))
    day_time_map = dict(enumerate(day_time_intervals))

    schedule_dict = defaultdict(list)
    for color_idx, color in enumerate(best_individual):
        lesson_name = nodes[str(color_idx + 1)]
        schedule_dict[day_time_map[color]].append(lesson_name)

    # TODO: refactor
    schedule_groups = defaultdict(list, {name: [] for name in get_groups()})
    for lessons in schedule_dict.values():
        for group in schedule_groups:
            found = False
            for lesson in lessons:
                cropped_name = "".join(lesson.split(", ")[:3])
                if str(group) in lesson:
                    schedule_groups[group].append(cropped_name)
                    found = True
                    continue

            if not found:
                schedule_groups[group].append(None)

    schedule_df = pd.DataFrame(data=schedule_groups, index=list(schedule_dict.keys()))
    return schedule_df


def save_artifacts(save_dpath: Path, schedule_solution: ScheduleSolution, prefix: str):
    odd_graph_fig = schedule_solution.gcp.get_color_graph(
        schedule_solution.best_individual, figsize=(10, 10)
    )
    color_odd_graph_fpath = save_dpath / f"{prefix}_color_graph.jpg"
    odd_graph_fig.savefig(color_odd_graph_fpath)

    odd_fitness_fig = plot_fitness(
        schedule_solution.logbook.select("min"),
        schedule_solution.logbook.select("avg"),
    )
    odd_fitness_fpath = save_dpath / f"{prefix}_fitness.jpg"
    odd_fitness_fig.savefig(odd_fitness_fpath)


@hydra.main(config_name="color_graph", config_path=str(CONFIG_DPATH), version_base=None)
def main(config: GeneticConfig):
    OmegaConf.register_new_resolver("date_now", get_date_string)
    random.seed(config.params.random_seed)

    graph_dpath = Path(config.paths.graph_dpath)

    # --- Caching directory --- #
    save_dpath = Path(config.paths.output_dpath)
    save_dpath.mkdir(parents=True, exist_ok=True)

    # --- Odd week processing --- #
    odd_graph_fpath = graph_dpath / config.files.odd_graph
    odd_graph = load_graph(odd_graph_fpath)

    odd_nodes_fpath = graph_dpath / config.files.odd_graph_nodes
    odd_nodes = read_json(odd_nodes_fpath)

    odd_schedule_solution = generate_schedule(odd_graph, config)
    odd_schedule_df = convert_to_dataframe(odd_schedule_solution.best_individual, odd_nodes)
    save_artifacts(
        save_dpath=save_dpath,
        schedule_solution=odd_schedule_solution,
        prefix="odd"
    )

    # --- Even week processing --- #
    even_graph_fpath = graph_dpath / config.files.even_graph
    even_graph = load_graph(even_graph_fpath)

    even_nodes_fpath = graph_dpath / config.files.even_graph_nodes
    even_nodes = read_json(even_nodes_fpath)

    even_schedule_solution = generate_schedule(even_graph, config)
    even_schedule_df = convert_to_dataframe(even_schedule_solution.best_individual, even_nodes)
    save_artifacts(
        save_dpath=save_dpath,
        schedule_solution=even_schedule_solution,
        prefix="even"
    )

    # --- Schedule data frames caching --- #
    schedule_fpath = save_dpath / f"schedule_{get_date_string()}.xlsx"
    with pd.ExcelWriter(schedule_fpath) as writer:
        odd_schedule_df.to_excel(writer, sheet_name="Нечётная неделя", index=False)
        even_schedule_df.to_excel(writer, sheet_name="Чётная неделя", index=False)


if __name__ == "__main__":
    main()
