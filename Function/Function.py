import sqlite3
import os
import pandas as pd
import re
import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import json

# ================== Biến toàn cục ==================
last_df = None
current_fig = None
DB_FOLDER = r"C:\Users\LENOVO\Documents\test3"
db_name = "database"

# ================== Hàm xử lý database ==================
def create_database(entry_widget):
    """Tạo database mới"""
    if not os.path.exists(DB_FOLDER):
        os.makedirs(DB_FOLDER)

    full_path = os.path.join(DB_FOLDER, db_name)

    try:
        conn = sqlite3.connect(full_path)
        entry_widget.delete(0, "end")
        entry_widget.insert(0, full_path)
        conn.close()
    except sqlite3.Error as e:
        messagebox.showerror("Lỗi", f"Lỗi khi tạo database: {e}")


def choose_database(entry_widget):
    """Chọn database từ file dialog"""
    file_path = filedialog.askopenfilename(
        title="Chọn Database",
        filetypes=[("SQLite Database", "*.db *.sqlite")]
    )
    if file_path:
        entry_widget.delete(0, "end")
        entry_widget.insert(0, file_path)
    else:
        messagebox.showinfo("Thông tin", "Chưa chọn database nào!")


def get_table_list(entry_database):
    """Lấy danh sách các bảng trong database"""
    db_path = entry_database.get().strip()

    if not db_path:
        return []

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        return tables
    except sqlite3.Error as e:
        messagebox.showerror("Lỗi", f"Lỗi khi lấy danh sách bảng: {e}")
        return []


def create_new_table(entry_database, table_name, columns_definition):
    """Tạo bảng mới trong database"""
    db_path = entry_database.get().strip()

    if not db_path:
        messagebox.showwarning("Cảnh báo", "Chưa chọn database!")
        return False

    if not table_name.strip():
        messagebox.showwarning("Cảnh báo", "Tên bảng không được để trống!")
        return False

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        if columns_definition.strip():
            sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_definition})"
        else:
            sql = f"CREATE TABLE IF NOT EXISTS {table_name} (id INTEGER PRIMARY KEY AUTOINCREMENT)"

        cursor.execute(sql)
        conn.commit()
        conn.close()

        messagebox.showinfo("Thành công", f"Đã tạo bảng '{table_name}' thành công!")
        return True

    except sqlite3.Error as e:
        messagebox.showerror("Lỗi", f"Không thể tạo bảng:\n{e}")
        return False


def drop_table(entry_database, table_name):
    """Xóa bảng trong database"""
    db_path = entry_database.get().strip()

    if not db_path:
        messagebox.showwarning("Cảnh báo", "Chưa chọn database!")
        return False

    if not table_name.strip():
        messagebox.showwarning("Cảnh báo", "Chưa chọn bảng để xóa!")
        return False

    confirm = messagebox.askyesno("Xác nhận", f"Bạn có chắc chắn muốn xóa bảng '{table_name}' không?")
    if not confirm:
        return False

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
        conn.commit()
        conn.close()
        messagebox.showinfo("Thành công", f"Đã xóa bảng '{table_name}'!")
        return True
    except sqlite3.Error as e:
        messagebox.showerror("Lỗi", f"Không thể xóa bảng:\n{e}")
        return False


# ================== Hàm nhập dữ liệu ==================
def choose_data(text_widget, scrollbar):
    """Chọn file dữ liệu từ dialog"""
    file_path = filedialog.askopenfilenames(
        title="Chọn file(CSV/JSON)",
        filetypes=[("CSV hoặc JSON", ("*.csv", "*.json"))]
    )
    if file_path:
        text_widget.delete("1.0", "end")
        text_widget.insert("1.0", "\n".join(file_path))
        auto_resize_text(text_widget, scrollbar)
    else:
        messagebox.showinfo("Thông tin", "Chưa chọn file nào!")


def auto_resize_text(text_widget, scrollbar, max_lines=5):
    """Tự động điều chỉnh kích thước text widget"""
    content = text_widget.get("1.0", "end").strip()
    if not content:
        num_lines = 1
    else:
        num_lines = content.count("\n") + 1

    new_height = min(num_lines, max_lines)
    text_widget.config(height=new_height)

    if num_lines > max_lines:
        scrollbar.grid()
    else:
        scrollbar.grid_remove()


