import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from Function.Function import *

# ===== Frame nhập liệu =====
frame_input = tk.Frame(root)
frame_input.pack(fill="x", padx=5, pady=5)
#Dòng 0
tk.Label(frame_input, text="Link (CSV/JSON):", font=("Arial", 14)).grid(row=0, column=0, sticky="w", padx=5, pady=5)
Entry_link = tk.Entry(frame_input, font=("Arial", 14), width=60)
Entry_link.grid(row=0, column=1, sticky="w", padx=5, pady=5)
tk.Button(frame_input, text="Chọn...", font=("Arial", 12), command=Choose_link).grid(row=0, column=2, sticky="w", padx=5, pady=5)
tk.Button(frame_input, text="Lấy data", font=("Arial", 12), command=clone).grid(row=0, column=4, padx=5, pady=5)
#Dòng 1
tk.Label(frame_input, text="Database:", font=("Arial", 14)).grid(row=1, column=0, sticky="w", padx=5, pady=5)
Entry_database = tk.Entry(frame_input, font=("Arial", 14), width=40)
Entry_database.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
tk.Button(frame_input, text="Chọn...", font=("Arial", 12), command=Choose_database).grid(row=1, column=2, padx=5, pady=5)
tk.Button(frame_input, text="Tạo", font=("Arial", 12), command=Create_database).grid(row=1, column=3, padx=5, pady=5)

#Dòng 2
table_name_var = tk.StringVar()

def on_table_name_change(*args):
    if table_name_var.get().strip():
        load_columns()

table_name_var.trace_add("write", on_table_name_change)

tk.Label(frame_input, text="Bảng:", font=("Arial", 14)).grid(row=2, column=0, sticky="w", padx=5, pady=5)
Entry_table = tk.Entry(frame_input, font=("Arial", 14), textvariable=table_name_var)
Entry_table.grid(row=2, column=1, sticky="w", padx=5, pady=5)
#dòng 3
# ===== Frame thiết lập biểu đồ =====
frame_opts = tk.Frame(root, padx=5, pady=5)
frame_opts.pack(fill="x")

tk.Label(frame_opts, text="Loại biểu đồ:", font=("Arial", 14)).grid(row=0, column=0, padx=(5, 2), pady=5, sticky="w")
selected_chart = tk.StringVar()
combo_chart = ttk.Combobox(frame_opts, textvariable=selected_chart, values=["Bar", "Pie", "Scatter", "Line"], font=("Arial", 12), state="readonly", width=10)
combo_chart.grid(row=0, column=1, padx=(0, 10), pady=2, sticky="w")

tk.Label(frame_opts, text="Cột X (nhóm):", font=("Arial", 14)).grid(row=0, column=2, padx=(10, 2), pady=5, sticky="w")
selected_x = tk.StringVar()
combo_x = ttk.Combobox(frame_opts, textvariable=selected_x, values=[], font=("Arial", 12), state="readonly", width=12)
combo_x.grid(row=0, column=3, padx=(0, 10), pady=2, sticky="w")

tk.Label(frame_opts, text="Cột Y (giá trị):", font=("Arial", 14)).grid(row=0, column=4, padx=(10, 2), pady=5, sticky="w")
selected_y = tk.StringVar()
combo_y = ttk.Combobox(frame_opts, textvariable=selected_y, values=[], font=("Arial", 12), state="readonly", width=12)
combo_y.grid(row=0, column=5, padx=(0, 10), pady=2, sticky="w")

tk.Button(frame_opts, text="Chạy SQL & vẽ", font=("Arial", 12), command=draw_chart).grid(row=0, column=6, padx=10)
tk.Button(frame_opts, text="Lưu ảnh", font=("Arial", 12), command=save_chart).grid(row=0, column=7, padx=5)

#Dòng 4
# ===== Frame SQL =====
frame_sql = tk.LabelFrame(root, text="Câu lệnh SQL", font=("Arial", 12), padx=10, pady=5)
frame_sql.pack(fill="x", padx=10, pady=5)

sql_text = tk.Text(frame_sql, font=("Consolas", 12), height=5)
sql_text.pack(fill="x", padx=5, pady=5, expand=True)

btn_execute = tk.Button(frame_sql, text="Thực thi SQL", font=("Arial", 12), command=execute_sql)
btn_execute.pack(anchor="e", padx=10, pady=5)

# ===== Frame hiển thị biểu đồ =====
frame_chart = tk.LabelFrame(root, text="Biểu đồ", font=("Arial", 12), padx=10, pady=5)
frame_chart.pack(fill="both", expand=True, padx=10, pady=5)

root.mainloop()