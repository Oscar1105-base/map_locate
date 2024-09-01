import random
import time
from utils import total_distance, generate_neighbor, get_memory_usage, dsd_optimization


def abc_algorithm(distmap, colony_size, max_iterations):
    num_cities = len(distmap)

    food_sources = [list(range(num_cities)) + [0] for _ in range(colony_size)]
    for source in food_sources:
        random.shuffle(source[1:-1])

    best_solution = min(food_sources, key=lambda x: total_distance(x, distmap))
    best_distance = total_distance(best_solution, distmap)

    iteration_distances = [(0, best_distance)]
    start_time = time.time()

    best_iteration = 0

    for iteration in range(max_iterations):
        # Employed Bees Phase
        for i in range(colony_size):
            neighbor = generate_neighbor(food_sources[i])
            if total_distance(neighbor, distmap) < total_distance(food_sources[i], distmap):
                food_sources[i] = neighbor

        # Onlooker Bees Phase
        fitnesses = [1 / (1 + total_distance(source, distmap)) for source in food_sources]
        total_fitness = sum(fitnesses)
        probabilities = [fit / total_fitness for fit in fitnesses]

        for _ in range(colony_size):
            selected = random.choices(range(colony_size), probabilities)[0]
            neighbor = generate_neighbor(food_sources[selected])
            if total_distance(neighbor, distmap) < total_distance(food_sources[selected], distmap):
                food_sources[selected] = neighbor

        # Scout Bees Phase
        for i in range(colony_size):
            if random.random() < 0.1:  # 10% chance of reset
                food_sources[i] = list(range(num_cities)) + [0]
                random.shuffle(food_sources[i][1:-1])

        # Update best solution
        current_best = min(food_sources, key=lambda x: total_distance(x, distmap))
        current_best_distance = total_distance(current_best, distmap)
        if current_best_distance < best_distance:
            best_solution = current_best
            best_distance = current_best_distance
            best_iteration = iteration + 1

        current_time = time.time() - start_time
        iteration_distances.append((current_time, best_distance))

    return best_solution, best_distance, iteration_distances, best_iteration


def run_abc(distmap, colony_size=100, max_iterations=1000):
    initial_memory = get_memory_usage()

    initial_solution, initial_distance = dsd_optimization(distmap)

    best_solution, best_distance, iteration_distances, best_iteration = abc_algorithm(distmap, colony_size,
                                                                                      max_iterations)

    final_memory = get_memory_usage()
    memory_used = final_memory - initial_memory

    return best_solution, best_distance, iteration_distances, best_iteration, memory_used
