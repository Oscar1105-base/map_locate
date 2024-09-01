import math
import random
import time
from utils import total_distance, dsd_optimization, get_memory_usage

# SA參數設置
SA_PARAMS = {
    't0': 100,  # 初始溫度
    'tmin': 0.1,  # 終止溫度
    'k': 70,  # 每個溫度下的迭代次數
    'coolnum': 0.98  # 冷卻係數
}


def inversion(route):
    copy = route.copy()
    i, j = random.sample(range(1, len(route) - 1), 2)
    copy[i], copy[j] = copy[j], copy[i]
    return copy


def simulated_annealing(route, distmap):
    t0 = SA_PARAMS['t0']
    tmin = SA_PARAMS['tmin']
    k = SA_PARAMS['k']
    coolnum = SA_PARAMS['coolnum']

    t = t0
    current_route = route
    current_distance = total_distance(current_route, distmap)
    best_route = current_route
    best_distance = current_distance
    iteration_count = 0
    best_iteration = 0

    evetime_distance = [(0, current_distance)]
    start_time = time.time()

    while t > tmin:
        for _ in range(k):
            iteration_count += 1
            new_route = inversion(current_route)
            new_distance = total_distance(new_route, distmap)
            diff = new_distance - current_distance

            if diff < 0 or random.random() < math.exp(-diff / t):
                current_route = new_route
                current_distance = new_distance

                if current_distance < best_distance:
                    best_route = current_route
                    best_distance = current_distance
                    best_iteration = iteration_count

            current_time = time.time() - start_time
            evetime_distance.append((current_time, current_distance))

        t *= coolnum

    return best_route, best_distance, best_iteration, evetime_distance


def run_sa(distmap):
    num_cities = len(distmap)
    initial_route, initial_distance = dsd_optimization(distmap)

    start_memory = get_memory_usage()

    best_route, best_distance, best_iteration, evetime_distance = simulated_annealing(initial_route, distmap)
    end_memory = get_memory_usage()
    memory_used = end_memory - start_memory

    return best_route, best_distance, best_iteration, evetime_distance, memory_used
