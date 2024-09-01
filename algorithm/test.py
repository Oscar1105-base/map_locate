import random
import time
import numpy as np
from Metaheuristic import run_hm
from utils import total_distance, knn_optimization, get_memory_usage


def knn_with_simulated_annealing(distmap, initial_temperature=1000, cooling_rate=0.995, max_iterations=1000):
    start_time = time.time()
    start_memory = get_memory_usage()

    # 獲取KNN初始解
    initial_route, initial_distance = knn_optimization(distmap)

    current_route = initial_route
    current_distance = initial_distance
    best_route = current_route
    best_distance = current_distance
    temperature = initial_temperature

    iterations = 0
    for iterations in range(max_iterations):
        # 生成鄰近解
        i, j = sorted(random.sample(range(1, len(current_route) - 1), 2))
        new_route = current_route[:i] + current_route[i:j + 1][::-1] + current_route[j + 1:]
        new_distance = total_distance(new_route, distmap)

        # 計算接受概率
        delta = new_distance - current_distance
        if delta < 0 or random.random() < np.exp(-delta / temperature):
            current_route = new_route
            current_distance = new_distance

            if current_distance < best_distance:
                best_route = current_route
                best_distance = current_distance

        # 降溫
        temperature *= cooling_rate

        # 如果溫度太低，提前結束
        if temperature < 0.01:
            break

    end_time = time.time()
    end_memory = get_memory_usage()

    total_time = end_time - start_time
    memory_used = end_memory - start_memory

    # 如果優化後的解不比初始解好,則返回初始解
    if best_distance >= initial_distance:
        return initial_route, initial_distance, total_time, iterations + 1, memory_used
    else:
        return best_route, best_distance, total_time, iterations + 1, memory_used


def compare_algorithms(distmap, num_runs=10):
    knn_sa_results = []
    hm_results = []

    for _ in range(num_runs):
        # KNN + 模擬退火
        knn_sa_route, knn_sa_distance, knn_sa_time, knn_sa_iterations, knn_sa_memory = knn_with_simulated_annealing(
            distmap)
        knn_sa_results.append((knn_sa_distance, knn_sa_time, knn_sa_iterations, knn_sa_memory))

        # 混合元啟發算法
        hm_route, hm_distance, _, hm_iterations, hm_memory, hm_time = run_hm(distmap)
        hm_results.append((hm_distance, hm_time, hm_iterations, hm_memory))

    print("KNN + Simulated Annealing:")
    print(f"Average distance: {np.mean([r[0] for r in knn_sa_results])}")
    print(f"Best distance: {min([r[0] for r in knn_sa_results])}")
    print(f"Worst distance: {max([r[0] for r in knn_sa_results])}")
    print(f"Average time: {np.mean([r[1] for r in knn_sa_results]):.2f} seconds")
    print(f"Average iterations: {np.mean([r[2] for r in knn_sa_results]):.0f}")
    print(f"Average memory usage: {np.mean([r[3] for r in knn_sa_results]) / (1024 * 1024):.2f} MB")

    print("\nHybrid Metaheuristic:")
    print(f"Average distance: {np.mean([r[0] for r in hm_results])}")
    print(f"Best distance: {min([r[0] for r in hm_results])}")
    print(f"Worst distance: {max([r[0] for r in hm_results])}")
    print(f"Average time: {np.mean([r[1] for r in hm_results]):.2f} seconds")
    print(f"Average iterations: {np.mean([r[2] for r in hm_results]):.0f}")
    print(f"Average memory usage: {np.mean([r[3] for r in hm_results]) / (1024 * 1024):.2f} MB")


# 使用示例
if __name__ == "__main__":
    # 假設我們有一個距離矩陣 distmap
    N = 10  # 城市數量
    distmap = np.random.randint(10, 100, size=(N, N))
    np.fill_diagonal(distmap, 0)
    distmap = (distmap + distmap.T) // 2  # 確保對稱性

    compare_algorithms(distmap)