def load_data(entry_db, entry_table, text_widget, tree=None, combo_x=None, combo_y=None):
    """Tải dữ liệu từ file vào database"""
    global last_df
    db_path = entry_db.get().strip()
    table_name = entry_table.get().strip()
    files_content = text_widget.get("1.0", "end").strip()

    if not db_path:
        messagebox.showwarning("Cảnh báo", "Chưa chọn database!")
        return None
    if not table_name:
        messagebox.showwarning("Cảnh báo", "Chưa nhập tên bảng!")
        return None
    if not files_content:
        messagebox.showwarning("Cảnh báo", "Chưa chọn file dữ liệu!")
        return None

    file_paths = [line.strip() for line in files_content.split("\n") if line.strip()]

    confirm = messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn tải dữ liệu?")
    if not confirm:
        return None

    dataframes = []
    for path in file_paths:
        try:
            if path.lower().endswith(".csv"):
                df = pd.read_csv(path)
            elif path.lower().endswith(".json"):
                with open(path, "r", encoding="utf-8") as f:
                    raw = json.load(f)
                if isinstance(raw, list):
                    df = pd.DataFrame(raw)
                elif isinstance(raw, dict):
                    df = pd.DataFrame([raw])
                else:
                    messagebox.showwarning("Cảnh báo", f"Dữ liệu JSON không hợp lệ: {path}")
                    continue

                for col in df.columns:
                    df[col] = df[col].apply(
                        lambda x: json.dumps(x, ensure_ascii=False) if isinstance(x, (list, dict)) else x
                    )
            else:
                continue

            df.columns = [col.strip().lower() for col in df.columns]
            dataframes.append(df)

        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi đọc file {path}:\n{e}")

    if not dataframes:
        messagebox.showwarning("Cảnh báo", "Không có file nào được tải!")
        return None

    merged_df = pd.concat(dataframes, ignore_index=True).drop_duplicates()

    try:
        conn = sqlite3.connect(db_path)

        try:
            existing_df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
        except pd.io.sql.DatabaseError:
            existing_df = pd.DataFrame()

        if not existing_df.empty and "id" in merged_df.columns:
            new_df = merged_df[~merged_df["id"].isin(existing_df["id"])]
        else:
            new_df = merged_df

        if new_df.empty:
            last_df = merged_df if not merged_df.empty else existing_df
            messagebox.showinfo("Thông báo", "Không có dữ liệu mới để thêm!")
        else:
            df_for_db = new_df.copy()
            for col in df_for_db.columns:
                df_for_db[col] = df_for_db[col].apply(
                    lambda x: json.dumps(x, ensure_ascii=False) if isinstance(x, (list, dict)) else x
                )

            df_for_db.to_sql(table_name, conn, if_exists="append", index=False)
            last_df = new_df

            if tree is not None:
                show_table_from_df(new_df, tree)
                if combo_x is not None and combo_y is not None:
                    update_column_options(new_df, combo_x, combo_y)

            messagebox.showinfo("Thành công", f"Đã thêm {len(new_df)} bản ghi vào bảng '{table_name}'!")

        conn.close()
        return table_name

    except sqlite3.Error as e:
        messagebox.showerror("Lỗi", f"Lỗi khi ghi dữ liệu:\n{e}")
        return None


def show_table_from_df(df, tree):
    """Hiển thị DataFrame lên Treeview"""
    if tree is None:
        return

    for item in tree.get_children():
        tree.delete(item)

    tree["columns"] = list(df.columns)
    tree["show"] = "headings"
    for col in df.columns:
        tree.heading(col, text=col)
        tree.column(col, width=120, anchor="w")

    for _, row in df.iterrows():
        tree.insert("", "end", values=list(row))


def update_column_options(df, combo_x, combo_y):
    """Cập nhật tùy chọn cột cho combobox"""
    cols = list(df.columns)
    combo_x["values"] = cols
    combo_y["values"] = cols

    combo_x.set("")
    combo_y.set("")

    def on_x_change(event):
        x_val = combo_x.get()
        combo_y["values"] = [c for c in cols if c != x_val]

    def on_y_change(event):
        y_val = combo_y.get()
        combo_x["values"] = [c for c in cols if c != y_val]

    combo_x.bind("<<ComboboxSelected>>", on_x_change)
    combo_y.bind("<<ComboboxSelected>>", on_y_change)


def load_table_data(entry_database, table_name, tree, combo_x, combo_y):
    """Tải dữ liệu từ bảng database"""
    global last_df
    db_path = entry_database.get().strip()

    if not db_path or not table_name:
        return

    try:
        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
        conn.close()

        if df.empty:
            messagebox.showinfo("Thông tin", f"Bảng '{table_name}' trống!")
        else:
            show_table_from_df(df, tree)
            update_column_options(df, combo_x, combo_y)
            last_df = df

    except sqlite3.Error as e:
        messagebox.showerror("Lỗi", f"Lỗi khi tải dữ liệu:\n{e}")


