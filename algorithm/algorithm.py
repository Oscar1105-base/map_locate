import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import psutil

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import create_output_directory, create_distmap, dsd_optimization, knn_with_two_opt
from ABC_Bee import run_abc
from SA_Annealing import run_sa
from Metaheuristic import run_hm
from DP_TSP import run_dp
from plotting import plot_results, plot_iterations_vs_distance, plot_hm_abc_comparison, plot_route


def save_results_to_file(
        dp_best_route, dp_best_distance, dp_execution_time, dp_memory_used,
        sa_best_route, sa_best_distance, sa_execution_time, sa_memory_used,
        abc_best_route, abc_best_distance, abc_execution_time, abc_memory_used,
        hm_best_route, hm_best_distance, hm_execution_time, hm_memory_used):
    """將計算結果保存到 output 目錄下的文件中"""
    output_dir = create_output_directory()
    result_file = os.path.join(output_dir, "algorithm_results.txt")

    with open(result_file, 'w', encoding="utf-8") as f:
        f.write(f'DP最終路徑: {dp_best_route}\n')
        f.write(f'DP最終距離: {dp_best_distance}\n')
        f.write(f'DP執行時間: {dp_execution_time:.2f} 毫秒\n')
        f.write(f'DP執行時間 (分秒): {milliseconds_to_minutes_seconds(dp_execution_time)}\n')
        f.write(f'DP內存使用: {dp_memory_used / 1024:.2f} KB\n')
        f.write(f'SA最終路徑: {sa_best_route}\n')
        f.write(f'SA最終距離: {sa_best_distance}\n')
        f.write(f'SA執行時間: {sa_execution_time:.2f} 毫秒\n')
        f.write(f'SA執行時間 (分秒): {milliseconds_to_minutes_seconds(sa_execution_time)}\n')
        f.write(f'SA內存使用: {sa_memory_used / 1024:.2f} KB\n')
        f.write(f'ABC最終路徑: {abc_best_route}\n')
        f.write(f'ABC最終距離: {abc_best_distance}\n')
        f.write(f'ABC執行時間: {abc_execution_time:.2f} 毫秒\n')
        f.write(f'ABC執行時間 (分秒): {milliseconds_to_minutes_seconds(abc_execution_time)}\n')
        f.write(f'ABC內存使用: {abc_memory_used / 1024:.2f} KB\n')
        f.write(f'HM最終路徑: {hm_best_route}\n')
        f.write(f'HM最終距離: {hm_best_distance}\n')
        f.write(f'HM執行時間: {hm_execution_time:.2f} 毫秒\n')
        f.write(f'HM執行時間 (分秒): {milliseconds_to_minutes_seconds(hm_execution_time)}\n')
        f.write(f'HM內存使用: {hm_memory_used / 1024:.2f} KB\n')

    print(f"算法計算結果已保存至: {result_file}")


