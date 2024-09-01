import configparser
import csv
import http.server
import os
import socketserver
import subprocess
import sys
import threading
import webbrowser
from datetime import datetime
from tkinter import filedialog

import customtkinter as ctk
from PIL import Image

from map.change_name import change_landmark_name, delete_landmark
from utils import run_openmap, create_output_directory


class LandmarkUpdateWindow:
    def __init__(self, root):
        self.root = root
        self.window = None
        self.icons = {}
        self.create_window()

    def create_window(self):
        self.window = ctk.CTkToplevel(self.root)
        self.window.title("地標更新")
        self.window.geometry("820x600")
        self.window.configure(fg_color="#2c3e50")
        self.window.protocol("WM_DELETE_WINDOW", self.hide_window)  # 重写关闭操作

        # 添加黑色边框
        border_frame = ctk.CTkFrame(self.window, fg_color="black")
        border_frame.pack(expand=True, fill="both", padx=2, pady=2)

        self.frame = ctk.CTkFrame(border_frame, fg_color="#2c3e50")
        self.frame.pack(expand=True, fill="both", padx=2, pady=2)
        self.frame.grid_columnconfigure((0, 1), weight=1)
        self.frame.grid_rowconfigure((0, 1, 2), weight=1)

        self.load_icons()
        self.create_buttons()

        self.window.withdraw()  # 初始化时隐藏窗口

    def load_icons(self):
        icon_files = {
            "upload_txt": "upload_txt.png",
            "upload_csv": "upload_csv.png",
            "change_name": "change_name.png",
            "delete_mark": "delete_mark.png"
        }
        for key, filename in icon_files.items():
            try:
                self.icons[key] = ctk.CTkImage(Image.open(os.path.join("image", filename)), size=(50, 50))
            except FileNotFoundError:
                print(f"Warning: Image file {filename} not found.")
                self.icons[key] = None

    def create_buttons(self):
        button_font = ctk.CTkFont(size=24, weight="bold")
        buttons = [
            ("上傳 TXT 文件\n(店家名稱/緯度/經度)", upload_txt, "#3498db", "#2980b9", 0, 0, self.icons["upload_txt"]),
            ("上傳 CSV 文件", upload_csv, "#e74c3c", "#c0392b", 0, 1, self.icons["upload_csv"]),
            ("更改名稱", change_name, "#3498db", "#2980b9", 1, 0, self.icons["change_name"]),
            ("刪除標記", delete_mark, "#e74c3c", "#c0392b", 1, 1, self.icons["delete_mark"])
        ]

        for text, command, fg_color, hover_color, row, col, icon in buttons:
            btn = ctk.CTkButton(self.frame, text=text, image=icon, compound="top",
                                command=lambda cmd=command: self.execute_command(cmd),
                                fg_color=fg_color, hover_color=hover_color,
                                width=350, height=250, font=button_font, corner_radius=10)
            btn.grid(row=row, column=col, padx=20, pady=20, sticky="nsew")

    def execute_command(self, cmd):
        progress = ctk.CTkProgressBar(self.frame, mode='indeterminate', height=20, width=700)
        progress.grid(row=2, column=0, columnspan=2, padx=20, pady=20, sticky="ew")
        progress.start()

        def run_command():
            cmd()
            progress.stop()
            progress.grid_forget()
            self.window.after(100, self.hide_window)  # 延迟隐藏窗口，给UI时间更新

        self.window.after(100, run_command)  # 延迟执行命令，给UI时间显示进度条

    def show_window(self):
        self.window.deiconify()
        self.window.lift()
        self.window.focus_force()
        self.window.grab_set()

    def hide_window(self):
        self.window.grab_release()
        self.window.withdraw()


# 在主窗口创建时初始化 LandmarkUpdateWindow
landmark_window = None


def create_main_window():
    global landmark_window
    main_window = ctk.CTk()
    main_window.title("紀錄與地平線 Ver_1.0")

    window_width = 820
    window_height = 600
    screen_width = main_window.winfo_screenwidth()
    screen_height = main_window.winfo_screenheight()
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)
    main_window.geometry(f'{window_width}x{window_height}+{x}+{y}')
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    landmark_window = LandmarkUpdateWindow(main_window)
    return main_window


def create_main_frame(root):
    frame = ctk.CTkFrame(root, fg_color="#2c3e50")
    frame.pack(pady=20, padx=20, fill="both", expand=True)
    frame.grid_columnconfigure((0, 1), weight=1)
    frame.grid_rowconfigure(3, weight=1)
    return frame


