#Form thêm/sửa giao dịch

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from typing import Dict, Any, Callable, Optional
from config import COLORS, DEFAULT_CATEGORIES, create_static_button_style, CSV_CONFIG


class TransactionForm(tk.LabelFrame):
    """Form để nhập thông tin giao dịch"""
    
    def __init__(self, parent, on_submit_callback: Callable = None):
        super().__init__(
            parent,
            text="Thêm Giao Dịch Mới",
            font=("Arial", 12, "bold"),
            bg=COLORS["background"],
            fg=COLORS["text"]
        )
        
        self.on_submit_callback = on_submit_callback
        self.create_widgets()
    
    def create_widgets(self):
        """Tạo các widget trong form"""
        # Loại giao dịch
        self.create_transaction_type_section()
        
        # Số tiền
        self.create_amount_section()
        
        # Danh mục
        self.create_category_section()
        
        # Ngày
        self.create_date_section()
        
        # Mô tả
        self.create_description_section()
        
        # Nút submit
        self.create_submit_button()
    
    def create_transaction_type_section(self):
        """Tạo section chọn loại giao dịch"""
        type_label = tk.Label(
            self,
            text="Loại giao dịch:",
            font=("Arial", 10, "bold"),
            bg=COLORS["background"],
            fg=COLORS["text"]
        )
        type_label.pack(anchor=tk.W, padx=10, pady=(10, 5))
        
        self.transaction_type = tk.StringVar(value="Chi tiêu")
        type_frame = tk.Frame(self, bg=COLORS["background"])
        type_frame.pack(anchor=tk.W, padx=20, pady=5)
        
        income_radio = tk.Radiobutton(
            type_frame,
            text="💰 Thu nhập",
            variable=self.transaction_type,
            value="Thu nhập",
            bg=COLORS["background"],
            fg=COLORS["success"],
            font=("Arial", 10, "bold"),
            command=self.on_type_change
        )
        income_radio.pack(side=tk.LEFT, padx=(0, 20))
        
        expense_radio = tk.Radiobutton(
            type_frame,
            text="💸 Chi tiêu",
            variable=self.transaction_type,
            value="Chi tiêu",
            bg=COLORS["background"],
            fg=COLORS["danger"],
            font=("Arial", 10, "bold"),
            command=self.on_type_change
        )
        expense_radio.pack(side=tk.LEFT)
    
    def create_amount_section(self):
        """Tạo section nhập số tiền"""
        amount_label = tk.Label(
            self,
            text="Số tiền (VNĐ):",
            font=("Arial", 10, "bold"),
            bg=COLORS["background"],
            fg=COLORS["text"]
        )
        amount_label.pack(anchor=tk.W, padx=10, pady=(10, 5))
        
        self.amount_entry = tk.Entry(
            self,
            font=("Arial", 12, "bold"),
            width=12,
            relief="solid",
            bd=1,
            highlightthickness=1,
            highlightbackground="#E0E0E0",
            highlightcolor=COLORS["primary"],
            insertbackground=COLORS["dark"]  # Màu của con trỏ
        )
        self.amount_entry.pack(anchor=tk.W, padx=20, pady=5)
        
        # Format hint
        hint_label = tk.Label(
            self,
            text="💡 Ví dụ: 50000 hoặc 1500000",
            font=("Arial", 8, "bold"),
            bg=COLORS["background"],
            fg=COLORS["secondary"]
        )
        hint_label.pack(anchor=tk.W, padx=20)
    
    def create_category_section(self):
        """Tạo section chọn danh mục"""
        category_label = tk.Label(
            self,
            text="Danh mục:",
            font=("Arial", 10, "bold"),
            bg=COLORS["background"],
            fg=COLORS["text"]
        )
        category_label.pack(anchor=tk.W, padx=10, pady=(10, 5))
        
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(
            self,
            textvariable=self.category_var,
            font=("Arial", 10, "bold"),
            width=12,
            state="readonly"
        )
        self.category_combo.pack(anchor=tk.W, padx=20, pady=5)
        
        # Cập nhật danh mục dựa trên loại giao dịch ban đầu
        self.update_categories()
    
    def create_date_section(self):
        """Tạo section nhập ngày"""
        date_label = tk.Label(
            self,
            text="Ngày giao dịch:",
            font=("Arial", 10, "bold"),
            bg=COLORS["background"],
            fg=COLORS["text"]
        )
        date_label.pack(anchor=tk.W, padx=10, pady=(10, 5))
        
        date_frame = tk.Frame(self, bg=COLORS["background"])
        date_frame.pack(anchor=tk.W, padx=20, pady=5)
        
        self.date_entry = tk.Entry(
            date_frame,
            font=("Arial", 12, "bold"),
            width=12,
            relief="solid",
            bd=1,
            highlightthickness=1,
            highlightbackground="#E0E0E0",
            highlightcolor=COLORS["primary"],
            insertbackground=COLORS["dark"]
        )
        self.date_entry.pack(side=tk.LEFT)
        
        # Nút để đặt ngày hôm nay
        today_btn = tk.Button(
            date_frame,
            text="📅 Hôm nay",
            command=self.set_today_date,
            font=("Arial", 10, "bold"),
            padx=6,
            pady=4,
            bg=COLORS["primary"],
            fg=COLORS["dark"],
            relief="solid",
            bd=1,
            cursor="hand2"
        )
        today_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        # Định dạng ngày
        date_hint = tk.Label(
            self,
            text="📅 Định dạng: DD/MM/YYYY (ví dụ: 15/12/2024)",
            font=("Arial", 8, "bold"),
            bg=COLORS["background"],
            fg=COLORS["secondary"]
        )
        date_hint.pack(anchor=tk.W, padx=20)
        
        # Đặt ngày hôm nay làm mặc định
        self.set_today_date()
    
    def create_description_section(self):
        """Tạo section nhập mô tả"""
        desc_label = tk.Label(
            self,
            text="Mô tả (tùy chọn):",
            font=("Arial", 10, "bold"),
            bg=COLORS["background"],
            fg=COLORS["text"]
        )
        desc_label.pack(anchor=tk.W, padx=10, pady=(10, 5))
        
        self.desc_entry = tk.Entry(
            self,
            font=("Arial", 10, "bold"),
            width=25,  # Giảm để cân đối với các ô khác
            relief="solid",
            bd=1,
            highlightthickness=1,
            highlightbackground="#E0E0E0",
            highlightcolor=COLORS["primary"],
            insertbackground=COLORS["dark"]  # Màu của con trỏ
        )
        self.desc_entry.pack(anchor=tk.W, padx=20, pady=5)

        # Thêm placeholder text khi focus
        def on_focus_in(event):
            if self.desc_entry.get() == "Nhập mô tả cho giao dịch...":
                self.desc_entry.delete(0, tk.END)
                self.desc_entry.config(fg=COLORS["dark"])

        def on_focus_out(event):
            if not self.desc_entry.get():
                self.desc_entry.insert(0, "Nhập mô tả cho giao dịch...")
                self.desc_entry.config(fg=COLORS["secondary"])

        # Đặt placeholder ban đầu
        self.desc_entry.insert(0, "Nhập mô tả cho giao dịch...")
        self.desc_entry.config(fg=COLORS["secondary"])

        # Bind sự kiện focus
        self.desc_entry.bind("<FocusIn>", on_focus_in)
        self.desc_entry.bind("<FocusOut>", on_focus_out)
    
    def create_submit_button(self):
        """Tạo nút submit form"""
        button_frame = tk.Frame(self, bg=COLORS["background"])
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Nút thêm giao dịch
        self.submit_btn = tk.Button(
            button_frame,
            text="➕ Thêm Giao Dịch",
            command=self.on_submit,
            font=("Arial", 12, "bold"),
            padx=20,
            pady=10,
            bg=COLORS["primary"],
            fg=COLORS["dark"],
            relief="solid",
            bd=1,
            cursor="hand2"
        )
        self.submit_btn.pack(fill=tk.X)
        
        # Nút làm mới form
        reset_btn = tk.Button(
            button_frame,
            text="🔄 Làm Mới Form",
            command=self.clear_form,
            font=("Arial", 10, "bold"),
            padx=15,
            pady=8,
            bg=COLORS["light"],
            fg=COLORS["dark"],
            relief="solid",
            bd=1,
            cursor="hand2"
        )
        reset_btn.pack(fill=tk.X, pady=(8, 0))

        # Thêm hiệu ứng hover cho các nút
        def on_enter(e):
            e.widget.config(bg=COLORS["primary"], fg=COLORS["dark"])
            
        def on_leave(e):
            if e.widget != self.submit_btn:  # Chỉ đổi màu nút reset khi rời chuột
                e.widget.config(bg=COLORS["light"], fg=COLORS["dark"])
        
        reset_btn.bind("<Enter>", on_enter)
        reset_btn.bind("<Leave>", on_leave)
    
    def on_type_change(self):
        """Xử lý khi thay đổi loại giao dịch"""
        self.update_categories()
        self.update_submit_button_style()
    
    def update_categories(self):
        """Cập nhật danh sách danh mục theo loại giao dịch"""
        if self.transaction_type.get() == "Thu nhập":
            categories = DEFAULT_CATEGORIES["income"]
        else:
            categories = DEFAULT_CATEGORIES["expense"]
        
        self.category_combo['values'] = categories
        self.category_combo.set("")  # Clear selection
    
    def update_submit_button_style(self):
        """Cập nhật style của nút submit theo loại giao dịch"""
        if self.transaction_type.get() == "Thu nhập":
            success_style = create_static_button_style(COLORS["success"])
            self.submit_btn.config(
                text="➕ Thêm Thu Nhập",
                **success_style
            )
        else:
            primary_style = create_static_button_style(COLORS["primary"])
            self.submit_btn.config(
                text="➕ Thêm Chi Tiêu",
                **primary_style
            )
    
    def set_today_date(self):
        """Đặt ngày hôm nay"""
        today = datetime.now().strftime("%d/%m/%Y")
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, today)
    
    def on_submit(self):
        """Xử lý khi submit form"""
        try:
            # Kiểm tra và lấy dữ liệu từ form
            transaction_data = self.get_form_data()
            if not transaction_data:
                return
            
            # Gọi callback nếu có
            if self.on_submit_callback:
                success = self.on_submit_callback(transaction_data)
                if success:
                    # Xóa form sau khi thêm giao dịch thành công
                    self.clear_form()
                return success
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể thêm giao dịch: {e}")
            return False
    
    def get_form_data(self) -> Optional[Dict[str, Any]]:
        """Lấy dữ liệu từ form"""
        try:
            # Lấy và validate ngày
            date = self.date_entry.get().strip()
            if not date:
                messagebox.showerror("Lỗi", "Vui lòng nhập ngày giao dịch!")
                return None
                
            # Kiểm tra định dạng ngày
            try:
                datetime.strptime(date, "%d/%m/%Y")
            except ValueError:
                messagebox.showerror("Lỗi", "Định dạng ngày không đúng! Sử dụng DD/MM/YYYY")
                return None
            
            # Lấy loại giao dịch
            transaction_type = self.transaction_type.get()
            if not transaction_type:
                messagebox.showerror("Lỗi", "Vui lòng chọn loại giao dịch!")
                return None
            
            # Lấy danh mục
            category = self.category_var.get()
            if not category:
                messagebox.showerror("Lỗi", "Vui lòng chọn danh mục!")
                return None
            
            # Lấy và validate số tiền
            amount_str = self.amount_entry.get().strip()
            if not amount_str:
                messagebox.showerror("Lỗi", "Vui lòng nhập số tiền!")
                return None
            
            try:
                amount = float(amount_str)
                if amount <= 0:
                    messagebox.showerror("Lỗi", "Số tiền phải lớn hơn 0!")
                    return None
            except ValueError:
                messagebox.showerror("Lỗi", "Số tiền không hợp lệ!")
                return None
            
            # Lấy mô tả (bỏ qua placeholder text)
            description = self.desc_entry.get().strip()
            if description == "Nhập mô tả cho giao dịch...":
                description = ""
            
            # Thêm timestamp (chỉ thời gian)
            timestamp = datetime.now().strftime(CSV_CONFIG["timestamp_format"])
            
            return {
                "timestamp": timestamp,
                "date": date,
                "type": transaction_type,
                "category": category,
                "amount": amount,
                "description": description
            }
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi lấy dữ liệu: {e}")
            return None
    
    def clear_form(self):
        """Xóa dữ liệu trong form"""
        self.transaction_type.set("Chi tiêu")
        self.amount_entry.delete(0, tk.END)
        self.update_categories()
        self.set_today_date()
        self.desc_entry.delete(0, tk.END)
        self.desc_entry.insert(0, "Nhập mô tả cho giao dịch...")
        self.desc_entry.config(fg=COLORS["secondary"])
        self.amount_entry.focus()
    
    def set_focus(self):
        """Đặt focus vào field đầu tiên"""
        self.amount_entry.focus() 