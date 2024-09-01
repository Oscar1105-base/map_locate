import time
from functools import lru_cache
from utils import total_distance


def dp_tsp(distmap):
    n = len(distmap)
    all_points_set = frozenset(range(n))

    @lru_cache(maxsize=None)
    def distance(current, remaining):
        if not remaining:
            return distmap[current][0], [current, 0]

        results = []
        for next_city in remaining:
            remaining_cities = remaining - frozenset([next_city])
            sub_path_dist, sub_path = distance(next_city, remaining_cities)
            total_dist = distmap[current][next_city] + sub_path_dist
            results.append((total_dist, [current] + sub_path))

        return min(results, key=lambda x: x[0])

    optimal_dist, optimal_path = distance(0, all_points_set - frozenset([0]))
    return optimal_path, optimal_dist


def run_dp(distmap):
    start_time = time.perf_counter()
    best_route, best_distance = dp_tsp(distmap)
    end_time = time.perf_counter()
    execution_time = (end_time - start_time) * 1000  # 轉換為毫秒

    # 使用 utils 中的 total_distance 函數來驗證結果
    calculated_distance = total_distance(best_route, distmap)
    return best_route, best_distance, execution_time
