#Dialog quản lý ngân sách

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from typing import Callable
from config import COLORS, DEFAULT_CATEGORIES, create_static_button_style
from utils.date_utils import generate_month_range


class BudgetDialog:
    """Dialog quản lý ngân sách"""
    
    def __init__(self, parent, controller, on_close_callback: Callable = None):
        self.parent = parent
        self.controller = controller
        self.on_close_callback = on_close_callback
        
        # Tạo dialog window
        self.dialog = tk.Toplevel(parent)
        self.setup_dialog()
        
        # Load dữ liệu và hiển thị
        self.current_month = datetime.now().strftime("%m/%Y")
        self.create_widgets()
        self.load_budget_data()
    
    def setup_dialog(self):
        """Thiết lập dialog"""
        self.dialog.title("🏦 Quản Lý Ngân Sách")
        self.dialog.geometry("800x600")
        self.dialog.configure(bg=COLORS["background"])
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Căn giữa dialog
        self.center_dialog()
        
        # Xử lý sự kiện đóng
        self.dialog.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def center_dialog(self):
        """Căn giữa dialog"""
        self.dialog.update_idletasks()
        
        # Lấy kích thước
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        parent_x = self.parent.winfo_x()
        parent_y = self.parent.winfo_y()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        # Tính toán vị trí
        x = parent_x + (parent_width - width) // 2
        y = parent_y + (parent_height - height) // 2
        
        self.dialog.geometry(f"{width}x{height}+{x}+{y}")
    
    def create_widgets(self):
        """Tạo các widget"""
        # Title
        self.create_title()
        
        # Chọn tháng
        self.create_month_selector()
        
        # Khung nhập ngân sách
        self.create_budget_input_section()
        
        # Khung trạng thái ngân sách
        self.create_budget_status_section()
        
        # Nút hành động
        self.create_action_buttons()
    
    def create_title(self):
        """Tạo tiêu đề"""
        title_frame = tk.Frame(self.dialog, bg=COLORS["primary"], height=60)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(
            title_frame,
            text="🏦 QUẢN LÝ NGÂN SÁCH",
            font=("Arial", 16, "bold"),
            bg=COLORS["primary"],
            fg=COLORS["light"]
        )
        title_label.pack(pady=20)
    
    def create_month_selector(self):
        """Tạo selector cho tháng"""
        month_frame = tk.Frame(self.dialog, bg=COLORS["light"])
        month_frame.pack(fill=tk.X, padx=20, pady=10)
        
        month_label = tk.Label(
            month_frame,
            text="Chọn tháng:",
            font=("Arial", 12, "bold"),
            bg=COLORS["light"],
            fg=COLORS["dark"]
        )
        month_label.pack(side=tk.LEFT)
        
        # Box chọn tháng
        self.month_var = tk.StringVar(value=self.current_month)
        self.month_combo = ttk.Combobox(
            month_frame,
            textvariable=self.month_var,
            width=10,
            state="readonly"
        )
        
        # Tạo các tháng
        months = generate_month_range()
        
        self.month_combo['values'] = months
        self.month_combo.pack(side=tk.LEFT, padx=10)
        self.month_combo.bind('<<ComboboxSelected>>', self.on_month_change)
    
    def create_budget_input_section(self):
        """Tạo section nhập ngân sách"""
        input_frame = tk.LabelFrame(
            self.dialog,
            text="Đặt Ngân Sách Mới",
            font=("Arial", 12, "bold"),
            bg=COLORS["light"],
            fg=COLORS["dark"]
        )
        input_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Chọn danh mục
        category_frame = tk.Frame(input_frame, bg=COLORS["light"])
        category_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(
            category_frame,
            text="Danh mục:",
            font=("Arial", 10, "bold"),
            bg=COLORS["light"]
        ).pack(side=tk.LEFT)
        
        self.budget_category_var = tk.StringVar()
        self.budget_category_combo = ttk.Combobox(
            category_frame,
            textvariable=self.budget_category_var,
            values=DEFAULT_CATEGORIES["expense"],
            width=15,
            state="readonly"
        )
        self.budget_category_combo.pack(side=tk.LEFT, padx=10)
        
        # Nhập số tiền
        tk.Label(
            category_frame,
            text="Số tiền:",
            font=("Arial", 10, "bold"),
            bg=COLORS["light"]
        ).pack(side=tk.LEFT, padx=(20, 0))
        
        self.budget_amount_entry = tk.Entry(
            category_frame,
            font=("Arial", 10),
            width=15
        )
        self.budget_amount_entry.pack(side=tk.LEFT, padx=10)
        
        # Nút đặt ngân sách
        set_style = create_static_button_style(COLORS["primary"])
        set_btn = tk.Button(
            category_frame,
            text="💰 Đặt Ngân Sách",
            command=self.set_budget,
            font=("Arial", 10, "bold"),
            **set_style
        )
        set_btn.pack(side=tk.LEFT, padx=10)
    
    def create_budget_status_section(self):
        """Tạo section hiển thị trạng thái ngân sách"""
        status_frame = tk.LabelFrame(
            self.dialog,
            text="Trạng Thái Ngân Sách",
            font=("Arial", 12, "bold"),
            bg=COLORS["light"],
            fg=COLORS["dark"]
        )
        status_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Treeview cho trạng thái ngân sách
        columns = ("Danh mục", "Ngân sách", "Đã chi", "Còn lại", "Tỷ lệ", "Trạng thái")
        self.budget_tree = ttk.Treeview(
            status_frame,
            columns=columns,
            show="headings",
            height=12
        )
        
        # Cấu hình cột
        column_widths = {
            "Danh mục": 120,
            "Ngân sách": 100,
            "Đã chi": 100,
            "Còn lại": 100,
            "Tỷ lệ": 80,
            "Trạng thái": 100
        }
        
        for col in columns:
            self.budget_tree.heading(col, text=col)
            self.budget_tree.column(col, width=column_widths.get(col, 100))
        
        # Thanh cuộn
        scrollbar = ttk.Scrollbar(
            status_frame,
            orient=tk.VERTICAL,
            command=self.budget_tree.yview
        )
        self.budget_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack treeview và thanh cuộn
        self.budget_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)
        
        # Context menu cho treeview ngân sách
        self.create_context_menu()
        self.budget_tree.bind("<Button-3>", self.show_context_menu)  # Right click
    
    def create_context_menu(self):
        """Tạo context menu cho budget tree"""
        self.context_menu = tk.Menu(self.dialog, tearoff=0)
        self.context_menu.add_command(label="✏️ Chỉnh sửa", command=self.edit_selected_budget)
        self.context_menu.add_command(label="🗑️ Xóa", command=self.delete_selected_budget)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="📊 Xem chi tiết", command=self.view_budget_details)
    
    def create_action_buttons(self):
        """Tạo các nút hành động"""
        button_frame = tk.Frame(self.dialog, bg=COLORS["light"])
        button_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Copy từ tháng trước
        copy_style = create_static_button_style(COLORS["teal"])
        copy_btn = tk.Button(
            button_frame,
            text="📋 Copy Từ Tháng Trước",
            command=self.copy_from_previous_month,
            font=("Arial", 10, "bold"),
            padx=15,
            pady=8,
            **copy_style
        )
        copy_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Xóa tất cả ngân sách
        clear_style = create_static_button_style(COLORS["orange"])
        clear_btn = tk.Button(
            button_frame,
            text="🗑️ Xóa Tất Cả",
            command=self.clear_all_budgets,
            font=("Arial", 10, "bold"),
            padx=15,
            pady=8,
            **clear_style
        )
        clear_btn.pack(side=tk.LEFT)
        
        # Nút đóng
        close_style = create_static_button_style(COLORS["secondary"])
        close_btn = tk.Button(
            button_frame,
            text="❌ Đóng",
            command=self.on_close,
            font=("Arial", 10, "bold"),
            padx=15,
            pady=8,
            **close_style
        )
        close_btn.pack(side=tk.RIGHT, padx=(10, 0))
    
    def on_month_change(self, event=None):
        """Xử lý khi thay đổi tháng"""
        self.current_month = self.month_var.get()
        self.load_budget_data()
    
    def set_budget(self):
        """Đặt ngân sách"""
        category = self.budget_category_var.get()
        amount_str = self.budget_amount_entry.get().strip()
        
        if not category:
            messagebox.showerror("Lỗi", "Vui lòng chọn danh mục!")
            return
        
        if not amount_str:
            messagebox.showerror("Lỗi", "Vui lòng nhập số tiền!")
            return
        
        try:
            amount = float(amount_str.replace(",", ""))
            if amount <= 0:
                messagebox.showerror("Lỗi", "Số tiền phải lớn hơn 0!")
                return
        except ValueError:
            messagebox.showerror("Lỗi", "Số tiền không hợp lệ!")
            return
        
        # Đặt ngân sách thông qua controller
        success = self.controller.set_budget(category, amount, self.current_month)
        if success:
            # Xóa form và tải lại dữ liệu
            self.budget_category_var.set("")
            self.budget_amount_entry.delete(0, tk.END)
            self.load_budget_data()
    
    def load_budget_data(self):
        """Tải dữ liệu ngân sách"""
        # Xóa dữ liệu hiện có
        for item in self.budget_tree.get_children():
            self.budget_tree.delete(item)
        
        # Lấy trạng thái ngân sách
        budget_statuses = self.controller.get_all_budget_status(self.current_month)
        
        # Thêm vào treeview
        for status in budget_statuses:
            # Định dạng giá trị
            budget_str = f"{status['budget']:,.0f}" if status['budget'] > 0 else "Chưa đặt"
            spent_str = f"{status['spent']:,.0f}"
            remaining_str = f"{status['remaining']:,.0f}" if status['budget'] > 0 else "N/A"
            percentage_str = f"{status['percentage']:.1f}%" if status['budget'] > 0 else "N/A"
            
            # Xác định màu nền dựa trên trạng thái
            tags = []
            if status['status'] == "Vượt quá":
                tags = ['exceeded']
            elif status['status'] == "Cảnh báo":
                tags = ['warning']
            elif status['status'] == "An toàn":
                tags = ['safe']
            
            self.budget_tree.insert("", tk.END, values=(
                status['category'],
                budget_str,
                spent_str,
                remaining_str,
                percentage_str,
                status['status']
            ), tags=tags)
        
        # Cấu hình màu nền cho tag
        self.budget_tree.tag_configure('exceeded', background='#ffebee')
        self.budget_tree.tag_configure('warning', background='#fff8e1')
        self.budget_tree.tag_configure('safe', background='#e8f5e8')
    
    def show_context_menu(self, event):
        """Hiển thị context menu"""
        # Chọn item dưới con trỏ
        item = self.budget_tree.identify('item', event.x, event.y)
        if item:
            self.budget_tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
    
    def edit_selected_budget(self):
        """Chỉnh sửa ngân sách được chọn"""
        selection = self.budget_tree.selection()
        if not selection:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn ngân sách để chỉnh sửa!")
            return
        
        item = self.budget_tree.item(selection[0])
        values = item['values']
        category = values[0]
        
        # Tiền đề cho form
        self.budget_category_var.set(category)
        
        # Lấy số tiền ngân sách hiện tại
        try:
            current_budget = float(values[1].replace(',', '').replace('Chưa đặt', '0'))
            self.budget_amount_entry.delete(0, tk.END)
            self.budget_amount_entry.insert(0, str(int(current_budget)))
        except:
            pass
    
    def delete_selected_budget(self):
        """Xóa ngân sách được chọn"""
        selection = self.budget_tree.selection()
        if not selection:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn ngân sách để xóa!")
            return
        
        item = self.budget_tree.item(selection[0])
        values = item['values']
        category = values[0]
        
        if messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn xóa ngân sách cho '{category}'?"):
            # Xóa thông qua budget manager
            success, message = self.controller.budget_manager.delete_budget(category, self.current_month)
            if success:
                messagebox.showinfo("Thành công", message)
                self.load_budget_data()
            else:
                messagebox.showerror("Lỗi", message)
    
    def view_budget_details(self):
        """Xem chi tiết ngân sách"""
        selection = self.budget_tree.selection()
        if not selection:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn ngân sách để xem chi tiết!")
            return
        
        item = self.budget_tree.item(selection[0])
        values = item['values']
        
        detail_text = f"""CHI TIẾT NGÂN SÁCH - {values[0]}

Tháng: {self.current_month}
Ngân sách: {values[1]} VNĐ
Đã chi tiêu: {values[2]} VNĐ
Còn lại: {values[3]} VNĐ
Tỷ lệ sử dụng: {values[4]}
Trạng thái: {values[5]}"""
        
        messagebox.showinfo("Chi tiết ngân sách", detail_text)
    
    def copy_from_previous_month(self):
        """Copy ngân sách từ tháng trước"""
        selected_month = self.month_var.get()  # Lấy tháng được chọn từ combobox
        if messagebox.askyesno("Xác nhận", f"Bạn có muốn copy ngân sách từ tháng trước sang tháng {selected_month} không?"):
            success, message = self.controller.budget_manager.copy_budget_to_next_month(selected_month)
            if success:
                messagebox.showinfo("Thành công", message)
                self.load_budget_data()
            else:
                messagebox.showerror("Lỗi", message)
    
    def clear_all_budgets(self):
        """Xóa tất cả ngân sách của tháng hiện tại"""
        if messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn xóa tất cả ngân sách tháng {self.current_month}?"):
            # Xóa tất cả ngân sách cho tháng hiện tại
            categories = DEFAULT_CATEGORIES["expense"]
            success_count = 0
            
            for category in categories:
                success, _ = self.controller.budget_manager.delete_budget(category, self.current_month)
                if success:
                    success_count += 1
            
            if success_count > 0:
                messagebox.showinfo("Thành công", f"Đã xóa {success_count} ngân sách!")
                self.load_budget_data()
            else:
                messagebox.showinfo("Thông báo", "Không có ngân sách nào để xóa!")
    
    def export_budget_report(self):
        """Xuất báo cáo ngân sách"""
        # Lấy dữ liệu báo cáo từ controller
        transactions = self.controller.get_all_transactions()
        report = self.controller.budget_manager.export_budget_report(transactions, self.current_month)
        
        # Tạo cửa sổ báo cáo mới
        report_window = tk.Toplevel(self.dialog)
        report_window.title(f"📊 Báo cáo ngân sách - {self.current_month}")
        report_window.geometry("800x600")
        report_window.configure(bg=COLORS["background"])
        
        # Tạo frame chứa nội dung
        content_frame = tk.Frame(report_window, bg=COLORS["background"])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Tạo canvas và scrollbar
        canvas = tk.Canvas(content_frame, bg=COLORS["background"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(content_frame, orient="vertical", command=canvas.yview)
        
        # Tạo frame chứa text
        text_frame = tk.Frame(canvas, bg=COLORS["background"])
        
        # Cấu hình canvas
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack scrollbar và canvas
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Tạo cửa sổ trong canvas
        canvas_frame = canvas.create_window((0, 0), window=text_frame, anchor="nw", width=canvas.winfo_width())
        
        # Tạo text widget với định dạng
        text_widget = tk.Text(
            text_frame,
            wrap=tk.WORD,
            font=("Courier New", 11),
            bg=COLORS["background"],
            fg=COLORS["text"],
            padx=10,
            pady=10,
            relief=tk.FLAT,
            highlightthickness=0
        )
        text_widget.pack(fill=tk.BOTH, expand=True)
        
        # Thêm nội dung báo cáo
        text_widget.insert(tk.END, report)
        text_widget.config(state=tk.DISABLED)
        
        # Cấu hình scroll
        def configure_scroll(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            # Cập nhật chiều rộng của text frame khi cửa sổ thay đổi kích thước
            canvas.itemconfig(canvas_frame, width=event.width)
        
        text_frame.bind("<Configure>", configure_scroll)
        canvas.bind("<Configure>", configure_scroll)
        
        # Thêm nút đóng
        close_btn = tk.Button(
            report_window,
            text="❌ Đóng",
            command=report_window.destroy,
            font=("Arial", 10, "bold"),
            padx=15,
            pady=8,
            **create_static_button_style(COLORS["secondary"])
        )
        close_btn.pack(pady=(0, 10))
        
        # Cập nhật scrollregion khi nội dung thay đổi
        def update_scrollregion(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        text_widget.bind("<Configure>", update_scrollregion)
    
    def on_close(self):
        """Xử lý khi đóng dialog"""
        if self.on_close_callback:
            self.on_close_callback()
        self.dialog.destroy() 