def create_buttons(frame, commands):
    button_font = ctk.CTkFont(size=30)

    icons = {
        "設置起點": ctk.CTkImage(Image.open("image/new_point.png"), size=(30, 30)),
        "算法測試": ctk.CTkImage(Image.open("image/algorithm.png"), size=(30, 30)),
        "地標更新": ctk.CTkImage(Image.open("image/update_point.png"), size=(30, 30)),
        "地圖繪製": ctk.CTkImage(Image.open("image/create_map.png"), size=(30, 30))
    }

    buttons = [
        ("設置起點", "#3498db", "#2980b9", 0, 0),
        ("算法測試", "#e74c3c", "#c0392b", 0, 1),
        ("地標更新", "#3498db", "#2980b9", 1, 0),
        ("地圖繪製", "#e74c3c", "#c0392b", 1, 1)
    ]

    for text, fg_color, hover_color, row, col in buttons:
        btn = ctk.CTkButton(frame, text=text, image=icons[text], compound="left",
                            command=commands[text], fg_color=fg_color, hover_color=hover_color,
                            width=350, height=80, font=button_font)
        btn.grid(row=row, column=col, padx=20, pady=20)


def create_output_area(frame):
    output_text = ctk.CTkTextbox(frame, wrap="none", font=("Courier", 14))
    output_text.grid(row=3, column=0, columnspan=2, padx=20, pady=20, sticky="nsew")
    return output_text


def initialize_output(output_text):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    initial_output = f"{sys.executable} (Python {sys.version.split()[0]}) - {current_time}"
    output_text.insert("1.0", initial_output)


def update_output(output_text, message):
    output_text.insert("end", f"\n{message}")
    output_text.see("end")


def update_config(lat, lon, radius):
    config = configparser.ConfigParser()
    config['Location'] = {
        'latitude': str(lat),
        'longitude': str(lon),
        'radius': str(radius)
    }
    with open('config.ini', 'w') as configfile:
        config.write(configfile)


def add_point():
    add_window = ctk.CTkToplevel(root)
    add_window.title("設置起點")
    add_window.geometry("400x400")  # Increased height to accommodate button
    add_window.configure(fg_color="#2c3e50")

    frame = ctk.CTkFrame(add_window, fg_color="#2c3e50")
    frame.pack(expand=True, fill="both", padx=20, pady=20)

    ctk.CTkLabel(frame, text="請輸入緯度:", font=("Arial", 14)).pack(pady=5)
    lat_entry = ctk.CTkEntry(frame, width=200)
    lat_entry.pack(pady=5)

    ctk.CTkLabel(frame, text="請輸入經度:", font=("Arial", 14)).pack(pady=5)
    lon_entry = ctk.CTkEntry(frame, width=200)
    lon_entry.pack(pady=5)

    ctk.CTkLabel(frame, text="請輸入範圍(米):", font=("Arial", 14)).pack(pady=5)
    radius_entry = ctk.CTkEntry(frame, width=200)
    radius_entry.pack(pady=5)

    result_label = ctk.CTkLabel(frame, text="", font=("Arial", 20))
    result_label.pack(pady=10)

    def update_point():
        try:
            lat = float(lat_entry.get().strip())
            lon = float(lon_entry.get().strip())
            radius = int(radius_entry.get().strip())

            # 更新配置文件
            update_config(lat, lon, radius)

            result_label.configure(text="起點已更新，請檢查控制台輸出")
            update_output(output_text, f"新起點已設置: 緯度 {lat}, 經度 {lon}, 範圍 {radius}米")
        except ValueError:
            result_label.configure(text="請輸入有效的數值")

    ctk.CTkButton(frame, text="設置起點", command=update_point,
                  fg_color="#3498db", hover_color="#2980b9",
                  width=200, height=40, font=("Arial", 14)).pack(pady=20)

    add_window.grab_set()
    add_window.wait_window()


