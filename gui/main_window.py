#Cửa sổ chính của ứng dụng

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from typing import Dict, Any

from gui.transaction_form import TransactionForm
from gui.budget_dialog import BudgetDialog
from config import COLORS
from utils.date_utils import generate_month_range

class MainWindow:
    """Cửa sổ chính của ứng dụng"""
    
    def __init__(self, parent: tk.Tk, controller):
        self.parent = parent
        self.controller = controller
        
        # Cấu hình cửa sổ
        self.setup_window()
        
        # Tạo giao diện
        self.setup_gui()
        
        # Load dữ liệu ban đầu
        self.refresh_all_data()
    
    def setup_window(self):
        """Cấu hình cửa sổ chính"""

        # Đặt theme sáng
        self.parent.configure(bg=COLORS["background"])
    
    def setup_gui(self):
        """Thiết lập giao diện người dùng"""
        # Khung tiêu đề
        self.create_title_frame()
        
        # Khung chính
        main_container = tk.Frame(self.parent, bg=COLORS["light"])
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Khung bên trái
        left_panel = tk.Frame(main_container, bg=COLORS["light"])
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # Form giao dịch
        self.transaction_form = TransactionForm(
            parent=left_panel,
            on_submit_callback=self.on_transaction_submit
        )
        self.transaction_form.pack(fill=tk.X, pady=(0, 10))
        
        # Nút điều khiển
        self.create_control_buttons(left_panel)
        
        # Khung bên phải
        right_panel = tk.Frame(main_container, bg=COLORS["light"])
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Nút ở phía trên
        self.create_top_buttons(right_panel)
        
        # Danh sách giao dịch
        self.create_transaction_list(right_panel)
        
        # Khung tóm tắt
        self.create_summary_panel(right_panel)
    
    def create_title_frame(self):
        """Tạo frame tiêu đề"""
        title_frame = tk.Frame(self.parent, bg=COLORS["primary"], height=60)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(
            title_frame,
            text="QUẢN LÝ CHI TIÊU CÁ NHÂN",
            font=("Arial", 18, "bold"),
            bg=COLORS["primary"],
            fg=COLORS["dark"]
        )
        title_label.pack(pady=15)
    
    def create_control_buttons(self, parent):
        """Tạo các nút điều khiển"""
        control_frame = tk.LabelFrame(
            parent,
            text="Quản Lý",
            font=("Arial", 12, "bold"),
            bg=COLORS["light"],
            fg=COLORS["dark"]
        )
        control_frame.pack(fill=tk.X, pady=10)
        
        # Nút quản lý ngân sách
        budget_btn = tk.Button(
            control_frame,
            text="🏦 Quản Lý Ngân Sách",
            command=self.open_budget_dialog,
            font=("Arial", 10, "bold"),
            pady=10,
            bg=COLORS["primary"],
            fg=COLORS["dark"],
            activebackground=COLORS["primary"],
            activeforeground=COLORS["dark"]
        )
        budget_btn.pack(fill=tk.X, pady=5, padx=10)
        
        # Nút xem báo cáo
        reports_btn = tk.Button(
            control_frame,
            text="📊 Xem Báo Cáo",
            command=self.show_reports,
            font=("Arial", 10, "bold"),
            pady=10,
            bg=COLORS["primary"],
            fg=COLORS["dark"],
            activebackground=COLORS["primary"],
            activeforeground=COLORS["dark"]
        )
        reports_btn.pack(fill=tk.X, pady=5, padx=10)
    
    def create_top_buttons(self, parent):
        """Tạo các nút ở phía trên"""
        button_frame = tk.Frame(parent, bg=COLORS["light"])
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Nút xóa giao dịch
        delete_btn = tk.Button(
            button_frame,
            text="🗑️ Xóa Giao Dịch",
            command=self.delete_selected_transaction,
            font=("Arial", 10, "bold"),
            padx=15,
            pady=8,
            bg=COLORS["primary"],
            fg=COLORS["dark"],
            activebackground=COLORS["primary"],
            activeforeground=COLORS["dark"]
        )
        delete_btn.pack(side=tk.LEFT, padx=5)
    
    def create_transaction_list(self, parent):
        """Tạo danh sách giao dịch"""
        list_frame = tk.LabelFrame(
            parent,
            text="Danh Sách Giao Dịch",
            font=("Arial", 12, "bold"),
            bg=COLORS["light"],
            fg=COLORS["dark"]
        )
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Khung lọc
        filter_frame = tk.Frame(list_frame, bg=COLORS["light"])
        filter_frame.pack(fill=tk.X, padx=10, pady=(10, 15))
        
        # Chọn tháng
        month_label = tk.Label(
            filter_frame,
            text="Tháng:",
            font=("Arial", 10, "bold"),
            bg=COLORS["light"],
            fg=COLORS["dark"]
        )
        month_label.pack(side=tk.LEFT, padx=(0, 5))
        
        # Tạo các tháng
        months = ["Tất cả"] + generate_month_range()
        
        self.month_var = tk.StringVar(value=datetime.now().strftime("%m/%Y"))
        self.month_combo = ttk.Combobox(
            filter_frame,
            values=months,
            textvariable=self.month_var,
            width=10,
            state="readonly",
            font=("Arial", 10, "bold")
        )
        self.month_combo.pack(side=tk.LEFT)
        self.month_combo.bind('<<ComboboxSelected>>', lambda e: self.update_transaction_list())
        
        # Cấu hình kiểu cho Treeview
        style = ttk.Style()
        style.configure(
            "Transactions.Treeview",
            background=COLORS["light"],
            foreground=COLORS["dark"],
            fieldbackground=COLORS["light"],
            font=("Arial", 10, "bold"),
            rowheight=30  # Tăng chiều cao hàng để tăng khoảng cách
        )
        style.configure(
            "Transactions.Treeview.Heading",
            font=("Arial", 10, "bold")  # Đặt font cho tiêu đề cột
        )
        style.map(
            "Transactions.Treeview",
            background=[("selected", COLORS["primary"])],
            foreground=[("selected", COLORS["light"])]
        )
        
        # Khung chứa cho treeview và thanh cuộn
        tree_container = tk.Frame(list_frame, bg=COLORS["light"])
        tree_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Treeview với kiểu tùy chỉnh
        columns = ("Ngày", "Loại", "Danh mục", "Số tiền", "Mô tả")
        self.transaction_tree = ttk.Treeview(
            tree_container,
            columns=columns,
            show="headings",
            height=15,
            style="Transactions.Treeview"
        )
        
        # Cấu hình cột
        column_widths = {"Ngày": 100, "Loại": 80, "Danh mục": 120, "Số tiền": 120, "Mô tả": 200}
        for col in columns:
            self.transaction_tree.heading(col, text=col, command=lambda c=col: self.sort_treeview(c))
            self.transaction_tree.column(col, width=column_widths.get(col, 100))
        
        # Biến để theo dõi trạng thái sắp xếp
        self.sort_state = {
            "column": "Ngày",  # Cột đang sắp xếp
            "reverse": True    # True = giảm dần (mới nhất lên đầu)
        }
        
        # Biến để theo dõi trạng thái sắp xếp
        self.transaction_tree.tag_configure('oddrow', background=COLORS["light"])
        self.transaction_tree.tag_configure('evenrow', background='#F5F5F5')
        
        # Thanh cuộn
        v_scrollbar = ttk.Scrollbar(tree_container, orient=tk.VERTICAL, command=self.transaction_tree.yview)
        h_scrollbar = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=self.transaction_tree.xview)
        self.transaction_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack treeview và thanh cuộn
        self.transaction_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Pack thanh cuộn ngang
        h_scrollbar.pack(fill=tk.X, padx=10, pady=(0, 10))
    
    def create_summary_panel(self, parent):
        """Tạo panel tóm tắt"""
        summary_frame = tk.LabelFrame(
            parent,
            text="Tóm Tắt Tài Chính",
            font=("Arial", 12, "bold"),
            bg=COLORS["light"],
            fg=COLORS["dark"]
        )
        summary_frame.pack(fill=tk.X, pady=(0, 10))

        # Tạo Text widget với scrollbar
        self.summary_text = tk.Text(
            summary_frame,
            font=("Arial", 10, "bold"),
            bg=COLORS["light"],
            fg=COLORS["dark"],
            height=10,
            wrap=tk.WORD,
            padx=10,
            pady=10,
            borderwidth=0,
            highlightthickness=0
        )
        scrollbar = ttk.Scrollbar(
            summary_frame,
            orient=tk.VERTICAL,
            command=self.summary_text.yview
        )
        
        # Cấu hình scrolling
        self.summary_text.configure(yscrollcommand=scrollbar.set)
        
        # Pack widgets
        self.summary_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)
        
        # Vô hiệu hóa chỉnh sửa
        self.summary_text.configure(state='disabled')
    
    def on_transaction_submit(self, transaction_data: Dict[str, Any]) -> bool:
        """Xử lý khi submit form giao dịch"""
        success, message = self.controller.add_transaction(transaction_data)
        if success:
            self.transaction_form.clear_form()
        return success
    
    def open_budget_dialog(self):
        """Mở dialog quản lý ngân sách"""
        BudgetDialog(
            parent=self.parent,
            controller=self.controller,
            on_close_callback=self.refresh_all_data
        )
    
    def show_reports(self):
        """Hiển thị cửa sổ báo cáo"""
        from gui.reports_window import ReportsWindow
        ReportsWindow(
            parent=self.parent,
            controller=self.controller
        )
    
    def delete_selected_transaction(self):
        """Xóa giao dịch được chọn"""
        selection = self.transaction_tree.selection()
        if not selection:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn giao dịch để xóa!")
            return
        
        # Lấy dữ liệu giao dịch được chọn
        item = self.transaction_tree.item(selection[0])
        values = item['values']
        
        # Chuyển đổi về format để xóa
        try:
            amount_str = values[3].replace(',', '').replace(' VNĐ', '').strip()
            amount = round(float(amount_str), 2)  # Làm tròn đến 2 chữ số thập phân
            
            transaction_data = {
                'date': values[0],
                'type': values[1],
                'category': values[2],
                'amount': amount,
                'description': values[4] if len(values) > 4 else ""
            }
            
            # Gọi controller để xóa
            if self.controller.delete_transaction(transaction_data):
                # Cập nhật lại giao diện
                self.refresh_all_data()
            else:
                messagebox.showerror("Lỗi", "Không thể xóa giao dịch. Vui lòng thử lại!")
                
        except (ValueError, IndexError) as e:
            messagebox.showerror("Lỗi", f"Dữ liệu giao dịch không hợp lệ: {e}")
    
    def refresh_all_data(self):
        """Làm mới tất cả dữ liệu"""
        self.update_transaction_list()
        self.update_summary()
    
    def update_transaction_list(self):
        """Cập nhật danh sách giao dịch"""
        # Xóa dữ liệu cũ
        for item in self.transaction_tree.get_children():
            self.transaction_tree.delete(item)
        
        # Lấy dữ liệu mới
        transactions = self.controller.get_all_transactions()
        
        # Lọc theo tháng nếu không chọn "Tất cả"
        selected_month = self.month_var.get()
        if selected_month != "Tất cả":
            transactions = [t for t in transactions if t.get_month_year() == selected_month]
        
        # Sắp xếp theo trạng thái hiện tại
        if self.sort_state["column"] == "Ngày":
            sorted_transactions = sorted(
                transactions,
                key=lambda x: datetime.strptime(x.date, "%d/%m/%Y"),
                reverse=self.sort_state["reverse"]
            )
        else:
            sorted_transactions = transactions
        
        # Thêm vào tree với alternating row colors
        for i, transaction in enumerate(sorted_transactions):
            amount_str = f"{transaction.amount:,.0f} VNĐ"
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            self.transaction_tree.insert(
                "",
                tk.END,
                values=(
                    transaction.date,
                    transaction.type,
                    transaction.category,
                    amount_str,
                    transaction.description
                ),
                tags=(tag,)
            )
    
    def update_summary(self):
        """Cập nhật tóm tắt tài chính"""
        summary_data = self.controller.get_summary_data()
        
        if summary_data:
            summary_text = f"""TỔNG QUAN TÀI CHÍNH

Tổng cộng:
• Thu nhập: {summary_data.get('total_income', 0):,.0f} VNĐ
• Chi tiêu: {summary_data.get('total_expense', 0):,.0f} VNĐ
• Số dư: {summary_data.get('total_balance', 0):,.0f} VNĐ

Tháng {summary_data.get('current_month', '')}:
• Thu nhập: {summary_data.get('monthly_income', 0):,.0f} VNĐ
• Chi tiêu: {summary_data.get('monthly_expense', 0):,.0f} VNĐ
• Số dư: {summary_data.get('monthly_balance', 0):,.0f} VNĐ

Thống kê:
• Tổng giao dịch: {summary_data.get('transaction_count', 0)}"""
            
            # Cập nhật nội dung
            self.summary_text.configure(state='normal')
            self.summary_text.delete(1.0, tk.END)
            self.summary_text.insert(tk.END, summary_text)
            self.summary_text.configure(state='disabled')
        else:
            self.summary_text.configure(state='normal')
            self.summary_text.delete(1.0, tk.END)
            self.summary_text.insert(tk.END, "Không có dữ liệu")
            self.summary_text.configure(state='disabled')
    
    def sort_treeview(self, column):
        """Sắp xếp dữ liệu trong treeview theo cột được chọn"""
        # Lấy tất cả items từ treeview
        items = [(self.transaction_tree.set(item, column), item) for item in self.transaction_tree.get_children('')]
        
        # Đảo ngược trạng thái sắp xếp nếu click vào cùng một cột
        if self.sort_state["column"] == column:
            self.sort_state["reverse"] = not self.sort_state["reverse"]
        else:
            self.sort_state["column"] = column
            self.sort_state["reverse"] = False
        
        # Hàm chuyển đổi giá trị để so sánh
        def convert_value(value):
            if column == "Ngày":
                try:
                    return datetime.strptime(value, "%d/%m/%Y")
                except:
                    return datetime.min
            elif column == "Số tiền":
                try:
                    return float(value.replace(',', '').replace(' VNĐ', ''))
                except:
                    return 0.0
            return value
        
        # Sắp xếp items
        items.sort(key=lambda x: convert_value(x[0]), reverse=self.sort_state["reverse"])
        
        # Di chuyển items đến vị trí mới
        for index, (_, item) in enumerate(items):
            self.transaction_tree.move(item, '', index)
            # Cập nhật màu nền xen kẽ
            self.transaction_tree.item(item, tags=('evenrow' if index % 2 == 0 else 'oddrow',)) 