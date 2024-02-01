from typing import Tuple

import matplotlib.pyplot as plt


def plot_fitness(min_fitness, mean_fitness, figsize: Tuple[int, int] = (7, 5)):
    fig = plt.figure(figsize=figsize)

    plt.plot(min_fitness, color="red", label="min fitness")
    plt.plot(mean_fitness, color="green", label="avg fitness")
    plt.xlabel("Generation")
    plt.ylabel("Fitness Values")
    plt.title("Min and Average fitness over Generations")
    plt.grid(True)
    plt.legend()

    return fig
