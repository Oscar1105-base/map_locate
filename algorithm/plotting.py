import io
import sys
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Slider

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


def plot_results(sa_evetime_distance, abc_evetime_distance, hm_evetime_distance,
                 sa_best_distance, abc_best_distance, hm_best_distance,
                 sa_best_iteration, abc_best_iteration, hm_best_iteration):
    plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']
    plt.rcParams['axes.unicode_minus'] = False

    fig, ax = plt.subplots(figsize=(15, 8))
    plt.subplots_adjust(bottom=0.2)

    sa_times, sa_distances = zip(*sa_evetime_distance)
    abc_times, abc_distances = zip(*abc_evetime_distance)
    hm_times, hm_distances = zip(*hm_evetime_distance)

    # 將時間單位從秒轉換為毫秒
    sa_times = [t * 1000 for t in sa_times]
    abc_times = [t * 1000 for t in abc_times]
    hm_times = [t * 1000 for t in hm_times]

    sa_line, = ax.plot(sa_times, sa_distances, linewidth=2.5, label="SA演算法", color='r')
    abc_line, = ax.plot(abc_times, abc_distances, linewidth=2.5, label="ABC演算法", color='b')
    hm_line, = ax.plot(hm_times, hm_distances, linewidth=2.5, label="HM演算法", color='g')

    ax.set_xlabel("計算時間 (毫秒)", fontsize=15)
    ax.set_ylabel("路徑長度", fontsize=15)
    ax.legend()

    # 标记最佳解的位置
    sa_best_time = sa_times[sa_best_iteration]
    abc_best_time = abc_times[abc_best_iteration]
    hm_best_time = hm_times[hm_best_iteration]

    ax.annotate(f'SA最佳解\n時間: {sa_best_time:.2f}ms\n距離: {sa_best_distance:.2f}',
                xy=(sa_best_time, sa_best_distance), xytext=(10, 10),
                textcoords='offset points', ha='left', va='bottom',
                bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.5),
                arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))

    ax.annotate(f'ABC最佳解\n时间: {abc_best_time:.2f}ms\n距離: {abc_best_distance:.2f}',
                xy=(abc_best_time, abc_best_distance), xytext=(10, -10),
                textcoords='offset points', ha='left', va='top',
                bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.5),
                arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))

    ax.annotate(f'HM最佳解\n时间: {hm_best_time:.2f}ms\n距離: {hm_best_distance:.2f}',
                xy=(hm_best_time, hm_best_distance), xytext=(-10, 0),
                textcoords='offset points', ha='right', va='center',
                bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.5),
                arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))

    plt.title("SA、ABC和HM性能比較", fontsize=20)
    plt.grid(True)

    # 添加滑块
    axcolor = 'lightgoldenrodyellow'
    ax_slider = plt.axes([0.1, 0.1, 0.8, 0.03], facecolor=axcolor)
    max_time = max(max(sa_times), max(abc_times), max(hm_times))
    slider = Slider(ax_slider, '起始時間', 0, max_time - 100, valinit=0, valstep=10)

    def update(val):
        pos = slider.val
        ax.set_xlim(pos, pos + 50)
        fig.canvas.draw_idle()

    slider.on_changed(update)

    # 初始显示前100毫秒的数据
    ax.set_xlim(0, 100)

    plt.show()


def plot_iterations_vs_distance(sa_evetime_distance, abc_evetime_distance, hm_evetime_distance,
                                sa_best_distance, abc_best_distance, hm_best_distance,
                                sa_best_iteration, abc_best_iteration, hm_best_iteration):
    plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']
    plt.rcParams['axes.unicode_minus'] = False

    fig, ax = plt.subplots(figsize=(15, 8))

    sa_iterations = list(range(len(sa_evetime_distance)))
    abc_iterations = list(range(len(abc_evetime_distance)))
    hm_iterations = list(range(len(hm_evetime_distance)))

    _, sa_distances = zip(*sa_evetime_distance)
    _, abc_distances = zip(*abc_evetime_distance)
    _, hm_distances = zip(*hm_evetime_distance)

    sa_line, = ax.plot(sa_iterations, sa_distances, linewidth=2.5, label="SA算法", color='r')
    abc_line, = ax.plot(abc_iterations, abc_distances, linewidth=2.5, label="ABC算法", color='b')
    hm_line, = ax.plot(hm_iterations, hm_distances, linewidth=2.5, label="HM算法", color='g')

    ax.set_xlabel("迭代次數", fontsize=15)
    ax.set_ylabel("路徑長度", fontsize=15)
    ax.legend()

    ax.annotate(f'SA最佳解\n迭代次數: {sa_best_iteration}\n距離: {sa_best_distance:.2f}',
                xy=(sa_best_iteration, sa_best_distance), xytext=(10, 10),
                textcoords='offset points', ha='left', va='bottom',
                bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.5),
                arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))

    ax.annotate(f'ABC最佳解\n迭代次數: {abc_best_iteration}\n距離: {abc_best_distance:.2f}',
                xy=(abc_best_iteration, abc_best_distance), xytext=(10, -10),
                textcoords='offset points', ha='left', va='top',
                bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.5),
                arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))

    ax.annotate(f'HM最佳解\n迭代次數: {hm_best_iteration}\n距離: {hm_best_distance:.2f}',
                xy=(hm_best_iteration, hm_best_distance), xytext=(-10, 0),
                textcoords='offset points', ha='right', va='center',
                bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.5),
                arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))

    plt.title("SA、ABC和HM算法迭代次數與路徑長度關係", fontsize=20)
    plt.grid(True)

    plt.show()


