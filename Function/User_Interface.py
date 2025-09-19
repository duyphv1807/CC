import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import datetime
import pandas as pd

# Import app-specific helper functions (keep as single import if functions used widely)
from Function.Function_def import *


# ====================== Custom Styles & Colors ======================
class ColorScheme:
    # Modern color palette
    PRIMARY = "#1E3A5F"
    SECONDARY = "#4A90E2"
    SUCCESS = "#52C41A"
    WARNING = "#FA8C16"
    ERROR = "#F5222D"

    BG_DARK = "#001529"
    BG_MAIN = "#F0F2F5"
    BG_CARD = "#FFFFFF"

    TEXT_PRIMARY = "#262626"
    TEXT_SECONDARY = "#8C8C8C"
    TEXT_WHITE = "#FFFFFF"

    BORDER = "#D9D9D9"
    SHADOW = "#00000019"


def setup_modern_styles():
    style = ttk.Style()
    try:
        style.theme_use('clam')
    except Exception:
        # If 'clam' not available, keep default theme
        pass

    # Configure modern button styles
    style.configure("Primary.TButton",
                    font=("Segoe UI", 10, "bold"),
                    borderwidth=0,
                    relief="flat",
                    padding=(15, 10))

    style.map("Primary.TButton",
              background=[('active', ColorScheme.SECONDARY),
                          ('!active', ColorScheme.PRIMARY)],
              foreground=[('active', 'white'), ('!active', 'white')])

    style.configure("Success.TButton",
                    font=("Segoe UI", 10),
                    borderwidth=0,
                    relief="flat",
                    padding=(12, 8))

    style.map("Success.TButton",
              background=[('active', '#73D13D'),
                          ('!active', ColorScheme.SUCCESS)],
              foreground=[('active', 'white'), ('!active', 'white')])

    style.configure("Danger.TButton",
                    font=("Segoe UI", 10),
                    borderwidth=0,
                    relief="flat",
                    padding=(12, 8))

    style.map("Danger.TButton",
              background=[('active', ColorScheme.ERROR),
                          ('!disabled', '#FF4D4F')],
              foreground=[('active', 'white'), ('!disabled', 'white')])

    # Configure combobox style
    style.configure("Modern.TCombobox",
                    fieldbackground="white",
                    borderwidth=1,
                    relief="solid")


class ModernCard(tk.Frame):
    def __init__(self, parent, title="", icon="", **kwargs):
        super().__init__(parent, bg=ColorScheme.BG_CARD, relief="flat", **kwargs)

        # Add subtle border
        self.configure(highlightbackground=ColorScheme.BORDER,
                       highlightthickness=1)

        if title:
            header = tk.Frame(self, bg=ColorScheme.BG_CARD)
            header.pack(fill="x", padx=20, pady=(10, 8))
            header.pack_propagate(False)

            title_label = tk.Label(header,
                                   text=f"{icon}  {title}" if icon else title,
                                   font=("Segoe UI", 13, "bold"),
                                   bg=ColorScheme.BG_CARD,
                                   fg=ColorScheme.TEXT_PRIMARY,
                                   anchor="nw",
                                   justify="left")
            title_label.pack(side="left", anchor="nw", pady=2)


