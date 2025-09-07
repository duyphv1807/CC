import sqlite3
import os
import pandas as pd
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
# ================== Hàm chức năng ==================

def Create_database():
    db_name = Entry_database.get()
    address = r"C:\Users\ASUS\final_report\Storage"
    if not os.path.exists(address):
        os.makedirs(address)
    full_path = os.path.join(address, db_name)
    if db_name.strip() == "":
        messagebox.showwarning("Thiếu tên!", "Vui lòng nhập tên database.")
        return
    try:
        conn = sqlite3.connect(full_path)
        # cursor = conn.cursor()
        # cursor
        messagebox.showinfo("Thông tin", f"Đã tạo database {db_name}")
        conn.close()
    except sqlite3.Error:
        messagebox.showerror("Lỗi", "Lỗi khi tạo database")

def Choose_database():
    file_path = filedialog.askopenfilename(title="Chọn file Database", filetypes=[("SQLite Database", "*.db")])
    if file_path:
        Entry_database.delete(0, tk.END)
        Entry_database.insert(0, file_path)

def Choose_link():
    file_path = filedialog.askopenfilename(title="Chọn file dữ liệu", filetypes=[("CSV Files", "*.csv"), ("JSON Files", "*.json")])
    if file_path:
        Entry_link.delete(0, tk.END)
        Entry_link.insert(0, file_path)

def load_columns():
    db_path = Entry_database.get()
    table_name = Entry_table.get()
    if not db_path or not table_name:
        messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập đường dẫn database và tên bảng.")
        return
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [row[1] for row in cursor.fetchall()]
        conn.close()
        if columns:
            combo_x['values'] = columns
            combo_y['values'] = columns
            messagebox.showinfo("Thành công", f"Đã tải {len(columns)} cột từ bảng '{table_name}'")
        else:
            messagebox.showwarning("Không có cột", "Không tìm thấy cột nào trong bảng.")
    except Exception as e:
        messagebox.showerror("Lỗi", f"Lỗi khi lấy cột: {e}")

def execute_sql():
    query = sql_text.get("1.0", tk.END).strip()
    db_path = Entry_database.get()
    if not query:
        messagebox.showwarning("Thiếu câu lệnh", "Vui lòng nhập câu lệnh SQL.")
        return
    if not os.path.exists(db_path):
        messagebox.showerror("Lỗi", "Đường dẫn database không tồn tại.")
        return
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(query)
        conn.commit()
        messagebox.showinfo("Thành công", "Đã thực thi câu lệnh SQL.")
        conn.close()
    except sqlite3.Error as e:
        messagebox.showerror("Lỗi SQL", f"Lỗi khi thực thi: {e}")

def draw_chart():
    db_path = Entry_database.get()
    table_name = Entry_table.get()
    x_col = selected_x.get()
    y_col = selected_y.get()
    chart_type = selected_chart.get()

    if not all([db_path, table_name, x_col, y_col, chart_type]):
        messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập đầy đủ thông tin để vẽ biểu đồ.")
        return
    if not os.path.exists(db_path):
        messagebox.showerror("Lỗi", "Đường dẫn database không tồn tại.")
        return
    try:
        conn = sqlite3.connect(db_path)
        query = f"SELECT {x_col}, {y_col} FROM {table_name}"
        df = pd.read_sql_query(query, conn)
        conn.close()

        if df.empty:
            messagebox.showwarning("Không có dữ liệu", "Bảng không có dữ liệu hoặc cột không hợp lệ.")
            return

        plt.figure(figsize=(8, 5))
        if chart_type == "Bar":
            plt.bar(df[x_col], df[y_col])
        elif chart_type == "Pie":
            plt.pie(df[y_col], labels=df[x_col], autopct='%1.1f%%')
        elif chart_type == "Line":
            plt.plot(df[x_col], df[y_col], marker='o')
        elif chart_type == "Scatter":
            plt.scatter(df[x_col], df[y_col])
        else:
            messagebox.showerror("Lỗi", "Loại biểu đồ không hợp lệ.")
            return

        plt.title(f"{chart_type} Chart: {y_col} theo {x_col}")
        plt.xlabel(x_col)
        plt.ylabel(y_col)
        plt.tight_layout()
        plt.show()
        plt.savefig("tam.png")  # hoặc gọi save_chart() sau khi chọn đường dẫn
        plt.show()
    except Exception as e:
        messagebox.showerror("Lỗi khi vẽ biểu đồ", str(e))

def save_chart():
    file_path = filedialog.asksaveasfilename(
        defaultextension=".png",
        filetypes=[("PNG Image", "*.png")],
        title="Lưu biểu đồ"
    )
    if file_path:
        try:
            plt.savefig(file_path)
            messagebox.showinfo("Thành công", f"Đã lưu biểu đồ tại:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Lỗi khi lưu", str(e))

root = tk.Tk()
root.title("MENU")
root.geometry("1600x800")

def clone():
    pass