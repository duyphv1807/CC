import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from Function.Function_def import *

# ====================== Giao diện ======================
root = tk.Tk()
root.title("MENU")
# ===== Frame nhập liệu =====
frame_input = tk.Frame(root)
frame_input.pack(fill="x", padx=5, pady=5)

#Dòng 1
# Label
tk.Label(frame_input, text="Link (CSV/JSON):", font=("Arial", 12)).grid(
    row=1, column=0, sticky="w", padx=5, pady=5
)

# Text widget
text_widget = tk.Text(
    frame_input,
    font=("Arial", 12),
    width=60,
    height=1,
    wrap="none"
)
text_widget.grid(row=1, column=1, sticky="ew", padx=(5, 0), pady=5)

# Scrollbar nằm chung ô với Text (column=1)
scroll = tk.Scrollbar(frame_input, orient="vertical", command=text_widget.yview)
text_widget.config(yscrollcommand=scroll.set)
scroll.grid(row=1, column=1, sticky="nse", padx=(0, 0))  # ép vào cạnh phải
scroll.grid_remove()  # ẩn mặc định

# Nút chọn file
tk.Button(
    frame_input,
    text="Chọn...",
    font=("Arial", 12),
    command=lambda: Choose_data(text_widget, scroll)
).grid(row=1, column=2, sticky="w", padx=5, pady=5)

# Nút lấy data
tk.Button(
    frame_input,
    text="Chèn",
    font=("Arial", 12),
    command=lambda: Load_data(Entry_database, Entry_table, text_widget, tree, combo_x, combo_y)
).grid(row=1, column=3, padx=5, pady=5)

# Cho cột 1 (Text) giãn đều
frame_input.grid_columnconfigure(1, weight=1)
#Dòng 0
tk.Label(frame_input, text="Database:", font=("Arial", 12)).grid(row=0, column=0, sticky="w", padx=5, pady=5)
Entry_database = tk.Entry(frame_input, font=("Arial", 12), width=40)
Entry_database.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
tk.Button(frame_input, text="Chọn...", font=("Arial", 12), command=lambda: Choose_database(Entry_database)).grid(row=0, column=2, padx=5, pady=5)
tk.Button(frame_input, text="Tạo", font=("Arial", 12), command=lambda: Create_database(Entry_database)).grid(row=0, column=3, sticky="w", padx=5, pady=5)

#Dòng 2
table_name_var = tk.StringVar()

tk.Label(frame_input, text="Bảng:", font=("Arial", 12)).grid(row=2, column=0, sticky="w", padx=5, pady=5)
Entry_table = tk.Entry(frame_input, font=("Arial", 12), textvariable=table_name_var)
Entry_table.grid(row=2, column=1, sticky="w", padx=5, pady=5)
#dòng 3
# ===== Frame thiết lập biểu đồ =====
frame_opts = tk.Frame(root, padx=5, pady=5)
frame_opts.pack(fill="x")

tk.Label(frame_opts, text="Loại biểu đồ:", font=("Arial", 12)).grid(row=0, column=0, padx=(5, 2), pady=5, sticky="w")
selected_chart = tk.StringVar()
combo_chart = ttk.Combobox(frame_opts, textvariable=selected_chart, values=["Bar", "Pie", "Scatter", "Line"], font=("Arial", 12), state="readonly", width=10)
combo_chart.grid(row=0, column=1, padx=(0, 10), pady=2, sticky="w")

tk.Label(frame_opts, text="Cột X (nhóm):", font=("Arial", 12)).grid(row=0, column=2, padx=(10, 2), pady=5, sticky="w")
selected_x = tk.StringVar()
combo_x = ttk.Combobox(frame_opts, textvariable=selected_x, values=[], font=("Arial", 12), state="readonly", width=12)
combo_x.grid(row=0, column=3, padx=(0, 10), pady=2, sticky="w")

tk.Label(frame_opts, text="Cột Y (giá trị):", font=("Arial", 12)).grid(row=0, column=4, padx=(10, 2), pady=5, sticky="w")
selected_y = tk.StringVar()
combo_y = ttk.Combobox(frame_opts, textvariable=selected_y, values=[], font=("Arial", 12), state="readonly", width=12)
combo_y.grid(row=0, column=5, padx=(0, 10), pady=2, sticky="w")

tk.Button(frame_opts, text="Vẽ", font=("Arial", 12), command=lambda: Draw_chart(combo_chart, combo_x, combo_y, frame_chart)).grid(row=0, column=6, padx=10)
tk.Button(frame_opts, text="Lưu ảnh", font=("Arial", 12), command=Save_chart).grid(row=0, column=7, padx=5)

#Dòng 4
# ===== Frame SQL =====
frame_sql = tk.LabelFrame(root, text="Câu lệnh SQL", font=("Arial", 12), padx=10, pady=5)
frame_sql.pack(fill="x", padx=10, pady=5)

sql_text = tk.Text(frame_sql, font=("Consolas", 12), height=5)
sql_text.pack(fill="x", padx=5, pady=5, expand=True)

btn_execute = tk.Button(frame_sql, text="Thực thi SQL", font=("Arial", 12), command=lambda:Excute_sql(Entry_database, sql_text, tree, combo_x, combo_y))
btn_execute.pack(anchor="e", padx=10, pady=5)

# ===== Frame Dự đoán =====
frame_predict = tk.LabelFrame(root, text="Dự đoán", font=("Arial", 12), padx=10, pady=5)
frame_predict.pack(fill="x", padx=10, pady=5)

combo_predict = ttk.Combobox(frame_predict, values=[], font=("Arial", 12), state="readonly", width=20)
combo_predict.pack(side="left", padx=5)

btn_predict = tk.Button(frame_predict, text="Dự đoán", font=("Arial", 12), command=clone)
btn_predict.pack(side="right", padx=5)

# ===== Frame hiển thị biểu đồ =====
frame_chart = tk.LabelFrame(root, text="Biểu đồ", font=("Arial", 12), padx=10, pady=5)
frame_chart.pack(fill="both", expand=True, padx=10, pady=5)

# ===== Frame hiển thị dữ liệu =====
frame_table = tk.LabelFrame(root, text=f"Dữ liệu trong bảng", font=("Arial", 12), padx=10, pady=5)
frame_table.pack(fill="both", expand=True, padx=10, pady=5)

tree = ttk.Treeview(frame_table)
tree.pack(fill="both", expand=True)

root.mainloop()
