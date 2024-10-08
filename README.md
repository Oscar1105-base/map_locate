# Python OpenStreet 超商&餐廳查詢系統 + 路徑演算法獨立測試

## 用 Python customtkinter  模擬 Windows XP 桌面的小型專案!

<div style="display: flex; justify-content: center; margin-bottom: 20px;">
  <img src="/python0808/main-window.png" alt="GitHub 簡介" style="width: 80%;">
</div>

> 2024/09/29 bata 1.0 edit

## 前情提要

Python 3.11 環境

## 主要功能

這專案中包含以下功能：

- 基礎座標定位 + 設置收尋範圍
- 3個演算法( SA、ABC、自研複合演算法)
- 更新店家資訊透過視窗或csv & txt匯入+格式轉換
- 繪製地圖與收尋店家圖標，輸出成html檔案

---

# DEMO 展示

## 繪製地圖

<div style="display: flex; gap: 20px;">
  <img src="/python0808/MapView-output.png" alt="DEMO 1" style="width: 40%;">
  <img src="/python0808/MapData-output.png" alt="DEMO 1-1" style="width: 40%;">
</div>

> 指定格式: 輸出到output，一份html，一份csv


## 更新資訊

<div style="display: flex; gap: 20px;">
  <img src="/python0808/update-location.png" alt="DEMO 2-1" style="width: 80%;">
</div>

> 指定格式: 店家資訊 / 緯度/ 經度


## 演算法效能測試

<div style="display: flex; gap: 20px;">
  <img src="/python0808/algorithm-test.png" alt="DEMO 2-1" style="width: 60%;">
</div>

> 原先要為路徑規劃設計最短路徑，因時間不足僅做模擬路徑&主畫面終端機顯示結果
