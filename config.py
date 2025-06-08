#Cấu hình cho ứng dụng

from pathlib import Path
from typing import Dict, Any
import tkinter as tk

# Đường dẫn cơ bản
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"

# Đảm bảo thư mục data tồn tại
DATA_DIR.mkdir(exist_ok=True)

# File paths
TRANSACTIONS_FILE = DATA_DIR / "transactions.csv"
BUDGET_FILE = DATA_DIR / "budget.csv"

# Cấu hình giao diện
WINDOW_CONFIG = {
    "title": "Quản Lý Chi Tiêu Cá Nhân",
    "geometry": "800x600",
    "min_size": (1200, 900),
    "bg_color": "#f0f0f0",
    "theme": "light"  # Luôn sử dụng theme sáng
}

# Cấu hình màu sắc
COLORS = {
    "primary": "#6366f1",     # Indigo sáng
    "success": "#10b981",     # Emerald xanh 
    "warning": "#f59e0b",     # Amber vàng
    "danger": "#ef4444",      # Red đỏ tươi
    "secondary": "#8b5cf6",   # Violet tím
    "dark": "#000000",        # Black
    "light": "#ffffff",       # White
    "background": "#ffffff",  # White
    "text": "#000000",        # Black
    "teal": "#14b8a6",       # Teal xanh ngọc
    "orange": "#f97316"       # Orange cam (thêm luôn vì thấy được sử dụng)
}

def create_static_button_style(color: str) -> Dict[str, Any]:
    """Tạo style cho button với màu cố định"""
    return {
        "bg": color,
        "fg": "black",
        "activebackground": color,
        "activeforeground": "black",
        "relief": tk.RAISED,
        "borderwidth": 2,
        "highlightthickness": 0,
        "cursor": "hand2"
    }

# Danh mục mặc định
DEFAULT_CATEGORIES = {
    "expense": [
        "Ăn uống", "Đi lại", "Học tập", "Giải trí", 
        "Mua sắm", "Y tế", "Hóa đơn", "Khác"
    ],
    "income": [
        "Lương", "Thưởng", "Làm thêm","Học bổng", "Đầu tư", "Khác"
    ]
}

# Cấu hình báo cáo
REPORT_CONFIG = {
    "date_format": "%d/%m/%Y",
    "currency": "VNĐ",
    "decimal_places": 0,
    "budget_warning_threshold": 0.8  # Cảnh báo khi chi tiêu >= 80% ngân sách
}

# Cấu hình CSV
CSV_CONFIG = {
    "encoding": "utf-8",
    "delimiter": ",",
    "date_format": "%d/%m/%Y %H:%M:%S",  # Format cũ (để tương thích)
    "timestamp_format": "%H:%M:%S"      # Format mới cho timestamp
}

# Cấu hình validation
VALIDATION_CONFIG = {
    "max_amount": 1000000000,  # 1 tỷ VNĐ
    "min_amount": 0.01,
    "max_description_length": 200,
    "date_range_years": 10  # Cho phép nhập giao dịch trong vòng 10 năm
} 