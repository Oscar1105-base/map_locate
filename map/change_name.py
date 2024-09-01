import csv
import os

import customtkinter as ctk

from utils import create_output_directory


# 更改路徑 0901

def change_landmark_name(root):
    change_window = ctk.CTkToplevel(root)
    change_window.title("更改地標名稱")
    change_window.geometry("400x350")
    change_window.configure(fg_color="#2c3e50")

    frame = ctk.CTkFrame(change_window, fg_color="#2c3e50")
    frame.pack(expand=True, fill="both", padx=20, pady=20)

    ctk.CTkLabel(frame, text="請輸入要更改的地標名稱:", font=("Arial", 14)).pack(pady=10)
    name_entry = ctk.CTkEntry(frame, width=200)
    name_entry.pack(pady=5)

    ctk.CTkLabel(frame, text="請輸入新的地標名稱:", font=("Arial", 14)).pack(pady=10)
    new_name_entry = ctk.CTkEntry(frame, width=200)
    new_name_entry.pack(pady=5)

    result_label = ctk.CTkLabel(frame, text="", font=("Arial", 12))
    result_label.pack(pady=10)

    def update_name():
        old_name = name_entry.get().strip()
        new_name = new_name_entry.get().strip()

        if not old_name or not new_name:
            result_label.configure(text="請輸入有效的舊名稱和新名稱")
            return

        output_dir = create_output_directory()
        nearby_places_file = os.path.join(output_dir, 'nearby_places_osm.csv')
        uploaded_places_file = os.path.join(output_dir, 'uploaded_places.csv')

        # 更新 nearby_places_osm.csv
        updated_data = update_csv_file(nearby_places_file, old_name, new_name)

        if updated_data:
            # 如果找到並更新了數據，則更新 uploaded_places.csv
            update_csv_file(uploaded_places_file, old_name, new_name,
                            [updated_data[0], updated_data[1], updated_data[2]])
            result_label.configure(text="更新完成，請檢查控制台輸出")
        else:
            result_label.configure(text=f"未在 nearby_places_osm.csv 中找到 '{old_name}'")

    ctk.CTkButton(frame, text="更改名稱", command=update_name,
                  fg_color="#3498db", hover_color="#2980b9",
                  width=120, height=30, font=("Arial", 12)).pack(pady=10)

    change_window.grab_set()
    change_window.wait_window()


def update_csv_file(file_path, old_name, new_name, data_to_update=None):
    updated_data = None
    try:
        with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            rows = list(reader)

        header = rows[0]
        updated = False
        for row in rows[1:]:
            if row[0].strip() == old_name:
                if file_path.endswith('nearby_places_osm.csv'):
                    updated_data = [new_name, row[1], row[2]]  # 名稱、緯度、經度
                row[0] = new_name
                updated = True
                break

        if updated or data_to_update:
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(header)
                if data_to_update:
                    if file_path.endswith('uploaded_places.csv'):
                        # 只寫入名稱、緯度、經度
                        writer.writerow([data_to_update[0], data_to_update[1], data_to_update[2]])
                    else:
                        writer.writerow(data_to_update)
                    print(f"已在 {file_path} 中添加更新的數據")
                else:
                    writer.writerows(rows[1:])
                    print(f"已更新文件: {file_path}")
        else:
            print(f"未在文件中找到要更新的名稱: {file_path}")

    except Exception as e:
        print(f"更新文件時發生錯誤 {file_path}: {str(e)}")

    return updated_data


def delete_landmark(root):
    delete_window = ctk.CTkToplevel(root)
    delete_window.title("刪除地標")
    delete_window.geometry("400x250")
    delete_window.configure(fg_color="#2c3e50")

    frame = ctk.CTkFrame(delete_window, fg_color="#2c3e50")
    frame.pack(expand=True, fill="both", padx=20, pady=20)

    ctk.CTkLabel(frame, text="請輸入要刪除的地標名稱:", font=("Arial", 14)).pack(pady=10)
    name_entry = ctk.CTkEntry(frame, width=200)
    name_entry.pack(pady=5)

    result_label = ctk.CTkLabel(frame, text="", font=("Arial", 12))
    result_label.pack(pady=10)

    def delete_name():
        name_to_delete = name_entry.get().strip()

        if not name_to_delete:
            result_label.configure(text="請輸入有效的地標名稱")
            return

        output_dir = create_output_directory()
        nearby_places_file = os.path.join(output_dir, 'nearby_places_osm.csv')

        # 刪除 nearby_places_osm.csv 中的地標
        deleted = delete_from_csv(nearby_places_file, name_to_delete)

        if deleted:
            result_label.configure(text="刪除完成，請檢查控制台輸出")
        else:
            result_label.configure(text=f"未在 nearby_places_osm.csv 中找到 '{name_to_delete}'")

    ctk.CTkButton(frame, text="刪除地標", command=delete_name,
                  fg_color="#e74c3c", hover_color="#c0392b",
                  width=120, height=30, font=("Arial", 12)).pack(pady=10)

    delete_window.grab_set()
    delete_window.wait_window()


def delete_from_csv(file_path, name_to_delete):
    deleted = False
    try:
        with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            rows = list(reader)

        header = rows[0]
        new_rows = [row for row in rows[1:] if row[0].strip() != name_to_delete]

        if len(new_rows) < len(rows) - 1:
            deleted = True
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(header)
                writer.writerows(new_rows)
            print(f"已從 {file_path} 中刪除地標 '{name_to_delete}'")
        else:
            print(f"未在文件中找到要刪除的地標: {file_path}")

    except Exception as e:
        print(f"刪除地標時發生錯誤 {file_path}: {str(e)}")

    return deleted


if __name__ == "__main__":
    root = ctk.CTk()
    delete_landmark(root)
    root.mainloop()
