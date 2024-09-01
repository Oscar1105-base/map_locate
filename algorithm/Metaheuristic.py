import random
import time
from utils import total_distance, get_memory_usage


def greedy_solution(distmap, start_city):
    num_cities = len(distmap)
    unvisited = set(range(num_cities))
    unvisited.remove(start_city)
    tour = [start_city]

    while unvisited:
        last = tour[-1]
        next_city = min(unvisited, key=lambda x: distmap[last][x])
        tour.append(next_city)
        unvisited.remove(next_city)

    tour.append(start_city)
    return tour


def multi_start_greedy(distmap, num_starts):
    solutions = [greedy_solution(distmap, i) for i in range(num_starts)]
    return sorted(solutions, key=lambda x: total_distance(x, distmap))


def generate_neighbor(solution):
    neighbor = solution.copy()
    size = len(solution)
    i, j = sorted(random.sample(range(1, size - 1), 2))
    neighbor[i:j + 1] = reversed(neighbor[i:j + 1])
    return neighbor


def rank_bees(food_sources, distmap):
    fitnesses = [1 / (1 + total_distance(source, distmap)) for source in food_sources]
    ranked_bees = sorted(range(len(fitnesses)), key=lambda k: fitnesses[k], reverse=True)
    return ranked_bees


def differential_mutation(food_sources, current_index, ranked_bees, distmap):
    candidates = [i for i in range(len(food_sources)) if i != current_index]
    weights = [1 / (rank + 1) for rank in range(len(candidates))]
    r1, r2, r3 = random.choices(candidates, weights=weights, k=3)

    mutant = food_sources[current_index].copy()
    num_cities = len(distmap)

    swap_count = max(2, int(0.1 * num_cities))
    swap_indices = random.sample(range(1, num_cities - 1), swap_count)

    for i in swap_indices:
        if random.random() < 0.5:
            j = random.choice(swap_indices)
            mutant[i], mutant[j] = mutant[j], mutant[i]

    return mutant


def local_search(solution, distmap, max_iterations=100):
    best_solution = solution
    best_distance = total_distance(solution, distmap)

    for _ in range(max_iterations):
        improved = False
        for i in range(1, len(solution) - 2):
            for j in range(i + 1, min(i + 20, len(solution) - 1)):
                delta = calculate_2opt_delta(solution, distmap, i, j)
                if delta < 0:
                    best_solution = solution[:i] + solution[i:j][::-1] + solution[j:]
                    best_distance += delta
                    improved = True
                    break
            if improved:
                break
        if not improved:
            break

    return best_solution


def calculate_2opt_delta(solution, distmap, i, j):
    a, b = solution[i - 1], solution[i]
    c, d = solution[j], solution[j + 1]
    return (distmap[a][c] + distmap[b][d]) - (distmap[a][b] + distmap[c][d])


def Hybrid_Metaheuristic_algorithm(distmap, colony_size, max_iterations, initial_solutions):
    num_cities = len(distmap)
    elite_size = min(len(initial_solutions), max(2, int(0.05 * colony_size)))

    food_sources = initial_solutions[:elite_size]

    for _ in range(colony_size - elite_size):
        new_solution = list(range(num_cities)) + [0]
        random.shuffle(new_solution[1:-1])
        food_sources.append(new_solution)

    best_solution = min(food_sources, key=lambda x: total_distance(x, distmap))
    best_distance = total_distance(best_solution, distmap)

    iteration_distances = [(0, best_distance)]
    start_time = time.time()

    best_iteration = 0
    stagnation_counter = 0

    for iteration in range(max_iterations):
        ranked_bees = rank_bees(food_sources, distmap)

        # 第一階段：差分進化
        for i in range(colony_size):
            mutant = differential_mutation(food_sources, i, ranked_bees, distmap)
            if total_distance(mutant, distmap) < total_distance(food_sources[i], distmap):
                food_sources[i] = mutant

        # 第二階段：近鄰搜索
        for i in range(colony_size):
            neighbor = generate_neighbor(food_sources[i])
            if total_distance(neighbor, distmap) < total_distance(food_sources[i], distmap):
                food_sources[i] = neighbor

        # 淘汰和重新初始化
        fitnesses = [1 / (1 + total_distance(source, distmap)) for source in food_sources]
        total_fitness = sum(fitnesses)
        probabilities = [fit / total_fitness for fit in fitnesses]

        for i in range(colony_size):
            if i in ranked_bees[colony_size // 2:]:
                if random.random() < 0.2:
                    food_sources[i] = list(range(num_cities)) + [0]
                    random.shuffle(food_sources[i][1:-1])

        current_best = min(food_sources, key=lambda x: total_distance(x, distmap))
        current_best_distance = total_distance(current_best, distmap)
        if current_best_distance < best_distance:
            best_solution = current_best
            best_distance = current_best_distance
            best_iteration = iteration + 1
            stagnation_counter = 0
        else:
            stagnation_counter += 1

        # 定期進行局部搜索
        if iteration % 100 == 0 or (iteration > max_iterations * 0.8 and iteration % 10 == 0):
            best_solution = local_search(best_solution, distmap)
            best_distance = total_distance(best_solution, distmap)

        # 保留精英解
        elite_size = max(2, int(0.05 * colony_size))
        food_sources = sorted(food_sources, key=lambda x: total_distance(x, distmap))
        food_sources[-elite_size:] = food_sources[:elite_size]

        current_time = time.time() - start_time
        iteration_distances.append((current_time, best_distance))

    return best_solution, best_distance, iteration_distances, best_iteration


def run_hm(distmap, colony_size=None, max_iterations=None):
    start_time = time.time()  # 開始計時

    num_cities = len(distmap)

    if colony_size is None:
        colony_size = min(50, max(20, num_cities // 2))
    if max_iterations is None:
        max_iterations = min(5000, max(1000, num_cities * 20))

    num_starts = min(num_cities, 20)
    initial_solutions = multi_start_greedy(distmap, num_starts)

    start_memory = get_memory_usage()
    best_solution, best_distance, iteration_distances, best_iteration = Hybrid_Metaheuristic_algorithm(
        distmap, colony_size, max_iterations, initial_solutions)
    end_memory = get_memory_usage()
    memory_used = end_memory - start_memory

    best_solution = [int(x) for x in best_solution]

    end_time = time.time()  # 結束計時
    total_time = end_time - start_time  # 計算總執行時間

    return best_solution, best_distance, iteration_distances, best_iteration, memory_used, total_time
