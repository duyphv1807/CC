import sqlite3
import os
import pandas as pd
import re
import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from Connect.Conn_database import *
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ================== Hàm chức năng ==================
last_df = None
current_fig = None
DB_FOLDER = r"C:\Users\LENOVO\Documents\test3\final_report"
db_name = "database"
def Create_database(entry_widget):
    # Tạo thư mục nếu chưa tồn tại
    if not os.path.exists(DB_FOLDER):
        os.makedirs(DB_FOLDER)

    full_path = os.path.join(DB_FOLDER, db_name)

    try:
        conn = sqlite3.connect(full_path)  # tạo hoặc mở database

        # Cập nhật đường dẫn vào Entry trong giao diện
        entry_widget.delete(0, "end")
        entry_widget.insert(0, full_path)
    except sqlite3.Error as e:
        messagebox.showerror("Lỗi", f"Lỗi khi tạo database: {e}")
def Choose_database(entry_widget):
    file_path = filedialog.askopenfilename(
        title="Chọn Database",
        filetypes=[("SQLite Database", "*.db *.sqlite")]
    )
    if file_path:  # nếu user chọn xong
        entry_widget.delete(0, "end")
        entry_widget.insert(0, file_path)
        conn = sqlite3.connect(file_path)
    else:
        messagebox.showinfo("Thông tin", "Chưa chọn database nào!")
def Choose_data(text_widget, scrollbar):
    file_path = filedialog.askopenfilenames(
        title="Chọn file(CSV/JSON)",
        filetypes=[("CSV hoặc JSON", ("*.csv", "*.json"))]
    )
    if file_path:  # nếu user chọn xong
        text_widget.delete("1.0", "end")
        text_widget.insert("1.0","\n".join(file_path))
        Auto_resize_text(text_widget, scrollbar)
    else:
        messagebox.showinfo("Thông tin", "Chưa chọn file nào!")
def Auto_resize_text(text_widget, scrollbar, max_lines=5):
    """Tự động đổi height của Text và bật/tắt scrollbar"""
    content = text_widget.get("1.0", "end").strip()
    if not content:
        num_lines = 1
    else:
        num_lines = content.count("\n") + 1

    # Giới hạn chiều cao
    new_height = min(num_lines, max_lines)
    text_widget.config(height=new_height)

    # Quản lý scrollbar: chỉ hiện khi cần
    if num_lines > max_lines:
        scrollbar.grid()  # hiện lại
    else:
        scrollbar.grid_remove()  # ẩn đi


def Load_data(entry_db, entry_table, text_widget, tree, combo_x, combo_y):
    """Đọc dữ liệu từ nhiều file CSV/JSON và loại bỏ trùng lặp"""
    db_path = entry_db.get().strip()
    table_name = entry_table.get().strip()
    files_content = text_widget.get("1.0", "end").strip()
    if not db_path:
        messagebox.showwarning("Cảnh báo", "Chưa chọn hoặc tạo Database!")
        return
    if not table_name:
        messagebox.showwarning("Cảnh báo", "Chưa nhập tên bảng!")
        return
    if not files_content:
        messagebox.showwarning("Cảnh báo", "Chưa chọn file dữ liệu!")
        return

    file_paths = [line.strip() for line in files_content.split("\n") if line.strip()]

    confirm = messagebox.askyesno("Thông báo", "Bạn có chắc chắn không?")
    if not confirm:
        return
    dataframes = []
    for path in file_paths:
        try:
            if path.lower().endswith(".csv"):
                df = pd.read_csv(path)
            elif path.lower().endswith(".json"):
                df = pd.read_json(path)
            else:
                continue
            df.columns = [col.strip().lower() for col in df.columns]
            dataframes.append(df)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi đọc file {path}:\n{e}")

    if not dataframes:
        messagebox.showwarning("Cảnh báo", "Không có file nào load được!")
        return None

    # Ghép dữ liệu và loại bỏ trùng lặp
    merged_df = pd.concat(dataframes, ignore_index=True).drop_duplicates()

    try:
        conn = sqlite3.connect(db_path)

        # Đọc dữ liệu hiện tại trong DB (nếu có)
        try:
            existing_df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
        except Exception:
            existing_df = pd.DataFrame()

        # Nếu bảng đã có dữ liệu, loại bỏ trùng theo cột 'id'
        if not existing_df.empty and "id" in merged_df.columns:
            new_df = merged_df[~merged_df["id"].isin(existing_df["id"])]
        else:
            new_df = merged_df

        if new_df.empty:
            messagebox.showinfo("Thông báo", "Không có dữ liệu mới để thêm (tất cả đều trùng).")
        else:
            new_df.to_sql(table_name, conn, if_exists="append", index=False)
            Update_column_options(new_df, combo_x, combo_y)
            Show_table_from_df(new_df, tree)
            global last_df
            last_df = new_df
            messagebox.showinfo(
                "Thông tin",
                f"Đã thêm {len(new_df)} bản ghi mới vào bảng '{table_name}'."
            )

    except Exception as e:
        messagebox.showerror("Lỗi", f"Không thể ghi dữ liệu vào database:\n{e}")
