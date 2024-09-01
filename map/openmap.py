import configparser
import csv
import os
import shutil
from math import radians, sin, cos, sqrt, atan2, degrees

import folium
import requests
from folium.plugins import Draw, MeasureControl


def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371  # 地球半徑（公里）
    dLat = radians(lat2 - lat1)
    dLon = radians(lon2 - lon1)
    a = sin(dLat / 2) * sin(dLat / 2) + cos(radians(lat1)) * cos(radians(lat2)) * sin(dLon / 2) * sin(dLon / 2)
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c * 1000  # 轉換為米


def get_direction(lat1, lon1, lat2, lon2):
    dLon = lon2 - lon1
    y = sin(radians(dLon)) * cos(radians(lat2))
    x = cos(radians(lat1)) * sin(radians(lat2)) - sin(radians(lat1)) * cos(radians(lat2)) * cos(radians(dLon))
    angle = degrees(atan2(y, x))

    if angle < 0:
        angle += 360

    if 45 <= angle < 135:
        return "東"
    elif 135 <= angle < 225:
        return "南"
    elif 225 <= angle < 315:
        return "西"
    else:
        return "北"


def process_existing_places(file_path):
    existing_places = {}
    try:
        with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # 跳過標題行
            for row in reader:
                if len(row) >= 3:
                    name, lat, lon = row[:3]
                    lat, lon = float(lat), float(lon)
                    existing_places[(lat, lon)] = name
    except Exception as e:
        print(f"讀取文件時發生錯誤 {file_path}: {str(e)}")
    return existing_places


def process_place(element, existing_places, processed_coordinates, latitude, longitude):
    if 'tags' not in element:
        return None

    lat = element['lat']
    lon = element['lon']
    key = (lat, lon)

    if key in processed_coordinates:
        return None

    name = existing_places.get(key) or element['tags'].get('name', '')

    # 篩選掉名稱為"蝦皮"或空白的地點
    if name in ["蝦皮", "Unknown", ""]:
        return None

    if element['tags'].get('shop') == 'convenience':
        place_type = '便利商店'
    elif element['tags'].get('amenity') == 'restaurant':
        place_type = '餐廳'
    elif element['tags'].get('amenity') == 'cafe':
        place_type = '咖啡廳'
    elif element['tags'].get('cuisine') == 'breakfast':
        place_type = '早餐店'
    elif element['tags'].get('cuisine') == 'burger':
        place_type = '漢堡店'
    else:
        return None

    distance = haversine_distance(latitude, longitude, lat, lon)
    direction = get_direction(latitude, longitude, lat, lon)

    if distance <= 300:  # 確保在300米範圍內
        processed_coordinates.add(key)
        return {
            'name': name,
            'type': place_type,
            'lat': lat,
            'lon': lon,
            'distance': distance,
            'direction': direction,
            'is_uploaded': key in existing_places
        }
    return None


def initialize_map(latitude, longitude):
    m = folium.Map(location=[latitude, longitude], zoom_start=16)
    m.add_child(MeasureControl())
    folium.Marker([latitude, longitude], popup="指定位置").add_to(m)
    folium.Circle(
        radius=300,
        location=[latitude, longitude],
        popup="300m範圍",
        color="crimson",
        fill=True,
    ).add_to(m)
    return m


def get_or_update_places(nearby_file, uploaded_file, latitude, longitude, radius):
    if not os.path.exists(nearby_file) or not os.path.getsize(nearby_file):
        # 如果 nearby_file 不存在或為空，從 API 獲取初始數據
        places_dict = fetch_places_from_api(latitude, longitude, radius)
        save_places_to_csv(places_dict, nearby_file)
    else:
        # 從 nearby_file 加載數據
        places_dict = load_places_from_csv(nearby_file, uploaded_file)

    # 如果 uploaded_file 存在，合併其中的數據
    if os.path.exists(uploaded_file):
        uploaded_places = load_places_from_csv(uploaded_file, None)
        places_dict.update(uploaded_places)
        save_places_to_csv(places_dict, nearby_file)

    return places_dict


def fetch_places_from_api(latitude, longitude, radius):
    overpass_url = "http://overpass-api.de/api/interpreter"
    overpass_query = f"""
     [out:json];
     (
       node["shop"="convenience"](around:{radius},{latitude},{longitude});
       node["amenity"="restaurant"](around:{radius},{latitude},{longitude});
       node["amenity"="cafe"](around:{radius},{latitude},{longitude});
       node["cuisine"="breakfast"](around:{radius},{latitude},{longitude});
       node["cuisine"="burger"](around:{radius},{latitude},{longitude});
     );
     out body;
     """

    response = requests.get(overpass_url, params={'data': overpass_query})
    data = response.json()

    places_dict = {}
    processed_coordinates = set()
    existing_places = process_existing_places('uploaded_places.csv')

    for element in data['elements']:
        place = process_place(element, existing_places, processed_coordinates, latitude, longitude)
        if place:
            key = (place['lat'], place['lon'])
            places_dict[key] = place

    return places_dict