def update_openmap_defaults(lat, lon, radius):
    openmap_path = os.path.join(os.path.dirname(__file__), "map", "openmap.py")
    with open(openmap_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    for i, line in enumerate(lines):
        if line.strip().startswith("latitude ="):
            lines[i] = f"        latitude = {lat}\n"
        elif line.strip().startswith("longitude ="):
            lines[i] = f"        longitude = {lon}\n"
        elif line.strip().startswith("radius ="):
            lines[i] = f"        radius = {radius}  # 米\n"

    with open(openmap_path, 'w', encoding='utf-8') as file:
        file.writelines(lines)

    print(f"openmap.py 已更新: 緯度 {lat}, 經度 {lon}, 範圍 {radius}米")


def run_algorithm():
    algorithm_path = os.path.join(os.path.dirname(__file__), "algorithm", "algorithm.py")
    try:
        result = subprocess.run(["python", algorithm_path], capture_output=True, text=True, encoding="utf-8",
                                check=True)
        update_output(output_text, result.stdout)
    except subprocess.CalledProcessError as e:
        error_message = f"Error running algorithm.py: {e}\n"
        if e.stdout:
            error_message += f"Stdout: {e.stdout}\n"
        if e.stderr:
            error_message += f"Stderr: {e.stderr}\n"
        update_output(output_text, error_message)
    except Exception as e:
        update_output(output_text, f"An unexpected error occurred: {str(e)}")


def update_landmarks():
    global landmark_window
    if landmark_window:
        landmark_window.show_window()
    else:
        print("Error: Landmark update window not initialized.")


def execute_command(cmd, window, frame):
    progress = ctk.CTkProgressBar(frame, mode='indeterminate', height=20, width=700)
    progress.grid(row=2, column=0, columnspan=2, padx=20, pady=20, sticky="ew")
    progress.start()

    def run_command():
        cmd()
        progress.stop()
        progress.grid_forget()
        window.after(100, window.destroy)  # 延迟关闭窗口，给UI时间更新

    window.after(100, run_command)  # 延迟执行命令，给UI时间显示进度条


def process_file(file_path, file_type):
    update_txt_path = os.path.join(os.path.dirname(__file__), "update_txt.py")
    result = subprocess.run(["python", update_txt_path, file_path, file_type], capture_output=True, text=True,
                            encoding="utf-8")
    update_output(output_text, result.stdout)

    processed_file = result.stdout.strip().split("：")[-1].strip()
    if os.path.exists(processed_file):
        os.rename(processed_file, "uploaded_places.csv")
        update_output(output_text, f"文件已重命名為 uploaded_places.csv")


def upload_txt():
    file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
    if file_path:
        process_file(file_path, "txt")


def upload_csv():
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if file_path:
        process_file(file_path, "csv")


def change_name():
    change_landmark_name(root)


def delete_mark():
    delete_landmark(root)


def start_server(directory, port=8000):
    os.chdir(directory)
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"Serving at port {port}")
        httpd.serve_forever()


def draw_map():
    output_dir = create_output_directory()
    # 确保 uploaded_places.csv 存在
    uploaded_file = os.path.join(output_dir, "uploaded_places.csv")
    if not os.path.exists(uploaded_file):
        with open(uploaded_file, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['名稱', '緯度', '經度'])
        update_output(output_text, "已創建空的 uploaded_places.csv 文件")

    update_uploaded_places()
    run_openmap()

    # 檢查 HTML 文件是否生成
    html_file = "map_with_nearby_places_osm.html"
    html_path = os.path.join(output_dir, html_file)

    if os.path.exists(html_path):
        # 啟動服務器並打開瀏覽器
        port = 8000
        server_thread = threading.Thread(target=start_server, args=(output_dir, port))
        server_thread.daemon = True
        server_thread.start()

        webbrowser.open(f"http://localhost:{port}/{html_file}")

        update_output(output_text,
                      f"地圖已生成並在瀏覽器中打開。如果沒有自動打開，請手動訪問 http://localhost:{port}/{html_file}")
    else:
        update_output(output_text, "HTML 文件生成失敗，請檢查 openmap.py 的執行結果")


def update_uploaded_places():
    output_dir = create_output_directory()
    uploaded_file = os.path.join(output_dir, "uploaded_places.csv")
    temp_file = os.path.join(output_dir, "temp_uploaded_places.csv")
    new_uploaded_file = os.path.join(output_dir, "new_uploaded_places.csv")
    existing_records = set()

    # 如果存在原有的 uploaded_places.csv，讀取已有的數據
    if os.path.exists(uploaded_file):
        with open(uploaded_file, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # 跳過標題行
            for row in reader:
                existing_records.add((row[1], row[2]))  # 使用緯度和經度作為唯一標識

    # 讀取新上傳的數據（如果有的話）
    new_data = []
    if os.path.exists(new_uploaded_file):
        with open(new_uploaded_file, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # 跳過標題行
            for row in reader:
                if (row[1], row[2]) not in existing_records:
                    new_data.append(row)
                    existing_records.add((row[1], row[2]))

    with open(temp_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['名稱', '緯度', '經度'])

        # 寫入原有數據
        if os.path.exists(uploaded_file):
            with open(uploaded_file, 'r', newline='', encoding='utf-8') as original:
                reader = csv.reader(original)
                next(reader)  # 跳過標題行
                for row in reader:
                    writer.writerow(row)

        # 寫入新數據
        for row in new_data:
            writer.writerow(row)

    # 替換原有文件
    if os.path.exists(uploaded_file):
        os.remove(uploaded_file)
    os.rename(temp_file, uploaded_file)

    # 刪除臨時的新上傳文件
    if os.path.exists(new_uploaded_file):
        os.remove(new_uploaded_file)

    update_output(output_text, f"已更新 {uploaded_file}，新增了 {len(new_data)} 條記錄")


def main():
    global root, output_text
    root = create_main_window()
    frame = create_main_frame(root)
    output_text = create_output_area(frame)
    initialize_output(output_text)

    commands = {
        "設置起點": add_point,
        "算法測試": run_algorithm,
        "地標更新": update_landmarks,
        "地圖繪製": draw_map
    }

    create_buttons(frame, commands)

    root.mainloop()


if __name__ == "__main__":
    main()