# ================== Hàm xử lý dữ liệu ==================
def parse_number(x):
    """Chuyển đổi chuỗi số thành float"""
    if pd.isna(x):
        return np.nan

    s = str(x).strip()
    if s == "":
        return np.nan

    s = s.replace('\u00A0', '').replace('\u2009', '').replace('\u202f', '').replace(' ', '')
    s = re.sub(r'[A-Za-z]', '', s)
    s = re.sub(r'[^\d,.\-]', '', s)

    if s == "" or s in ["-", ".", ","]:
        return np.nan

    if '.' in s and ',' in s:
        if s.rfind('.') > s.rfind(','):
            s = s.replace(',', '')
        else:
            s = s.replace('.', '')
            s = s.replace(',', '.')
    elif ',' in s:
        parts = s.split(',')
        if len(parts[-1]) == 3:
            s = s.replace(',', '')
        else:
            s = s.replace(',', '.')
    elif '.' in s:
        parts = s.split('.')
        if len(parts[-1]) == 3:
            s = s.replace('.', '')

    try:
        return float(s)
    except ValueError:
        return np.nan


# ================== Hàm vẽ biểu đồ ==================
def draw_chart(combo_chart, combo_x, combo_y, frame_chart):
    """Vẽ biểu đồ từ dữ liệu"""
    global last_df, current_fig
    if last_df is None or last_df.empty:
        messagebox.showwarning("Cảnh báo", "Chưa có dữ liệu!")
        return

    chart_type = combo_chart.get()
    col_x = combo_x.get()
    col_y = combo_y.get()

    if not col_x or not col_y:
        messagebox.showwarning("Cảnh báo", "Chưa chọn đủ cột dữ liệu!")
        return

    def extract_value(item, path):
        if isinstance(item, str):
            try:
                item = json.loads(item)
            except json.JSONDecodeError:
                pass

        parts = path.split(".") if path else []
        val = item
        for p in parts:
            if isinstance(val, list):
                if val and isinstance(val[0], dict):
                    val = val[0].get(p)
                else:
                    val = val[0] if val else None
            elif isinstance(val, dict):
                val = val.get(p)
            else:
                val = None

        if isinstance(val, str):
            try:
                val = float(val.replace(",", "").strip())
            except ValueError:
                val = None

        return val

    df = last_df.copy()

    if col_x in df.columns:
        col_x_use = col_x
    elif "." in col_x:
        root, sub = col_x.split(".", 1)
        df["_x_"] = df[root].apply(lambda v: extract_value(v, sub))
        col_x_use = "_x_"
    else:
        messagebox.showwarning("Cảnh báo", f"Cột X '{col_x}' không tồn tại!")
        return

    if col_y in ["prices", "price"] and "prices" in df.columns:
        df["_y_"] = df["prices"].apply(lambda v: extract_value(v, "price"))
        col_y_use = "_y_"
    elif "." in col_y:
        root, sub = col_y.split(".", 1)
        df["_y_"] = df[root].apply(lambda v: extract_value(v, sub))
        col_y_use = "_y_"
    elif col_y in df.columns:
        df["_y_"] = df[col_y].apply(lambda v: extract_value(v, ""))
        col_y_use = "_y_"
    else:
        messagebox.showwarning("Cảnh báo", f"Cột Y '{col_y}' không tồn tại!")
        return

    df["_parsed_y_"] = pd.to_numeric(df[col_y_use], errors="coerce")
    plot_df = df.dropna(subset=["_parsed_y_"])[[col_x_use, "_parsed_y_"]]

    for widget in frame_chart.winfo_children():
        widget.destroy()

    if plot_df.empty:
        messagebox.showerror("Lỗi", "Không có dữ liệu hợp lệ để vẽ!")
        return

    fig, ax = plt.subplots(figsize=(8, 4.5))
    current_fig = fig

    try:
        if chart_type == "Bar":
            ax.bar(plot_df[col_x_use].astype(str), plot_df["_parsed_y_"])
            ax.set_xlabel(col_x)
            ax.set_ylabel(col_y)
            ax.tick_params(axis="x", rotation=45)

        elif chart_type == "Pie":
            ax.pie(plot_df["_parsed_y_"], labels=plot_df[col_x_use].astype(str), autopct="%1.1f%%")
            ax.set_ylabel("")

        elif chart_type == "Line":
            ax.plot(plot_df[col_x_use].astype(str), plot_df["_parsed_y_"], marker="o")
            ax.set_xlabel(col_x)
            ax.set_ylabel(col_y)
            ax.tick_params(axis="x", rotation=45)

        elif chart_type == "Scatter":
            x_vals = plot_df[col_x_use]
            if not pd.api.types.is_numeric_dtype(x_vals):
                x_vals = pd.to_numeric(x_vals, errors="coerce")
            ax.scatter(x_vals, plot_df["_parsed_y_"])
            ax.set_xlabel(col_x)
            ax.set_ylabel(col_y)

        else:
            messagebox.showinfo("Thông báo", f"Loại biểu đồ '{chart_type}' chưa được hỗ trợ!")
            return

        canvas = FigureCanvasTkAgg(fig, master=frame_chart)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    except Exception as e:
        messagebox.showerror("Lỗi", f"Lỗi khi vẽ biểu đồ:\n{e}")


