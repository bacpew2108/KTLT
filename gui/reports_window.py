#Cửa sổ báo cáo

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from typing import Dict, Any
from config import COLORS, create_static_button_style
from utils.date_utils import generate_month_range


class ReportsWindow:
    """Cửa sổ hiển thị báo cáo"""
    
    def __init__(self, parent, controller):
        self.parent = parent
        self.controller = controller
        
        # Tạo cửa sổ báo cáo
        self.window = tk.Toplevel(parent)
        self.setup_window()
        self.create_widgets()
        self.load_reports()
    
    def setup_window(self):
        """Thiết lập cửa sổ"""
        self.window.title("📊 Báo Cáo Tài Chính")
        
        # Lấy kích thước màn hình
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        
        # Tính toán kích thước cửa sổ (40% chiều rộng, 80% chiều cao màn hình)
        window_width = int(screen_width * 0.38)
        window_height = int(screen_height * 0.85)
        
        # Đảm bảo kích thước tối thiểu
        window_width = max(window_width, 450)
        window_height = max(window_height, 900)
        
        # Tính toán vị trí để căn giữa
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        # Đặt kích thước và vị trí cửa sổ
        self.window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        self.window.configure(bg=COLORS["light"])
        self.window.transient(self.parent)
        self.window.grab_set()
        
        # Handle close event
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def create_widgets(self):
        """Tạo các widget"""
        # Title Frame
        title_frame = tk.Frame(self.window, bg=COLORS["primary"], height=60)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(
            title_frame,
            text="📊 BÁO CÁO TÀI CHÍNH CHI TIẾT",
            font=("Arial", 16, "bold"),
            bg=COLORS["primary"],
            fg="white"
        )
        title_label.pack(pady=20)
        
        # Khung điều khiển
        control_frame = tk.Frame(self.window, bg=COLORS["light"])
        control_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Chọn loại báo cáo
        report_types = ["Tổng hợp", "Tháng", "Năm", "Danh mục", "Xu hướng", "Sức khỏe tài chính"]
        self.report_type_var = tk.StringVar(value="Tổng hợp")
        
        report_type_label = tk.Label(
            control_frame,
            text="Loại báo cáo:",
            font=("Arial", 10, "bold"),
            bg=COLORS["light"]
        )
        report_type_label.pack(side=tk.LEFT, padx=(0, 10))
        
        report_type_menu = ttk.Combobox(
            control_frame,
            textvariable=self.report_type_var,
            values=report_types,
            state="readonly",
            width=20
        )
        report_type_menu.pack(side=tk.LEFT, padx=5)
        report_type_menu.bind("<<ComboboxSelected>>", self.on_report_type_change)
        
        # Chọn kỳ báo cáo
        self.period_frame = tk.Frame(control_frame, bg=COLORS["light"])
        self.period_frame.pack(side=tk.LEFT, padx=20)
        
        self.period_label = tk.Label(
            self.period_frame,
            text="Kỳ báo cáo:",
            font=("Arial", 10, "bold"),
            bg=COLORS["light"]
        )
        self.period_label.pack(side=tk.LEFT, padx=(0, 10))
        
        # Tạo box cho tháng và năm (chọn tháng và năm)
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        months = generate_month_range()
        years = [str(y) for y in range(2025, 2028)]
        
        self.period_var = tk.StringVar(value=f"{current_month:02d}/{current_year}")
        self.period_menu = ttk.Combobox(
            self.period_frame,
            textvariable=self.period_var,
            values=months,
            state="readonly",
            width=15
        )
        self.period_menu.pack(side=tk.LEFT, padx=5)
        self.period_menu.bind("<<ComboboxSelected>>", self.load_reports)
        
        # Khung nội dung chính
        main_frame = tk.Frame(self.window, bg=COLORS["light"])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Nội dung báo cáo
        self.report_text = tk.Text(
            main_frame,
            font=("Courier New", 11),
            bg="white",
            fg=COLORS["dark"],
            wrap=tk.WORD,
            padx=15,
            pady=15
        )
        self.report_text.pack(fill=tk.BOTH, expand=True)
        
        # Thanh cuộn cho văn bản
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.report_text.yview)
        self.report_text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Khung nút ở dưới
        button_frame = tk.Frame(self.window, bg=COLORS["light"])
        button_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        # Nút đóng
        close_btn = tk.Button(
            button_frame,
            text="❌ Đóng",
            command=self.on_close,
            font=("Arial", 10, "bold"),
            padx=15,
            pady=5,
            **create_static_button_style(COLORS["secondary"])
        )
        close_btn.pack(side=tk.RIGHT)
    
    def on_report_type_change(self, event=None):
        """Xử lý khi thay đổi loại báo cáo"""
        report_type = self.report_type_var.get()
        
        # Cập nhật giao diện chọn kỳ báo cáo
        if report_type == "Tháng":
            months = generate_month_range()
            self.period_menu.configure(values=months)
            self.period_var.set(months[0])  # Đặt tháng đầu tiên trong khoảng (01/2025)
            self.period_frame.pack(side=tk.LEFT, padx=20)
            
        elif report_type == "Năm":
            years = [str(y) for y in range(2025, 2028)]
            self.period_menu.configure(values=years)
            self.period_var.set("2025")  # Đặt năm đầu tiên trong khoảng (2025)
            self.period_frame.pack(side=tk.LEFT, padx=20)
            
        else:
            self.period_frame.pack_forget()
        
        self.load_reports()
    
    def load_reports(self, event=None):
        """Tải và hiển thị báo cáo"""
        try:
            report_type = self.report_type_var.get()
            period = self.period_var.get() if hasattr(self, 'period_var') else None
            
            if report_type == "Tổng hợp":
                report = self.controller.generate_report("comprehensive")
                self.display_report(report.get("report", ""))
                
            elif report_type == "Tháng":
                report = self.controller.generate_report("monthly", month_year=period)
                self.display_monthly_report(report)
                
            elif report_type == "Năm":
                report = self.controller.generate_report("yearly", year=period)
                self.display_yearly_report(report)
                
            elif report_type == "Danh mục":
                report = self.controller.generate_report("category")
                self.display_category_report(report)
                
            elif report_type == "Xu hướng":
                report = self.controller.generate_report("trend")
                self.display_trend_report(report)
                
            elif report_type == "Sức khỏe tài chính":
                report = self.controller.generate_report("health")
                self.display_health_report(report)
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải báo cáo: {e}")
    
    def display_report(self, report_content: str):
        """Hiển thị nội dung báo cáo"""
        self.report_text.delete(1.0, tk.END)
        self.report_text.insert(tk.END, report_content)
    
    def display_monthly_report(self, report_data: Dict[str, Any]):
        """Hiển thị báo cáo tháng"""
        if not report_data or "summary" not in report_data:
            self.display_report("Không có dữ liệu cho kỳ báo cáo này")
            return
        
        summary = report_data["summary"]
        report = f"""
╔══════════════════════════════════════════════════════════════╗
║                     BÁO CÁO THÁNG {report_data['month_year']}                    ║
╚══════════════════════════════════════════════════════════════╝

💰 TỔNG QUAN
────────────────────────────────────────────────────────────────
• Thu nhập: {summary['income']:,.0f} VNĐ
• Chi tiêu: {summary['expense']:,.0f} VNĐ
• Số dư: {summary['balance']:,.0f} VNĐ
• Tỷ lệ tiết kiệm: {summary.get('savings_rate', 0):.1f}%
• Số giao dịch: {summary['transaction_count']}
• Giao dịch TB: {summary.get('avg_transaction', 0):,.0f} VNĐ
• Chi tiêu lớn nhất: {summary.get('max_single_expense', 0):,.0f} VNĐ
• Thu nhập lớn nhất: {summary.get('max_single_income', 0):,.0f} VNĐ

📊 CHI TIÊU THEO DANH MỤC
────────────────────────────────────────────────────────────────"""
        
        # Thêm thông tin chi tiêu theo danh mục
        expense_categories = report_data.get("expense_by_category", {})
        if expense_categories:
            sorted_categories = sorted(expense_categories.items(), key=lambda x: x[1], reverse=True)
            for category, amount in sorted_categories:
                percentage = (amount / summary['expense'] * 100) if summary['expense'] > 0 else 0
                report += f"\n• {category:<15}: {amount:>15,.0f} VNĐ ({percentage:>5.1f}%)"
        
        # Thêm thông tin theo tuần
        weekly_data = report_data.get("weekly_data", {})
        if weekly_data:
            report += "\n\n📅 PHÂN TÍCH THEO TUẦN"
            report += "\n────────────────────────────────────────────────────────────────"
            for week, data in sorted(weekly_data.items()):
                report += f"\nTuần {week}:"
                report += f"\n  • Thu nhập: {data['income']:,.0f} VNĐ"
                report += f"\n  • Chi tiêu: {data['expense']:,.0f} VNĐ"
                balance = data['income'] - data['expense']
                report += f"\n  • Số dư: {balance:,.0f} VNĐ"
        
        report += "\n\n═══════════════════════════════════════════════════════════════"
        self.display_report(report)
    
    def display_yearly_report(self, report_data: Dict[str, Any]):
        """Hiển thị báo cáo năm"""
        if not report_data or "summary" not in report_data:
            self.display_report("Không có dữ liệu cho năm này")
            return
        
        summary = report_data["summary"]
        report = f"""
╔══════════════════════════════════════════════════════════════╗
║                     BÁO CÁO NĂM {report_data['year']}                         ║
╚══════════════════════════════════════════════════════════════╝

💰 TỔNG QUAN NĂM
────────────────────────────────────────────────────────────────
• Tổng thu nhập: {summary['total_income']:,.0f} VNĐ
• Tổng chi tiêu: {summary['total_expense']:,.0f} VNĐ
• Số dư năm: {summary['total_balance']:,.0f} VNĐ
• Thu nhập TB/tháng: {summary['avg_monthly_income']:,.0f} VNĐ
• Chi tiêu TB/tháng: {summary['avg_monthly_expense']:,.0f} VNĐ
• Số dư TB/tháng: {summary.get('avg_monthly_balance', 0):,.0f} VNĐ
• Tỷ lệ tiết kiệm: {summary.get('savings_rate', 0):.1f}%
• Tổng giao dịch: {summary['transaction_count']}

📈 PHÂN TÍCH THEO THÁNG
────────────────────────────────────────────────────────────────"""
        
        # Thêm thông tin theo tháng
        monthly_data = report_data.get("monthly_breakdown", {})
        if monthly_data:
            for month, data in sorted(monthly_data.items()):
                report += f"\n{month}:"
                report += f"\n  • Thu nhập: {data['income']:,.0f} VNĐ"
                report += f"\n  • Chi tiêu: {data['expense']:,.0f} VNĐ"
                report += f"\n  • Số dư: {data['balance']:,.0f} VNĐ"
                report += f"\n  • Giao dịch: {data.get('transaction_count', 0)}"
                report += "\n  ────────────────────────────────"
        
        # Thêm phân tích xu hướng
        trend_analysis = report_data.get("trend_analysis", {})
        if trend_analysis:
            report += "\n\n📊 XU HƯỚNG THEO THÁNG"
            report += "\n────────────────────────────────────────────────────────────────"
            
            for trend_type, trend_data in trend_analysis.items():
                if trend_data:
                    report += f"\n{trend_type.replace('_trend', '').title()}:"
                    for data in trend_data:
                        change_symbol = "↑" if data['change'] > 0 else "↓" if data['change'] < 0 else "→"
                        report += f"\n  • {data['month']}: {change_symbol} {abs(data['change']):,.0f} VNĐ ({data['percentage']:+.1f}%)"
        
        report += "\n\n═══════════════════════════════════════════════════════════════"
        self.display_report(report)
    
    def display_category_report(self, categories: list):
        """Hiển thị báo cáo theo danh mục"""
        if not categories:
            self.display_report("Không có dữ liệu danh mục")
            return
        
        report = """
╔══════════════════════════════════════════════════════════════╗
║                    PHÂN TÍCH THEO DANH MỤC                   ║
╚══════════════════════════════════════════════════════════════╝

📊 CHI TIẾT TỪNG DANH MỤC
────────────────────────────────────────────────────────────────"""
        
        for category in categories:
            report += f"""
{category['category']}:
• Tổng chi tiêu: {category['total_amount']:,.0f} VNĐ ({category['percentage']:.1f}%)
• Số giao dịch: {category['transaction_count']}
• Trung bình/GD: {category['avg_amount']:,.0f} VNĐ
• Thấp nhất: {category['min_amount']:,.0f} VNĐ
• Cao nhất: {category['max_amount']:,.0f} VNĐ

📈 Xu hướng theo tháng:"""
            
            monthly_trend = category.get('monthly_trend', [])
            if monthly_trend:
                for trend in monthly_trend:
                    change_symbol = "↑" if trend['change'] > 0 else "↓" if trend['change'] < 0 else "→"
                    report += f"\n  • {trend['month']}: {change_symbol} {abs(trend['change']):,.0f} VNĐ ({trend['percentage']:+.1f}%)"
            
            report += "\n────────────────────────────────────────────────────────────────"
        
        report += "\n═══════════════════════════════════════════════════════════════"
        self.display_report(report)
    
    def display_trend_report(self, trend_data: Dict[str, Any]):
        """Hiển thị báo cáo xu hướng"""
        if not trend_data or "monthly_data" not in trend_data:
            self.display_report("Không có dữ liệu xu hướng")
            return
        
        report = f"""
╔══════════════════════════════════════════════════════════════╗
║                     PHÂN TÍCH XU HƯỚNG                       ║
╚══════════════════════════════════════════════════════════════╝

📈 XU HƯỚNG CHUNG ({trend_data['periods_analyzed']} THÁNG GẦN NHẤT)
────────────────────────────────────────────────────────────────
• Thu nhập: {trend_data['trends']['income']}
• Chi tiêu: {trend_data['trends']['expense']}
• Số dư: {trend_data['trends']['balance']}
• Tỷ lệ tiết kiệm: {trend_data['trends'].get('savings_rate', 'không đủ dữ liệu')}

📊 TỐC ĐỘ TĂNG TRƯỞNG
────────────────────────────────────────────────────────────────
• Thu nhập: {trend_data['growth_rates']['income']:+.1f}%
• Chi tiêu: {trend_data['growth_rates']['expense']:+.1f}%
• Số dư: {trend_data['growth_rates']['balance']:+.1f}%

📅 DỮ LIỆU THEO THÁNG
────────────────────────────────────────────────────────────────"""
        
        for data in trend_data['monthly_data']:
            report += f"""
{data['month']}:
• Thu nhập: {data['income']:,.0f} VNĐ
• Chi tiêu: {data['expense']:,.0f} VNĐ
• Số dư: {data['balance']:,.0f} VNĐ
• Tỷ lệ tiết kiệm: {data.get('savings_rate', 0):.1f}%
• Số giao dịch: {data['transaction_count']}
────────────────────────────────────────────────────────────────"""
        
        report += "\n═══════════════════════════════════════════════════════════════"
        self.display_report(report)
    
    def display_health_report(self, health_data: Dict[str, Any]):
        """Hiển thị báo cáo sức khỏe tài chính"""
        if not health_data:
            self.display_report("Không có dữ liệu đánh giá sức khỏe tài chính")
            return
        
        report = f"""
╔══════════════════════════════════════════════════════════════╗
║                  ĐÁNH GIÁ SỨC KHỎE TÀI CHÍNH                 ║
╚══════════════════════════════════════════════════════════════╝

📊 ĐIỂM SỐ: {health_data['score']}/100 ({health_data['level']})
Tháng đánh giá: {health_data['month_analyzed']}

📈 CHỈ SỐ CHI TIẾT
────────────────────────────────────────────────────────────────"""
        
        details = health_data.get('details', {})
        if details:
            if 'expense_ratio' in details:
                report += f"\n• Tỷ lệ chi tiêu/thu nhập: {details['expense_ratio']*100:.1f}%"
            if 'savings_rate' in details:
                report += f"\n• Tỷ lệ tiết kiệm: {details['savings_rate']:.1f}%"
            if 'transaction_count' in details:
                report += f"\n• Số lượng giao dịch: {details['transaction_count']}"
        
        report += "\n\n💡 KHUYẾN NGHỊ"
        report += "\n────────────────────────────────────────────────────────────────"
        
        for rec in health_data.get('recommendations', []):
            icon = "⚠️ " if rec['type'] == "warning" else "❗" if rec['type'] == "critical" else "ℹ️ "
            report += f"\n{icon} {rec['message']}"
            report += f"\n  ➤ {rec['action']}"
            report += "\n"
        
        report += "\n═══════════════════════════════════════════════════════════════"
        self.display_report(report)
    
    def on_close(self):
        """Xử lý khi đóng cửa sổ"""
        self.window.destroy() 