def save_places_to_csv(places_dict, file_path):
    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['名稱', '緯度', '經度'])
        for info in places_dict.values():
            writer.writerow([info['name'], info['lat'], info['lon']])


def load_places_from_csv(nearby_file, uploaded_file):
    places_dict = {}
    uploaded_places = set()

    if uploaded_file and os.path.exists(uploaded_file):
        with open(uploaded_file, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # 跳過標題行
            for row in reader:
                if len(row) >= 3:
                    name, lat, lon = row[:3]
                    uploaded_places.add(name)

    with open(nearby_file, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # 跳過標題行
        for row in reader:
            if len(row) >= 3:
                name, lat, lon = row[:3]
                lat, lon = float(lat), float(lon)
                places_dict[(lat, lon)] = {
                    'name': name,
                    'lat': lat,
                    'lon': lon,
                    'is_uploaded': name in uploaded_places
                }
    return places_dict


def update_map(m, places_dict):
    for info in places_dict.values():
        icon_color = 'green' if info.get('is_uploaded', False) else 'orange'
        folium.Marker(
            [info['lat'], info['lon']],
            popup=f"{info['name']}",
            icon=folium.Icon(color=icon_color)
        ).add_to(m)


def add_map_features(m):
    draw = Draw()
    draw.add_to(m)


def save_map(m, parent_dir):
    output_html = os.path.join(parent_dir, 'map_with_nearby_places_osm.html')
    print("output_html = " + output_html)
    m.save(output_html)
    print(f"處理完成。請查看 '{output_html}' 文件。")


def main():
    try:
        # 設定基本參數
        config = configparser.ConfigParser()
        config.read('config.ini')

        # 獲取配置的值,如果沒有配置則使用默認值
        latitude = config.getfloat('Location', 'latitude', fallback=25.0111)
        longitude = config.getfloat('Location', 'longitude', fallback=121.5146)
        radius = config.getint('Location', 'radius', fallback=300)

        # 設定文件路徑
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_dir = os.path.dirname(current_dir)
        output_dir = os.path.join(project_dir, 'output')

        # 確保output資料夾存在
        os.makedirs(output_dir, exist_ok=True)

        nearby_file = os.path.join(output_dir, 'nearby_places_osm.csv')
        uploaded_file = os.path.join(output_dir, 'uploaded_places.csv')

        print("current_dir =", current_dir)
        print("project_dir =", project_dir)
        print("output_dir =", output_dir)
        print("nearby_file =", nearby_file)
        print("uploaded_file =", uploaded_file)

        # 確保 uploaded_places.csv 存在
        if not os.path.exists(uploaded_file):
            with open(uploaded_file, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['名稱', '緯度', '經度'])
            print("已創建空的 uploaded_places.csv 文件")

        # 獲取或更新地點數據
        places_dict = get_or_update_places(nearby_file, uploaded_file, latitude, longitude, radius)

        # 初始化地圖
        m = initialize_map(latitude, longitude)

        # 更新地圖
        update_map(m, places_dict)

        # 添加額外的地圖功能
        add_map_features(m)

        # 保存地圖
        output_html = os.path.join(output_dir, 'map_with_nearby_places_osm.html')
        m.save(output_html)
        print(f"處理完成。HTML 文件已保存至: '{output_html}'")

        if os.path.exists(output_html):
            print("HTML 文件成功創建")
        else:
            print("錯誤: HTML 文件未能成功創建")

    except Exception as e:
        print(f"執行過程中發生錯誤: {str(e)}")
        import traceback
        print(traceback.format_exc())


if __name__ == "__main__":
    main()


# 注意：以下函數應該在主程序之外調用，例如在打包過程中
def move_files_to_external_folder():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    output_dir = os.path.join(current_dir, 'output')

    # 移動文件到父目錄
    shutil.move(os.path.join(output_dir, 'map_with_nearby_places_osm.html'),
                os.path.join(parent_dir, 'map_with_nearby_places_osm.html'))
    shutil.move(os.path.join(output_dir, 'nearby_places_osm.csv'),
                os.path.join(parent_dir, 'nearby_places_osm.csv'))
    print("文件已成功移動到外部文件夾")
