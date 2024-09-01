import csv
import os
import re
import sys


def process_txt_file(file_path):
    lines = []
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        print(f"成功讀取文件，共 {len(lines)} 行")
    except FileNotFoundError:
        print(f"找不到文件：{file_path}")
        return
    except IOError as e:
        print(f"讀取文件時發生錯誤：{e}")
        return

    data = []
    for i, line in enumerate(lines, start=1):
        line = ''.join(line.split())
        match = re.match(r'(.+?)(\d+\.\d+),(\d+\.\d+)', line)
        if match:
            place, latitude, longitude = match.groups()
            data.append([place, latitude, longitude])
            print(f"添加數據: {place}, {latitude}, {longitude}")
        else:
            print(f"警告: 第 {i} 行格式不正確")

    return data


def process_csv_file(file_path):
    data = []
    try:
        with open(file_path, 'r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)  # 跳過標題行
            for row in reader:
                if len(row) >= 3:
                    data.append(row[:3])  # 只取前三列
                    print(f"添加數據: {', '.join(row[:3])}")
                else:
                    print(f"警告: 行 {reader.line_num} 格式不正確")
    except FileNotFoundError:
        print(f"找不到文件：{file_path}")
    except IOError as e:
        print(f"讀取文件時發生錯誤：{e}")

    return data


def main():
    if len(sys.argv) < 3:
        print("使用方法: python update_txt.py <文件路徑> <文件類型>")
        return

    file_path = sys.argv[1]
    file_type = sys.argv[2]

    if file_type == "txt":
        data = process_txt_file(file_path)
    elif file_type == "csv":
        data = process_csv_file(file_path)
    else:
        print("不支持的文件類型")
        return

    if data:
        output_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploaded_places.csv")
        try:
            # 如果文件已存在，先读取现有数据
            existing_data = []
            if os.path.exists(output_file):
                with open(output_file, 'r', newline='', encoding='utf-8') as file:
                    reader = csv.reader(file)
                    next(reader)  # 跳过标题行
                    existing_data = list(reader)

            # 合并现有数据和新数据，去重
            all_data = existing_data + data
            unique_data = list({tuple(row) for row in all_data})

            with open(output_file, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['名稱', '緯度', '經度'])  # 写入标题行
                writer.writerows(unique_data)
            print(f"CSV檔案已更新：{output_file}")
            print(f"總共 {len(unique_data)} 行數據（包括新增和既有）")
        except IOError as e:
            print(f"寫入CSV檔案時發生錯誤：{e}")
    else:
        print("沒有數據可處理")


if __name__ == "__main__":
    main()