def Show_table_from_df(df, tree):
    """Hiển thị DataFrame lên Treeview"""
    # Xóa dữ liệu cũ
    for col in tree.get_children():
        tree.delete(col)

    # Cập nhật lại cột
    tree["columns"] = list(df.columns)
    tree["show"] = "headings"
    for col in df.columns:
        tree.heading(col, text=col)
        tree.column(col, width=120, anchor="w")

    # Thêm dữ liệu mới
    for _, row in df.iterrows():
        tree.insert("", "end", values=list(row))
def Update_column_options(df, combo_x, combo_y):
    """Cập nhật danh sách cột cho combobox X và Y"""
    cols = list(df.columns)
    combo_x["values"] = cols
    combo_y["values"] = cols

    # reset lựa chọn
    combo_x.set("")
    combo_y.set("")

    # Ràng buộc sự kiện để loại trừ cột đã chọn
    def on_x_change(event):
        x_val = combo_x.get()
        combo_y["values"] = [c for c in cols if c != x_val]

    def on_y_change(event):
        y_val = combo_y.get()
        combo_x["values"] = [c for c in cols if c != y_val]

    combo_x.bind("<<ComboboxSelected>>", on_x_change)
    combo_y.bind("<<ComboboxSelected>>", on_y_change)

def parse_number(x):
    """Chuyển chuỗi tiền tệ VN (vd: '1.240.000đ', '193.600đ', '964,32') thành float"""
    if pd.isna(x):
        return np.nan
    s = str(x).strip()
    if s == "":
        return np.nan

    # bỏ ký tự tiền, chữ, khoảng trắng đặc biệt
    s = s.replace('\u00A0', '').replace('\u2009', '').replace('\u202f', '').replace(' ', '')
    s = re.sub(r'[A-Za-z]', '', s)
    s = re.sub(r'[^\d,.\-]', '', s)

    if s == "" or s in ["-", ".", ","]:
        return np.nan

    # nếu có cả . và , thì xác định dấu nào là thập phân (dựa theo vị trí cuối)
    if '.' in s and ',' in s:
        if s.rfind('.') > s.rfind(','):
            s = s.replace(',', '')
        else:
            s = s.replace('.', '')
            s = s.replace(',', '.')
    elif ',' in s:
        parts = s.split(',')
        if len(parts[-1]) == 3:  # có thể là dấu ngăn nghìn
            s = s.replace(',', '')
        else:
            s = s.replace(',', '.')
    elif '.' in s:
        parts = s.split('.')
        if len(parts[-1]) == 3:
            s = s.replace('.', '')

    try:
        return float(s)
    except:
        return np.nan


