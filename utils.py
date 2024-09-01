import os
import random
import subprocess
import sys

import numpy as np
import psutil


def create_output_directory():
    if getattr(sys, 'frozen', False):
        # 如果是打包後的 exe
        base_path = sys._MEIPASS
    else:
        # 如果是直接運行 Python 腳本
        output_dir = os.path.join(os.path.dirname(__file__), "output")

    os.makedirs(output_dir, exist_ok=True)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    return output_dir


def run_openmap():
    # 获取 main.py 所在的目录
    if getattr(sys, 'frozen', False):
        # 如果是打包后的 exe
        base_path = sys._MEIPASS
    else:
        # 如果是直接运行 Python 脚本
        base_path = os.path.dirname(os.path.abspath(__file__))

    # 构建 openmap.py 的绝对路径
    openmap_path = os.path.join(base_path, "map", "openmap.py")

    # 构建输出 HTML 文件的路径
    output_dir = os.path.join(base_path, "output")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    html_file = "map_with_nearby_places_osm.html"
    html_path = os.path.join(output_dir, html_file)

    # 执行 openmap.py 脚本
    result = subprocess.run(["python", openmap_path], capture_output=True, text=True, encoding="utf-8")
    print(result.stdout)

    # 检查是否生成了 HTML 文件
    if os.path.exists(html_path):
        print(f"地图已生成并保存至: '{html_path}'")
    else:
        print("错误: HTML 文件未能成功创建")


def get_memory_usage():
    process = psutil.Process(os.getpid())
    return process.memory_info().rss


def total_distance(route, distmap):
    return sum(distmap[int(route[i]), int(route[i + 1])] for i in range(len(route) - 1))


def create_distmap(N):
    distmap = np.zeros((N, N))
    for i in range(N):
        for j in range(i, N):
            if i < j:
                distmap[i][j] = random.randint(10, 50)
                distmap[j][i] = distmap[i][j]
    return distmap


# DSD
def create_dsd_matrix(n_cities):
    dsd = np.zeros((2 * n_cities + 1, n_cities))
    for i in range(n_cities):
        dsd[2 * i, i] = -1
        dsd[2 * i + 1, i] = 1
    dsd[-1, :] = 0
    return dsd


def generate_route_from_dsd(row):
    order = np.argsort(row)
    route = [int(i) for i in order] + [int(order[0])]
    return route


def dsd_optimization(distmap):
    n_cities = len(distmap)
    dsd_matrix = create_dsd_matrix(n_cities)
    routes = [generate_route_from_dsd(row) for row in dsd_matrix]
    distances = [total_distance(route, distmap) for route in routes]
    best_index = np.argmin(distances)
    return routes[best_index], distances[best_index]


def generate_neighbor(solution):
    neighbor = solution.copy()
    i, j = random.sample(range(1, len(solution) - 1), 2)
    neighbor[i], neighbor[j] = neighbor[j], neighbor[i]
    return neighbor


# K近鄰
def knn_optimization(distmap):
    n_cities = len(distmap)
    unvisited = set(range(n_cities))
    route = [0]  # 從城市0開始
    unvisited.remove(0)

    while unvisited:
        last = route[-1]
        next_city = min(unvisited, key=lambda x: distmap[int(last)][int(x)])
        route.append(int(next_city))
        unvisited.remove(next_city)

    route.append(0)  # 回到起點
    distance = total_distance(route, distmap)
    return route, distance


def two_opt_swap(route, i, k):
    new_route = route[:i] + route[i:k + 1][::-1] + route[k + 1:]
    return [int(city) for city in new_route]


def two_opt(route, distmap):
    best = route
    improved = True
    while improved:
        improved = False
        for i in range(1, len(route) - 2):
            for k in range(i + 1, len(route) - 1):
                new_route = two_opt_swap(route, i, k)
                if total_distance(new_route, distmap) < total_distance(best, distmap):
                    best = new_route
                    improved = True
        route = best
    return best, total_distance(best, distmap)


def knn_with_two_opt(distmap):
    initial_route, initial_distance = knn_optimization(distmap)
    optimized_route, optimized_distance = two_opt(initial_route, distmap)
    return optimized_route, optimized_distance