def milliseconds_to_minutes_seconds(milliseconds):
    """將毫秒轉換為分鐘和秒的格式"""
    seconds = milliseconds / 1000
    minutes = int(seconds // 60)
    remaining_seconds = seconds % 60
    return f"{minutes}分 {remaining_seconds:.2f}秒"


def get_memory_usage():
    process = psutil.Process(os.getpid())
    return process.memory_info().rss


def save_results(
        dp_best_route, dp_best_distance, dp_execution_time, dp_memory_used,
        sa_best_route, sa_best_distance, sa_execution_time, sa_memory_used,
        abc_best_route, abc_best_distance, abc_execution_time, abc_memory_used,
        hm_best_route, hm_best_distance, hm_execution_time, hm_memory_used):
    with open('w', 'results.txt', encoding="utf-8") as f:
        f.write(f'DP最終路徑: {dp_best_route}\n')
        f.write(f'DP最終距離: {dp_best_distance}\n')
        f.write(f'DP執行時間: {dp_execution_time:.2f} 毫秒\n')
        f.write(f'DP執行時間 (分秒): {milliseconds_to_minutes_seconds(dp_execution_time)}\n')
        f.write(f'DP內存使用: {dp_memory_used / 1024:.2f} KB\n')
        f.write(f'SA最終路徑: {sa_best_route}\n')
        f.write(f'SA最終距離: {sa_best_distance}\n')
        f.write(f'SA執行時間: {sa_execution_time:.2f} 毫秒\n')
        f.write(f'SA執行時間 (分秒): {milliseconds_to_minutes_seconds(sa_execution_time)}\n')
        f.write(f'SA內存使用: {sa_memory_used / 1024:.2f} KB\n')
        f.write(f'ABC最終路徑: {abc_best_route}\n')
        f.write(f'ABC最終距離: {abc_best_distance}\n')
        f.write(f'ABC執行時間: {abc_execution_time:.2f} 毫秒\n')
        f.write(f'ABC執行時間 (分秒): {milliseconds_to_minutes_seconds(abc_execution_time)}\n')
        f.write(f'ABC內存使用: {abc_memory_used / 1024:.2f} KB\n')
        f.write(f'HM最終路徑: {hm_best_route}\n')
        f.write(f'HM最終距離: {hm_best_distance}\n')
        f.write(f'HM執行時間: {hm_execution_time:.2f} 毫秒\n')
        f.write(f'HM執行時間 (分秒): {milliseconds_to_minutes_seconds(hm_execution_time)}\n')
        f.write(f'HM內存使用: {hm_memory_used / 1024:.2f} KB\n')


def main():
    print("Algorithm execution completed successfully.")
    N = 10  # 城市數量
    distmap = create_distmap(N)
    distmap = distmap.astype(int)

    print("距離矩陣：(KM)")
    print("   ", end="")
    for i in range(N):
        print("{0:02d}".format(i), end=" ")
    print()
    for i in range(N):
        print(f"{i:2}", end=" ")

        for j in range(N):
            # print(f"{distmap[i][j]:3}", end=" ")
            print("{0:02d}".format(distmap[i][j]), end=" ")

        print()
    print('=' * 50)

    if N < 10:
        dsd_start_time = time.perf_counter()
        initial_route, initial_distance = dsd_optimization(distmap)
        dsd_end_time = time.perf_counter()
        print('DSD初始路徑:', [int(x) for x in initial_route])
        print('DSD初始距離:', initial_distance)

    else:
        knn_start_time = time.perf_counter()
        initial_route, initial_distance = knn_with_two_opt(distmap)
        knn_end_time = time.perf_counter()
        print('KNN+2-opt初始路徑:', [int(x) for x in initial_route])
        print('KNN+2-opt初始距離:', initial_distance)

    print('=' * 50)

    # 執行DP算法
    start_memory_dp = get_memory_usage()
    dp_best_route, dp_best_distance, dp_execution_time = run_dp(distmap)
    end_memory_dp = get_memory_usage()
    dp_memory_used = end_memory_dp - start_memory_dp

    with ThreadPoolExecutor(max_workers=3) as executor:
        sa_future = executor.submit(run_sa, distmap)
        abc_future = executor.submit(run_abc, distmap, 50, 1000)
        hm_future = executor.submit(run_hm, distmap, 50, 1000)

        sa_result = sa_future.result()
        abc_result = abc_future.result()
        hm_result = hm_future.result()

    sa_best_route, sa_best_distance, sa_best_iteration, sa_evetime_distance, sa_memory_used = sa_result
    abc_best_route, abc_best_distance, abc_evetime_distance, abc_best_iteration, abc_memory_used = abc_result
    hm_best_route, hm_best_distance, hm_evetime_distance, hm_best_iteration, hm_memory_used, hm_total_time = hm_result

    sa_best_time = sa_evetime_distance[sa_best_iteration][0] * 1000
    abc_best_time = abc_evetime_distance[abc_best_iteration][0] * 1000
    hm_best_time = hm_evetime_distance[hm_best_iteration][0] * 1000

    sa_execution_time = sa_evetime_distance[-1][0] * 1000
    abc_execution_time = abc_evetime_distance[-1][0] * 1000
    hm_execution_time = hm_evetime_distance[-1][0] * 1000

    print('DP最終路徑:', dp_best_route)
    print('DP最終距離:', dp_best_distance)
    print(f'DP執行時間: {dp_execution_time:.2f} 毫秒')
    print(f'DP執行時間 (分秒): {milliseconds_to_minutes_seconds(dp_execution_time)}')
    print(f'DP算法內存使用: {dp_memory_used / 1024:.2f} KB')
    print('=' * 50)
    print('SA最終路徑:', [int(x) for x in sa_best_route])
    print('SA最終距離:', sa_best_distance)
    print(f'SA得出最終距離的最少迭代次數: {sa_best_iteration}')
    print(f'SA算法得到最佳解時間: {sa_best_time:.2f} 毫秒')
    print(f'SA算法得到最佳解時間 (分秒): {milliseconds_to_minutes_seconds(sa_best_time)}')
    print(f'SA算法內存使用: {sa_memory_used / 1024:.2f} KB')
    print('=' * 50)
    print('ABC最終路徑:', abc_best_route)
    print('ABC最終距離:', abc_best_distance)
    print(f'ABC得出最終距離的最少迭代次數: {abc_best_iteration}')
    print(f'ABC算法得到最佳解時間: {abc_best_time:.2f} 毫秒')
    print(f'ABC算法得到最佳解時間 (分秒): {milliseconds_to_minutes_seconds(abc_best_time)}')
    print(f'ABC算法內存使用: {abc_memory_used / 1024:.2f} KB')
    print('=' * 50)
    print('HM最終路徑:', hm_best_route)
    print('HM最終距離:', hm_best_distance)
    print(f'HM得出最終距離的最少迭代次數: {hm_best_iteration}')
    print(f'HM算法得到最佳解時間: {hm_best_time:.2f} 毫秒')
    print(f'HM算法得到最佳解時間 (分秒): {milliseconds_to_minutes_seconds(hm_best_time)}')
    print(f'HM算法內存使用: {hm_memory_used / 1024:.2f} KB')
    print(f'HM算法總計算時間 (分秒): {milliseconds_to_minutes_seconds(hm_total_time * 1000)}')

    print('=' * 50)

    plot_hm_abc_comparison(hm_evetime_distance, abc_evetime_distance,
                           hm_best_distance, abc_best_distance,
                           hm_best_iteration, abc_best_iteration)

    plot_results(sa_evetime_distance, abc_evetime_distance, hm_evetime_distance,
                 sa_best_distance, abc_best_distance, hm_best_distance,
                 sa_best_iteration, abc_best_iteration, hm_best_iteration)

    plot_iterations_vs_distance(sa_evetime_distance, abc_evetime_distance, hm_evetime_distance,
                                sa_best_distance, abc_best_distance, hm_best_distance,
                                sa_best_iteration, abc_best_iteration, hm_best_iteration)

    # plot_route(distmap, dp_best_route, "DP算法最佳路径")
    plot_route(distmap, sa_best_route, "SA算法最佳路径")
    plot_route(distmap, abc_best_route, "ABC算法最佳路径")
    plot_route(distmap, hm_best_route, "HM算法最佳路径")

    save_results_to_file(
        dp_best_route, dp_best_distance, dp_execution_time, dp_memory_used,
        sa_best_route, sa_best_distance, sa_execution_time, sa_memory_used,
        abc_best_route, abc_best_distance, abc_execution_time, abc_memory_used,
        hm_best_route, hm_best_distance, hm_execution_time, hm_memory_used)


if __name__ == "__main__":
    main()