def Draw_chart(combo_chart, combo_x, combo_y, frame_chart):
    """Vẽ biểu đồ từ DataFrame hiện tại (last_df) dựa trên lựa chọn X, Y"""
    global last_df, current_fig
    if last_df is None or last_df.empty:
        messagebox.showwarning("Chưa có dữ liệu", "Bạn cần load dữ liệu hoặc chạy SQL trước!")
        return

    chart_type = combo_chart.get()
    col_x = combo_x.get()
    col_y = combo_y.get()

    if not col_x or not col_y:
        messagebox.showwarning("Cảnh báo", "Bạn phải chọn cả cột X và cột Y!")
        return
    if col_x not in last_df.columns or col_y not in last_df.columns:
        messagebox.showwarning("Cảnh báo", "Cột X hoặc Y không tồn tại trong dữ liệu!")
        return

    # Chuẩn hóa cột Y thành số
    df = last_df.copy()
    df['_parsed_y_'] = df[col_y].apply(parse_number)
    plot_df = df.dropna(subset=['_parsed_y_'])[[col_x, '_parsed_y_']]

    # Xóa biểu đồ cũ
    for widget in frame_chart.winfo_children():
        widget.destroy()

    if plot_df.empty:
        messagebox.showerror("Lỗi", "Không có dữ liệu số hợp lệ để vẽ biểu đồ!")
        return

    # Xóa biểu đồ cũ
    for widget in frame_chart.winfo_children():
        widget.destroy()

    fig, ax = plt.subplots(figsize=(8, 4.5))
    current_fig = fig

    try:
        if chart_type == "Bar":
            x_vals = plot_df[col_x].astype(str).tolist()
            y_vals = plot_df['_parsed_y_'].tolist()
            ax.bar(x_vals, y_vals)
            ax.set_xlabel(col_x)
            ax.set_ylabel(col_y)
            ax.tick_params(axis='x', rotation=45)

        elif chart_type == "Pie":
            sizes = plot_df['_parsed_y_'].tolist()
            labels = plot_df[col_x].astype(str).tolist()
            ax.pie(sizes, labels=labels, autopct='%1.1f%%')
            ax.set_ylabel("")

        elif chart_type == "Line":
            x_vals = plot_df[col_x].astype(str).tolist()
            y_vals = plot_df['_parsed_y_'].tolist()
            ax.plot(x_vals, y_vals, marker='o')
            ax.set_xlabel(col_x)
            ax.set_ylabel(col_y)
            ax.tick_params(axis='x', rotation=45)

        elif chart_type == "Scatter":
            x_vals = plot_df[col_x]
            if not pd.api.types.is_numeric_dtype(x_vals):
                x_vals = x_vals.apply(parse_number)
            y_vals = plot_df['_parsed_y_']
            ax.scatter(x_vals, y_vals)
            ax.set_xlabel(col_x)
            ax.set_ylabel(col_y)

        else:
            messagebox.showinfo("Thông báo", f"Loại biểu đồ '{chart_type}' chưa hỗ trợ!")
            return

        # Nhúng vào Tkinter
        canvas = FigureCanvasTkAgg(fig, master=frame_chart)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    except Exception as e:
        messagebox.showerror("Lỗi khi vẽ", f"{type(e).__name__}: {e}")

def Save_chart():
    """Lưu biểu đồ hiện tại ra file ảnh"""
    global current_fig
    if current_fig is None:
        messagebox.showwarning("Chưa có biểu đồ", "Bạn cần vẽ biểu đồ trước khi lưu!")
        return

    file_path = filedialog.asksaveasfilename(
        title="Lưu biểu đồ",
        defaultextension=".png",
        filetypes=[("PNG Image", "*.png"), ("JPEG Image", "*.jpg"), ("All files", "*.*")]
    )

    if not file_path:
        return  # người dùng bấm Cancel

    try:
        current_fig.savefig(file_path, dpi=300, bbox_inches="tight")
        messagebox.showinfo("Thành công", f"Biểu đồ đã được lưu tại:\n{file_path}")
    except Exception as e:
        messagebox.showerror("Lỗi", f"Không thể lưu biểu đồ:\n{e}")
def Excute_sql(Entry_database, sql_text, tree, combo_x, combo_y):
    """Thực thi câu lệnh SQL từ ô nhập và hiển thị kết quả"""
    global last_df

    # Lấy đường dẫn DB và câu lệnh SQL
    db_path = Entry_database.get().strip()
    query = sql_text.get("1.0", "end").strip()

    if not db_path:
        messagebox.showwarning("Cảnh báo", "Chưa chọn hoặc tạo Database!")
        return
    if not query:
        messagebox.showwarning("Cảnh báo", "Bạn chưa nhập câu lệnh SQL!")
        return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Nếu là SELECT → trả về bảng
        if query.strip().lower().startswith("select"):
            df = pd.read_sql_query(query, conn)
            if df.empty:
                messagebox.showinfo("Thông tin", "Truy vấn thành công nhưng không có dữ liệu.")
            else:
                Show_table_from_df(df, tree)
                Update_column_options(df, combo_x, combo_y)
                last_df = df
        else:
            cursor.execute(query)
            conn.commit()
            messagebox.showinfo("Thông tin", f"Đã thực thi SQL thành công.\nẢnh hưởng {cursor.rowcount} dòng.")

    except Exception as e:
        messagebox.showerror("Lỗi SQL", str(e))

def clone():
    pass