def plot_route(distmap, route, title):
    n = len(distmap)
    coords = np.random.rand(n, 2)  # 隨機生成城市坐標

    plt.figure(figsize=(10, 10))
    plt.scatter(coords[:, 0], coords[:, 1], s=200, c='red')

    for i, city in enumerate(coords):
        plt.annotate(f'城市{i}', (city[0], city[1]), xytext=(5, 5), textcoords='offset points')

    for i in range(len(route)):
        start = coords[route[i]]
        end = coords[route[(i + 1) % len(route)]]
        plt.plot([start[0], end[0]], [start[1], end[1]], 'b-')

    plt.title(title)
    plt.xlabel('X座標')
    plt.ylabel('Y座標')
    plt.grid(True)
    plt.show()


def plot_hm_abc_comparison(hm_evetime_distance, abc_evetime_distance, hm_best_distance, abc_best_distance,
                           hm_best_iteration, abc_best_iteration):
    plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']
    plt.rcParams['axes.unicode_minus'] = False

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 16))
    plt.subplots_adjust(bottom=0.1, hspace=0.3)

    # 時間軸圖
    hm_times, hm_distances = zip(*hm_evetime_distance)
    abc_times, abc_distances = zip(*abc_evetime_distance)

    hm_times = [t * 1000 for t in hm_times]  # 轉換為毫秒
    abc_times = [t * 1000 for t in abc_times]

    hm_line, = ax1.plot(hm_times, hm_distances, linewidth=2.5, label="HM算法", color='g')
    abc_line, = ax1.plot(abc_times, abc_distances, linewidth=2.5, label="ABC算法", color='b')

    ax1.set_xlabel("計算時間 (毫秒)", fontsize=12)
    ax1.set_ylabel("路徑長度", fontsize=12)
    ax1.legend()
    ax1.set_title("HM和ABC算法時間軸比較", fontsize=16)
    ax1.grid(True)

    # 迭代圖
    hm_iterations = list(range(len(hm_evetime_distance)))
    abc_iterations = list(range(len(abc_evetime_distance)))

    hm_iter_line, = ax2.plot(hm_iterations, hm_distances, linewidth=2.5, label="HM算法", color='g')
    abc_iter_line, = ax2.plot(abc_iterations, abc_distances, linewidth=2.5, label="ABC算法", color='b')

    ax2.set_xlabel("迭代次數", fontsize=12)
    ax2.set_ylabel("路徑長度", fontsize=12)
    ax2.legend()
    ax2.set_title("HM和ABC算法迭代比較H", fontsize=16)
    ax2.grid(True)

    # 添加最佳解標記
    hm_best_time = hm_times[hm_best_iteration]
    abc_best_time = abc_times[abc_best_iteration]

    ax1.annotate(f'HM最佳解\n時間: {hm_best_time:.2f}ms\n距離: {hm_best_distance:.2f}',
                 xy=(hm_best_time, hm_best_distance), xytext=(10, 10),
                 textcoords='offset points', ha='left', va='bottom',
                 bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.5),
                 arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))

    ax1.annotate(f'ABC最佳解\n時間: {abc_best_time:.2f}ms\n距離: {abc_best_distance:.2f}',
                 xy=(abc_best_time, abc_best_distance), xytext=(10, -10),
                 textcoords='offset points', ha='left', va='top',
                 bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.5),
                 arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))

    ax2.annotate(f'HM最佳解\n迭代: {hm_best_iteration}\n距離: {hm_best_distance:.2f}',
                 xy=(hm_best_iteration, hm_best_distance), xytext=(10, 10),
                 textcoords='offset points', ha='left', va='bottom',
                 bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.5),
                 arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))

    ax2.annotate(f'ABC最佳解\n迭代: {abc_best_iteration}\n距離: {abc_best_distance:.2f}',
                 xy=(abc_best_iteration, abc_best_distance), xytext=(10, -10),
                 textcoords='offset points', ha='left', va='top',
                 bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.5),
                 arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))

    # 添加滾軸
    axcolor = 'lightgoldenrodyellow'
    ax_slider_time = plt.axes([0.1, 0.06, 0.8, 0.03], facecolor=axcolor)
    ax_slider_iter = plt.axes([0.1, 0.02, 0.8, 0.03], facecolor=axcolor)

    max_time = max(max(hm_times), max(abc_times))
    max_iter = max(len(hm_iterations), len(abc_iterations))
    slider_iter = Slider(ax_slider_iter, '迭代範圍', 0, max_iter, valinit=0, valstep=max_iter / 100)

    slider_time = Slider(ax_slider_time, '時間範圍', 0, max_time, valinit=0, valstep=max_time / 100)

    def update_time(val):
        pos = slider_time.val
        ax1.set_xlim(pos, pos + max_time / 10)
        fig.canvas.draw_idle()

    def update_iter(val):
        pos = slider_iter.val
        ax2.set_xlim(pos, pos + max_iter / 10)
        fig.canvas.draw_idle()

    slider_iter.on_changed(update_iter)
    slider_time.on_changed(update_time)

    # 初始顯示範圍
    ax1.set_xlim(0, max_time / 10)
    ax2.set_xlim(0, max_iter / 10)
    plt.show()