def save_chart():
    """Lưu biểu đồ thành file ảnh"""
    global current_fig
    if current_fig is None:
        messagebox.showwarning("Cảnh báo", "Chưa có biểu đồ để lưu!")
        return

    file_path = filedialog.asksaveasfilename(
        title="Lưu biểu đồ",
        defaultextension=".png",
        filetypes=[("PNG Image", "*.png"), ("JPEG Image", "*.jpg"), ("All files", "*.*")]
    )

    if not file_path:
        return

    try:
        current_fig.savefig(file_path, dpi=300, bbox_inches="tight")
        messagebox.showinfo("Thành công", f"Đã lưu biểu đồ tại:\n{file_path}")
    except Exception as e:
        messagebox.showerror("Lỗi", f"Lỗi khi lưu biểu đồ:\n{e}")


# ================== Hàm xử lý SQL ==================
def execute_sql(entry_database, sql_text, tree, combo_x, combo_y):
    """Thực thi câu lệnh SQL"""
    global last_df

    db_path = entry_database.get().strip()
    query = sql_text.get("1.0", "end").strip()

    if not db_path:
        messagebox.showwarning("Cảnh báo", "Chưa chọn database!")
        return

    if not query:
        messagebox.showwarning("Cảnh báo", "Chưa nhập câu lệnh SQL!")
        return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        if query.strip().lower().startswith("select"):
            df = pd.read_sql_query(query, conn)
            if df.empty:
                messagebox.showinfo("Thông tin", "Truy vấn không trả về kết quả!")
            else:
                show_table_from_df(df, tree)
                update_column_options(df, combo_x, combo_y)
                last_df = df
        else:
            cursor.execute(query)
            conn.commit()
            messagebox.showinfo("Thành công", f"Đã thực thi SQL!\nSố dòng ảnh hưởng: {cursor.rowcount}")

    except sqlite3.Error as e:
        messagebox.showerror("Lỗi SQL", f"Lỗi khi thực thi SQL:\n{e}")


# ================== Hàm xuất dữ liệu ==================
def export_data(combo_format):
    """Xuất dữ liệu ra file"""
    global last_df

    if last_df is None or last_df.empty:
        messagebox.showwarning("Cảnh báo", "Chưa có dữ liệu để xuất!")
        return

    export_format = combo_format.get()
    if not export_format:
        messagebox.showwarning("Cảnh báo", "Chưa chọn định dạng xuất!")
        return

    if export_format.lower() == "csv":
        file_path = filedialog.asksaveasfilename(
            title="Xuất file CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if file_path:
            try:
                last_df.to_csv(file_path, index=False, encoding='utf-8-sig')
                messagebox.showinfo("Thành công", f"Đã xuất CSV tới:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Lỗi khi xuất CSV:\n{e}")

    elif export_format.lower() == "json":
        file_path = filedialog.asksaveasfilename(
            title="Xuất file JSON",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            try:
                # Kiểm tra xem phương thức to_json có hỗ trợ ensure_ascii không
                try:
                    last_df.to_json(file_path, orient='records', indent=2, ensure_ascii=False)
                except TypeError:
                    # Nếu không hỗ trợ ensure_ascii, thử không dùng tham số này
                    last_df.to_json(file_path, orient='records', indent=2)
                messagebox.showinfo("Thành công", f"Đã xuất JSON tới:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Lỗi khi xuất JSON:\n{e}")


def clear_table(database_path, table_name):
    """Xóa toàn bộ dữ liệu trong bảng"""
    if not database_path or not table_name:
        messagebox.showwarning("Cảnh báo", "Chưa chọn database hoặc bảng!")
        return False

    confirm = messagebox.askyesno("Xác nhận", f"Xóa toàn bộ dữ liệu trong bảng '{table_name}'?")
    if not confirm:
        return False

    try:
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM {table_name}")
        conn.commit()
        conn.close()
        messagebox.showinfo("Thành công", f"Đã xóa dữ liệu trong bảng '{table_name}'!")
        return True
    except sqlite3.Error as e:
        messagebox.showerror("Lỗi", f"Lỗi khi xóa dữ liệu:\n{e}")
        return False


def clone():
    """Hàm clone (chưa implement)"""
    pass