# ====================== Main ======================
class Dashboard:
    def update_clock(self):
        """Update the clock label every second."""
        now = datetime.datetime.now().strftime("%d/%m/%Y - %H:%M:%S")
        if self.clock_label is not None:
            self.clock_label.config(text=f"🕐 {now}")
        # schedule next update
        if hasattr(self, 'root') and self.root is not None:
            self.root.after(1000, self.update_clock)

    def __init__(self, main_window):
        # Window
        self.root = main_window
        self.root.title("Test")
        self.root.geometry("1400x900")
        self.root.configure(bg=ColorScheme.BG_MAIN)

        # Initialize instance attributes here (avoid defining them elsewhere)
        self.clock_label = None
        self.entry_database = None
        self.entry_table = None
        self.text_widget = None
        self.scroll = None
        self.preview_notebook = None
        self.table_listbox = None
        self.delete_table_button = None
        self.current_selected_table = None
        self.combo_chart = None
        self.combo_x = None
        self.combo_y = None
        self.frame_chart = None
        self.sql_text = None
        self.combo_export = None
        self.tree_sql = None
        self.combo_model = None
        self.entry_year = None
        self.prediction_frame = None

        # Save created treeviews/tabs for preview
        self.table_views = {}

        # Setup styles
        setup_modern_styles()

        # Create main layout
        self.create_layout()

    def create_layout(self):
        # Top Navigation Bar
        self.create_navbar()

        # Main Container
        main_container = tk.Frame(self.root, bg=ColorScheme.BG_MAIN)
        main_container.pack(fill="both", expand=True)

        # Main Content Area
        content_area = tk.Frame(main_container, bg=ColorScheme.BG_MAIN)
        content_area.pack(side="left", fill="both", expand=True, padx=(0, 20), pady=20)

        # Dashboard Header with Stats
        self.create_dashboard_header(content_area)

        # Main Work Area
        work_area = tk.Frame(content_area, bg=ColorScheme.BG_MAIN)
        work_area.pack(fill="both", expand=True, pady=(20, 0))

        # Create tabbed interface
        self.create_tabbed_interface(work_area)

    def create_navbar(self):
        """Top navigation bar with title and clock."""
        navbar = tk.Frame(self.root, bg=ColorScheme.PRIMARY, height=60)
        navbar.pack(fill="x")
        navbar.pack_propagate(False)

        # App title
        title_frame = tk.Frame(navbar, bg=ColorScheme.PRIMARY)
        title_frame.pack(side="left", padx=20, fill="y")

        tk.Label(title_frame,
                 text="Menu",
                 font=("Segoe UI", 16, "bold"),
                 bg=ColorScheme.PRIMARY,
                 fg=ColorScheme.TEXT_WHITE).pack(expand=True)

        # Right side info
        info_frame = tk.Frame(navbar, bg=ColorScheme.PRIMARY)
        info_frame.pack(side="right", padx=20, fill="y")

        # Clock label
        self.clock_label = tk.Label(info_frame,
                                    text="",
                                    font=("Segoe UI", 10),
                                    bg=ColorScheme.PRIMARY,
                                    fg=ColorScheme.TEXT_WHITE)
        self.clock_label.pack(side="right", expand=True)

        # Start the clock updates
        self.update_clock()

    def create_dashboard_header(self, parent):
        """Header area for dashboard title / stats."""
        header_frame = tk.Frame(parent, bg=ColorScheme.BG_MAIN)
        header_frame.pack(fill="x")

        tk.Label(header_frame,
                 text="Bảng Điều Khiển",
                 font=("Segoe UI", 18, "bold"),
                 bg=ColorScheme.BG_MAIN,
                 fg=ColorScheme.TEXT_PRIMARY).pack(anchor="w", pady=(0, 15))

    def create_tabbed_interface(self, parent):
        """Main tabbed interface."""
        notebook = ttk.Notebook(parent)
        notebook.pack(fill="both", expand=True)

        # Tabs
        self.create_data_import_tab(notebook)
        self.create_visualization_tab(notebook)
        self.create_sql_tab(notebook)
        self.create_prediction_tab(notebook)

    def create_data_import_tab(self, notebook):
        """Create data import tab with redesigned layout for more space"""
        tab = tk.Frame(notebook, bg=ColorScheme.BG_MAIN)
        notebook.add(tab, text="   📥 Nhập Dữ Liệu   ")

        # Left (config) and right (preview)
        left_column = tk.Frame(tab, bg=ColorScheme.BG_MAIN, width=400)
        left_column.pack(side="left", fill="y", padx=20, pady=20)

        right_column = tk.Frame(tab, bg=ColorScheme.BG_MAIN)
        right_column.pack(side="right", fill="both", expand=True, padx=20, pady=20)

        # Database section (left)
        db_card = ModernCard(left_column, "Cấu Hình Cơ Sở Dữ Liệu", "🗄️")
        db_card.pack(fill="x", pady=(0, 10))

        db_content = tk.Frame(db_card, bg=ColorScheme.BG_CARD)
        db_content.pack(fill="x", padx=20, pady=(0, 20))

        # Database path row
        db_row1 = tk.Frame(db_content, bg=ColorScheme.BG_CARD)
        db_row1.pack(fill="x", pady=5)

        tk.Label(db_row1,
                 text="Đường dẫn CSDL:",
                 font=("Segoe UI", 10),
                 bg=ColorScheme.BG_CARD,
                 fg=ColorScheme.TEXT_PRIMARY,
                 width=15,
                 anchor="w").pack(side="left")

        self.entry_database = tk.Entry(db_row1,
                                       font=("Segoe UI", 10),
                                       relief="solid",
                                       bd=1)
        self.entry_database.pack(side="left", fill="x", expand=True, padx=(0, 10))

        ttk.Button(db_row1,
                   text="Chọn DB",
                   command=lambda: choose_database(self.entry_database)).pack(side="left", padx=2)

        ttk.Button(db_row1,
                   text="➕ Tạo mới",
                   style="Success.TButton",
                   command=lambda: create_database(self.entry_database)).pack(side="left", padx=2)

        # Table name row
        db_row2 = tk.Frame(db_content, bg=ColorScheme.BG_CARD)
        db_row2.pack(fill="x", pady=5)

        tk.Label(db_row2,
                 text="Tên bảng:",
                 font=("Segoe UI", 10),
                 bg=ColorScheme.BG_CARD,
                 fg=ColorScheme.TEXT_PRIMARY,
                 width=15,
                 anchor="w").pack(side="left")

        self.entry_table = tk.Entry(db_row2,
                                    font=("Segoe UI", 10),
                                    relief="solid",
                                    bd=1,
                                    width=30)
        self.entry_table.pack(side="left")

        # File import section (left)
        file_card = ModernCard(left_column, "Nhập Liệu Từ File", "📁")
        file_card.pack(fill="x", pady=10)

        file_content = tk.Frame(file_card, bg=ColorScheme.BG_CARD)
        file_content.pack(fill="x", padx=20, pady=(0, 20))

        file_row = tk.Frame(file_content, bg=ColorScheme.BG_CARD)
        file_row.pack(fill="x")

        tk.Label(file_row,
                 text="File dữ liệu:",
                 font=("Segoe UI", 10),
                 bg=ColorScheme.BG_CARD,
                 fg=ColorScheme.TEXT_PRIMARY,
                 width=15,
                 anchor="nw").pack(side="left")

        # Text widget for files
        text_frame = tk.Frame(file_row, relief="solid", bd=1, bg="white")
        text_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.text_widget = tk.Text(text_frame,
                                   font=("Consolas", 10),
                                   height=4,
                                   wrap="none",
                                   relief="flat",
                                   bg="white")
        self.text_widget.pack(side="left", fill="both", expand=True)

        self.scroll = tk.Scrollbar(text_frame, orient="vertical", command=self.text_widget.yview)
        self.scroll.pack(side="right", fill="y")
        self.text_widget.config(yscrollcommand=self.scroll.set)

        btn_frame = tk.Frame(file_row, bg=ColorScheme.BG_CARD)
        btn_frame.pack(side="left")

        ttk.Button(btn_frame,
                   text="📂 Chọn file",
                   command=lambda: choose_data(self.text_widget, self.scroll)).pack(pady=2)

        ttk.Button(btn_frame,
                   text="⬆️ Tải lên",
                   style="Primary.TButton",
                   command=self.on_load_data).pack(pady=2)

        # Table management section (left)
        self.create_table_management_section(left_column)

        # Data preview (right - larger space with notebook for multiple "sheets")
        preview_card = ModernCard(right_column, "Xem Trước Dữ Liệu", "👁️")
        preview_card.pack(fill="both", expand=True)

        # Add notebook for multiple table views (like sheets)
        self.preview_notebook = ttk.Notebook(preview_card)
        self.preview_notebook.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    def create_table_management_section(self, parent):
        """Create the table management area (left column)."""
        table_mgmt_card = ModernCard(parent, "Quản Lý Bảng", "📋")
        table_mgmt_card.pack(fill="x", pady=10)

        mgmt_content = tk.Frame(table_mgmt_card, bg=ColorScheme.BG_CARD)
        mgmt_content.pack(fill="x", padx=20, pady=(0, 20))

        table_list_frame = tk.Frame(mgmt_content, bg=ColorScheme.BG_CARD)
        table_list_frame.pack(fill="x", pady=5)

        tk.Label(table_list_frame,
                 text="Danh sách bảng:",
                 font=("Segoe UI", 10),
                 bg=ColorScheme.BG_CARD,
                 fg=ColorScheme.TEXT_PRIMARY).pack(side="left", padx=(0, 10))

        self.table_listbox = tk.Listbox(table_list_frame,
                                        font=("Segoe UI", 9),
                                        height=4,
                                        relief="solid",
                                        bd=1)
        self.table_listbox.pack(side="left", fill="both", expand=True, padx=(0, 10))

        table_scroll = tk.Scrollbar(table_list_frame, orient="vertical", command=self.table_listbox.yview)
        table_scroll.pack(side="right", fill="y")
        self.table_listbox.config(yscrollcommand=table_scroll.set)

        # Bind event click into listbox to show preview
        self.table_listbox.bind("<<ListboxSelect>>", self.on_table_select)

        btn_mgmt_frame = tk.Frame(mgmt_content, bg=ColorScheme.BG_CARD)
        btn_mgmt_frame.pack(fill="x", pady=(10, 0))

        ttk.Button(btn_mgmt_frame,
                   text="🔄 Làm mới danh sách",
                   command=self.refresh_table_list).pack(side="left", padx=(0, 10))

        # Delete table button (initially disabled)
        self.delete_table_button = ttk.Button(btn_mgmt_frame,
                                              text="🗑️ Xóa bảng này",
                                              style="Danger.TButton",
                                              command=self.on_drop_table_from_preview)
        self.delete_table_button.pack(side="right")
        self.delete_table_button.config(state="disabled")

    def on_table_select(self, event=None):
        """When selecting a table from the listbox, show preview in notebook."""
        selection = self.table_listbox.curselection()
        if not selection:
            # no selection -> disable
            self.delete_table_button.config(state="disabled")
            self.current_selected_table = None
            return

        table_name = self.table_listbox.get(selection[0])
        if table_name == "Không có bảng nào":
            self.delete_table_button.config(state="disabled")
            self.current_selected_table = None
            return

        # If tab already exists, switch to it
        if table_name in self.table_views:
            self.preview_notebook.select(self.table_views[table_name]['frame'])
        else:
            # create new tab with a Treeview
            tab_frame = tk.Frame(self.preview_notebook, bg=ColorScheme.BG_CARD)
            self.preview_notebook.add(tab_frame, text=table_name)

            tree_frame = tk.Frame(tab_frame, bg=ColorScheme.BG_CARD)
            tree_frame.pack(fill="both", expand=True)

            tree = ttk.Treeview(tree_frame)

            vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
            tree.configure(yscrollcommand=vsb.set)

            hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
            tree.configure(xscrollcommand=hsb.set)

            tree.grid(row=0, column=0, sticky="nsew")
            vsb.grid(row=0, column=1, sticky="ns")
            hsb.grid(row=1, column=0, sticky="ew")

            tree_frame.grid_rowconfigure(0, weight=1)
            tree_frame.grid_columnconfigure(0, weight=1)

            # Load data from DB into tree
            load_table_data(self.entry_database, table_name, tree, self.combo_x, self.combo_y)

            # Save reference
            self.table_views[table_name] = {'frame': tab_frame, 'tree': tree}

            # Select the newly created tab
            self.preview_notebook.select(tab_frame)

        # Enable delete button and save current selection
        self.current_selected_table = table_name
        self.delete_table_button.config(state="normal")

    def on_drop_table_from_preview(self):
        """Delete the currently selected table from the database and UI."""
        table_name = self.current_selected_table
        if not table_name:
            return

        # Confirm deletion with user (optional)
        if not messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn xóa bảng '{table_name}'?"):
            return

        # Drop table in DB
        try:
            success = drop_table(self.entry_database, table_name)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể xóa bảng: {e}")
            return

        if success:
            # remove tab if present
            if table_name in self.table_views:
                self.preview_notebook.forget(self.table_views[table_name]['frame'])
                del self.table_views[table_name]

            # refresh table list
            self.refresh_table_list()

            # reset selection
            self.delete_table_button.config(state="disabled")
            self.current_selected_table = None

    def refresh_table_list(self):
        """Refresh the list of tables in the listbox."""
        self.table_listbox.delete(0, tk.END)
        try:
            tables = get_table_list(self.entry_database)
        except Exception as e:
            # show error and early return
            messagebox.showerror("Lỗi", f"Không thể lấy danh sách bảng: {e}")
            return

        if not tables:
            self.table_listbox.insert(0, "Không có bảng nào")
        else:
            for table in tables:
                self.table_listbox.insert(tk.END, table)

    def create_visualization_tab(self, notebook):
        """Visualization tab with chart configuration and display."""
        tab = tk.Frame(notebook, bg=ColorScheme.BG_MAIN)
        notebook.add(tab, text="   📊 Trực Quan Hóa   ")

        # Chart configuration card
        config_card = ModernCard(tab, "Cấu Hình Biểu Đồ", "⚙️")
        config_card.pack(fill="x", padx=20, pady=(20, 10))

        config_content = tk.Frame(config_card, bg=ColorScheme.BG_CARD)
        config_content.pack(fill="x", padx=20, pady=(0, 20))

        row1 = tk.Frame(config_content, bg=ColorScheme.BG_CARD)
        row1.pack(fill="x", pady=5)

        tk.Label(row1,
                 text="Loại biểu đồ:",
                 font=("Segoe UI", 10),
                 bg=ColorScheme.BG_CARD,
                 width=12,
                 anchor="w").pack(side="left", padx=(0, 10))

        self.combo_chart = ttk.Combobox(row1,
                                        values=["Bar", "Pie", "Line", "Scatter"],
                                        font=("Segoe UI", 10),
                                        state="readonly",
                                        width=15)
        self.combo_chart.pack(side="left", padx=5)
        self.combo_chart.set("Bar")

        tk.Label(row1,
                 text="Trục X:",
                 font=("Segoe UI", 10),
                 bg=ColorScheme.BG_CARD,
                 width=8,
                 anchor="e").pack(side="left", padx=(20, 5))

        self.combo_x = ttk.Combobox(row1,
                                    values=[],
                                    font=("Segoe UI", 10),
                                    state="readonly",
                                    width=15)
        self.combo_x.pack(side="left", padx=5)

        tk.Label(row1,
                 text="Trục Y:",
                 font=("Segoe UI", 10),
                 bg=ColorScheme.BG_CARD,
                 width=8,
                 anchor="e").pack(side="left", padx=(20, 5))

        self.combo_y = ttk.Combobox(row1,
                                    values=[],
                                    font=("Segoe UI", 10),
                                    state="readonly",
                                    width=15)
        self.combo_y.pack(side="left", padx=5)

        ttk.Button(row1,
                   text="Vẽ biểu đồ",
                   style="Primary.TButton",
                   command=lambda: draw_chart(
                       self.combo_chart, self.combo_x, self.combo_y, self.frame_chart
                   )).pack(side="left", padx=(20, 5))

        ttk.Button(row1,
                   text="💾 Lưu",
                   style="Success.TButton",
                   command=save_chart).pack(side="left", padx=5)

        # Chart display card
        chart_card = ModernCard(tab, "Biểu Đồ")
        chart_card.pack(fill="both", expand=True, padx=20, pady=10)

        self.frame_chart = tk.Frame(chart_card, bg=ColorScheme.BG_CARD)
        self.frame_chart.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    @staticmethod
    def get_main_and_numeric_fields(df):
        """Return (main_fields, numeric_fields) from a dataframe.

        - main_fields: scalar/categorical columns (skip nested list/dict).
        - numeric_fields: numeric columns.
        """
        if df is None or df.empty:
            return [], []

        main_fields = []
        numeric_fields = []

        for col in df.columns:
            ser = df[col]
            non_null = ser.dropna()
            sample = non_null.iloc[0] if len(non_null) > 0 else None

            # Skip nested values
            if isinstance(sample, (list, dict)):
                continue

            # Numeric dtype
            if pd.api.types.is_numeric_dtype(ser):
                main_fields.append(col)
                numeric_fields.append(col)
                continue

            if sample is None:
                main_fields.append(col)
                continue

            if isinstance(sample, (int, float, bool)):
                main_fields.append(col)
                numeric_fields.append(col)
                continue

            if isinstance(sample, str):
                main_fields.append(col)
                continue

            # fallback
            main_fields.append(col)

        if 'prices' in df.columns:
            if 'price' not in numeric_fields:
                numeric_fields.insert(0, 'price')
            if 'price' not in main_fields:
                main_fields.insert(0, 'price')

        return main_fields, numeric_fields

    def populate_combo_fields(self, df=None):
        """Populate X/Y comboboxes from a dataframe (last loaded DF if df None)."""
        # prefer passed df; otherwise use last_df from Function_def if available
        if df is None:
            try:
                from Function import Function_def
                df = Function_def.last_df
            except Exception:
                df = None

        if df is None or df.empty:
            if self.combo_x is not None:
                self.combo_x['values'] = []
                self.combo_x.set('')
            if self.combo_y is not None:
                self.combo_y['values'] = []
                self.combo_y.set('')
            return

        main_fields, numeric_fields = self.get_main_and_numeric_fields(df)

        if self.combo_x is not None:
            self.combo_x['values'] = main_fields
            if main_fields:
                self.combo_x.set(main_fields[0])

        y_values = numeric_fields if numeric_fields else main_fields
        if self.combo_y is not None:
            self.combo_y['values'] = y_values
            if y_values:
                self.combo_y.set(y_values[0])

    def on_load_data(self):
        """Wrapper: load dữ liệu, refresh list, and open preview for created table."""
        try:
            created_table = load_data(self.entry_database, self.entry_table, self.text_widget,
                                      None, self.combo_x, self.combo_y)

            # If user canceled or nothing created, refresh list and exit
            if not created_table:
                self.refresh_table_list()
                return

            # Refresh table list
            self.refresh_table_list()

            # If created table exists in listbox, select it and open preview
            all_items = list(self.table_listbox.get(0, tk.END))
            if created_table in all_items:
                idx = all_items.index(created_table)
                self.table_listbox.selection_clear(0, tk.END)
                self.table_listbox.selection_set(idx)
                self.table_listbox.activate(idx)
                # call handler to open preview
                self.on_table_select(None)
            else:
                # If DB not yet flushed, try refreshing again shortly
                self.root.after(200, self.refresh_table_list)

            # If Load_data updated last_df, update combo fields
            try:
                from Function import Function_def
                if getattr(Function_def, 'last_df', None) is not None:
                    self.populate_combo_fields(Function_def.last_df)
            except Exception:
                # only catch errors local to Function_def access
                pass

        except (FileNotFoundError, PermissionError, ValueError, RuntimeError) as e:
            # narrower exception handling
            messagebox.showerror("Lỗi", f"Không thể tải dữ liệu: {e}")
        except Exception:
            # re-raise unexpected exceptions to be caught during development
            raise

    def on_execute_sql(self):
        """Execute SQL and populate comboboxes based on result (if any)."""
        execute_sql(self.entry_database, self.sql_text, self.tree_sql,
                   self.combo_x, self.combo_y)
        self.populate_combo_fields()

    def create_sql_tab(self, notebook):
        """Create SQL query tab."""
        tab = tk.Frame(notebook, bg=ColorScheme.BG_MAIN)
        notebook.add(tab, text="   🔍 Truy Vấn SQL   ")

        editor_card = ModernCard(tab, " SQL", "✏️")
        editor_card.pack(fill="x", padx=20, pady=(20, 10))

        editor_content = tk.Frame(editor_card, bg=ColorScheme.BG_CARD)
        editor_content.pack(fill="x", padx=20, pady=(0, 20))

        sql_frame = tk.Frame(editor_content, relief="solid", bd=1, bg="#2B2B2B")
        sql_frame.pack(fill="x")

        self.sql_text = tk.Text(sql_frame,
                                font=("Consolas", 11),
                                height=8,
                                bg="#2B2B2B",
                                fg="#F0F0F0",
                                insertbackground="white",
                                relief="flat")
        self.sql_text.pack(side="left", fill="both", expand=True)

        sql_scroll = tk.Scrollbar(sql_frame, orient="vertical", command=self.sql_text.yview)
        sql_scroll.pack(side="right", fill="y")
        self.sql_text.config(yscrollcommand=sql_scroll.set)

        # Sample query
        self.sql_text.insert("1.0", "SELECT * FROM ;")

        button_frame = tk.Frame(editor_content, bg=ColorScheme.BG_CARD)
        button_frame.pack(fill="x", pady=(10, 0))

        ttk.Button(button_frame,
                   text="▶ Thực thi",
                   style="Primary.TButton",
                   command=self.on_execute_sql).pack(side="left")

        export_frame = tk.Frame(button_frame, bg=ColorScheme.BG_CARD)
        export_frame.pack(side="right")

        tk.Label(export_frame,
                 text="Xuất ra file:",
                 font=("Segoe UI", 10),
                 bg=ColorScheme.BG_CARD,
                 fg=ColorScheme.TEXT_PRIMARY).pack(side="left", padx=(0, 5))

        self.combo_export = ttk.Combobox(export_frame,
                                         values=["CSV", "JSON"],
                                         font=("Segoe UI", 9),
                                         state="readonly",
                                         width=8)
        self.combo_export.pack(side="left", padx=5)
        self.combo_export.set("CSV")

        ttk.Button(export_frame,
                   text="📤 Xuất",
                   style="Success.TButton",
                   command=lambda: export_data(self.combo_export)).pack(side="left", padx=(5, 0))

        results_card = ModernCard(tab, "Kết Quả Truy Vấn", "📋")
        results_card.pack(fill="both", expand=True, padx=20, pady=10)

        tree_frame = tk.Frame(results_card, bg=ColorScheme.BG_CARD)
        tree_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        self.tree_sql = ttk.Treeview(tree_frame)
        self.tree_sql.pack(side="left", fill="both", expand=True)

        tree_scroll_sql = tk.Scrollbar(tree_frame, orient="vertical", command=self.tree_sql.yview)
        tree_scroll_sql.pack(side="right", fill="y")
        self.tree_sql.config(yscrollcommand=tree_scroll_sql.set)

    def create_prediction_tab(self, notebook):
        """Prediction tab (UI scaffold)."""
        tab = tk.Frame(notebook, bg=ColorScheme.BG_MAIN)
        notebook.add(tab, text="   📈 Dự báo   ")

        model_card = ModernCard(tab, "Mô Hình Dự Báo")
        model_card.pack(fill="x", padx=20, pady=(20, 10))

        model_content = tk.Frame(model_card, bg=ColorScheme.BG_CARD)
        model_content.pack(fill="x", padx=20, pady=(0, 20))

        model_row = tk.Frame(model_content, bg=ColorScheme.BG_CARD)
        model_row.pack(fill="x", pady=10)

        tk.Label(model_row,
                 text="Mô hình:",
                 font=("Segoe UI", 11),
                 bg=ColorScheme.BG_CARD,
                 fg=ColorScheme.TEXT_PRIMARY).pack(side="left", padx=(0, 10))

        self.combo_model = ttk.Combobox(model_row,
                                        values=[],
                                        font=("Segoe UI", 10),
                                        state="readonly",
                                        width=25)
        self.combo_model.pack(side="left", padx=5)
        self.combo_model.set("")

        tk.Label(model_row,
                 text="Năm dự báo:",
                 font=("Segoe UI", 11),
                 bg=ColorScheme.BG_CARD,
                 fg=ColorScheme.TEXT_PRIMARY).pack(side="left", padx=(30, 10))

        self.entry_year = tk.Entry(model_row,
                                   font=("Segoe UI", 10),
                                   width=10,
                                   relief="solid",
                                   bd=1,
                                   state="disabled")
        self.entry_year.pack(side="left", padx=5)
        self.entry_year.insert(0, "2025")

        ttk.Button(model_row,
                   text="Dự báo (Chưa khả dụng)",
                   style="Primary.TButton",
                   state="disabled").pack(side="left", padx=(30, 0))

        results_card = ModernCard(tab, "Kết Quả Dự Báo", "📊")
        results_card.pack(fill="both", expand=True, padx=20, pady=10)

        self.prediction_frame = tk.Frame(results_card, bg=ColorScheme.BG_CARD)
        self.prediction_frame.pack(fill="both", expand=True, padx=20, pady=20)

        info_panel = tk.Frame(results_card, bg="#E6F7FF", relief="solid", bd=1)
        info_panel.pack(fill="x", padx=20, pady=(0, 20))

        tk.Label(info_panel,
                 text=" Cho em qua môn ",
                 font=("Segoe UI", 10),
                 bg="#E6F7FF",
                 fg=ColorScheme.PRIMARY,
                 wraplength=800).pack(padx=15, pady=10)


if __name__ == "__main__":
    root = tk.Tk()
    app = Dashboard(root)

    # Center the window on screen
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry('{}x{}+{}+{}'.format(width, height, x, y))

    root.mainloop()
