#Class chính điều khiển ứng dụng

import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from typing import List, Dict, Any, Tuple

# Import các modules
from core_logic.transactions import TransactionManager, Transaction
from core_logic.budget import BudgetManager
from core_logic.reports import ReportGenerator
from gui.main_window import MainWindow
from config import WINDOW_CONFIG, DEFAULT_CATEGORIES

class AppController:
    """Class chính điều khiển ứng dụng"""
    
    def __init__(self):
        """Khởi tạo AppController với các thành phần cần thiết"""
        self.root = tk.Tk()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Khởi tạo các thành phần
        self.transaction_manager = TransactionManager()
        self.budget_manager = BudgetManager()
        self._transaction_cache = {}
        self._budget_cache = {}
        
        # Tạo giao diện
        self.main_window = MainWindow(self.root, self)
        self.center_window()
        
        # Cấu hình window
        self.root.title(WINDOW_CONFIG["title"])
        self.root.geometry(WINDOW_CONFIG["geometry"])
        self.root.minsize(
            WINDOW_CONFIG["min_size"][0],
            WINDOW_CONFIG["min_size"][1]
        )
    
    def center_window(self) -> None:
        """Căn giữa cửa sổ trên màn hình"""
        try:
            self.root.update_idletasks()
            
            # Lấy kích thước cửa sổ và màn hình
            window_width = self.root.winfo_width()
            window_height = self.root.winfo_height()
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            
            # Tính toán vị trí căn giữa
            x = (screen_width - window_width) // 2
            y = (screen_height - window_height) // 2
            
            self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
            
        except Exception as e:
            print(f"Lỗi căn giữa cửa sổ: {e}")
    
    def on_closing(self) -> None:
        """Xử lý khi đóng ứng dụng"""
        try:
            if messagebox.askokcancel("Thoát", "Bạn có chắc chắn muốn thoát?"):
                self.root.destroy()
        except Exception as e:
            print(f"Lỗi khi đóng ứng dụng: {e}")
            self.root.destroy()
    
    def get_transactions(self, **filters) -> List[Transaction]:
        """Lấy danh sách giao dịch với bộ lọc (có cache)"""
        cache_key = str(filters)
        
        if cache_key not in self._transaction_cache:
            self._transaction_cache[cache_key] = self.transaction_manager.get_transactions(**filters)
        
        return self._transaction_cache[cache_key]
    
    def invalidate_caches(self) -> None:
        """Xóa cache khi có thay đổi dữ liệu"""
        self._transaction_cache.clear()
        self._budget_cache.clear()
        # Refresh display để cập nhật giao diện
        self.refresh_display()
    
    def add_transaction(self, transaction_data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Thêm giao dịch mới với validation và xử lý lỗi
        
        Args:
            transaction_data: Dictionary chứa thông tin giao dịch
            
        Returns:
            Tuple[bool, str]: (Thành công?, Message)
        """
        try:
            # Validate dữ liệu đầu vào
            success, message = self._validate_transaction_data(transaction_data)
            if not success:
                return False, message
            
            success, message = self.transaction_manager.add_transaction(
                date=transaction_data["date"],
                transaction_type=transaction_data["type"],
                category=transaction_data["category"],
                amount=transaction_data["amount"],
                description=transaction_data.get("description", ""),
                timestamp=transaction_data.get("timestamp")
            )
            
            if success:
                # Xóa cache khi có thay đổi
                self.invalidate_caches()
                
                # Kiểm tra cảnh báo ngân sách
                if transaction_data["type"] == "Chi tiêu":
                    self.check_budget_warning(transaction_data)
                
                messagebox.showinfo("Thành công", message)
            else:
                messagebox.showerror("Lỗi", message)
            
            return success, message
                
        except Exception as e:
            error_msg = f"Lỗi không mong đợi khi thêm giao dịch: {str(e)}"
            messagebox.showerror("Lỗi", error_msg)
            return False, error_msg
    
    def _validate_transaction_data(self, data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Kiểm tra tính hợp lệ của dữ liệu giao dịch
        
        Args:
            data: Dictionary chứa dữ liệu cần kiểm tra
            
        Returns:
            Tuple[bool, str]: (Thành công?, Message)
        """
        required_fields = ["date", "type", "category", "amount"]
        
        try:
            # Kiểm tra các trường bắt buộc
            if not all(field in data for field in required_fields):
                missing_fields = [field for field in required_fields if field not in data]
                return False, f"Thiếu thông tin: {', '.join(missing_fields)}"
            
            # Kiểm tra kiểu dữ liệu
            if not isinstance(data["amount"], (int, float)) or data["amount"] <= 0:
                return False, "Số tiền phải là số dương"
                
            # Kiểm tra ngày hợp lệ
            try:
                datetime.strptime(data["date"], "%d/%m/%Y")
            except ValueError:
                return False, "Định dạng ngày không đúng (DD/MM/YYYY)"
            
            # Kiểm tra loại giao dịch
            if data["type"] not in ["Thu nhập", "Chi tiêu"]:
                return False, "Loại giao dịch không hợp lệ"
            
            # Kiểm tra danh mục
            valid_categories = (DEFAULT_CATEGORIES["income"] if data["type"] == "Thu nhập" 
                              else DEFAULT_CATEGORIES["expense"])
            if data["category"] not in valid_categories:
                return False, f"Danh mục không hợp lệ cho {data['type'].lower()}"
            
            return True, ""
            
        except Exception as e:
            print(f"Lỗi validate dữ liệu giao dịch: {e}")
            return False, f"Lỗi validate dữ liệu giao dịch: {e}"
    
    def delete_transaction(self, transaction_data: Dict[str, Any]) -> bool:
        """
        Xóa giao dịch
        
        Args:
            transaction_data: Dictionary chứa thông tin giao dịch cần xóa
            
        Returns:
            bool: True nếu thành công
        """
        try:
            if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa giao dịch này?"):
                success, message = self.transaction_manager.delete_transaction(transaction_data)
                
                if success:
                    messagebox.showinfo("Thành công", message)
                    self.invalidate_caches()
                    return True
                else:
                    messagebox.showerror("Lỗi", message)
                    return False
            return False
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể xóa giao dịch: {e}")
            return False
    
    def get_all_transactions(self) -> List[Transaction]:
        """Lấy tất cả giao dịch"""
        return self.transaction_manager.transactions
    
    # Phương thức đặt ngân sách
    def set_budget(self, category: str, amount: float, month_year: str = None) -> bool:
        """
        Đặt ngân sách
        
        Args:
            category: Danh mục
            amount: Số tiền ngân sách
            month_year: Tháng/năm
            
        Returns:
            bool: True nếu thành công
        """
        try:
            success, message = self.budget_manager.set_budget(category, amount, month_year)
            
            if success:
                messagebox.showinfo("Thành công", message)
                self.invalidate_caches()
                return True
            else:
                messagebox.showerror("Lỗi", message)
                return False
                
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể đặt ngân sách: {e}")
            return False
    
    def get_budget_status(self, category: str, month_year: str = None) -> Dict[str, Any]:
        """Lấy trạng thái ngân sách"""
        transactions = self.get_all_transactions()
        return self.budget_manager.get_budget_status(transactions, category, month_year)
    
    def get_all_budget_status(self, month_year: str = None) -> List[Dict[str, Any]]:
        """Lấy trạng thái tất cả ngân sách"""
        transactions = self.get_all_transactions()
        return self.budget_manager.get_all_budget_status(transactions, month_year)
    
    def check_budget_warning(self, transaction_data: Dict[str, Any]):
        """Kiểm tra và hiển thị cảnh báo ngân sách"""
        if transaction_data["type"] == "Chi tiêu":
            current_month = datetime.now().strftime("%m/%Y")
            status = self.get_budget_status(transaction_data["category"], current_month)
            
            if status["status"] == "Vượt quá":
                messagebox.showwarning(
                    "Cảnh báo ngân sách!",
                    f"Bạn đã vượt ngân sách danh mục '{transaction_data['category']}'!\n"
                    f"Ngân sách: {status['budget']:,.0f} VNĐ\n"
                    f"Đã chi: {status['spent']:,.0f} VNĐ\n"
                    f"Vượt quá: {status['spent'] - status['budget']:,.0f} VNĐ"
                )
            elif status["status"] == "Cảnh báo":
                messagebox.showwarning(
                    "Cảnh báo ngân sách!",
                    f"Chi tiêu danh mục '{transaction_data['category']}' đang gần đạt ngân sách!\n"
                    f"Ngân sách: {status['budget']:,.0f} VNĐ\n"
                    f"Đã chi: {status['spent']:,.0f} VNĐ ({status['percentage']:.1f}%)\n"
                    f"Còn lại: {status['remaining']:,.0f} VNĐ"
                )
    
    # Báo cáo ngân sách
    def generate_report(self, report_type: str, **kwargs) -> Dict[str, Any]:
        """
        Tạo báo cáo
        
        Args:
            report_type: Loại báo cáo
            **kwargs: Các tham số khác
            
        Returns:
            Dict: Dữ liệu báo cáo
        """
        try:
            transactions = self.get_all_transactions()
            report_generator = ReportGenerator(transactions)
            
            if report_type == "monthly":
                return report_generator.get_monthly_report(kwargs.get("month_year"))
            elif report_type == "yearly":
                return report_generator.get_yearly_report(kwargs.get("year"))
            elif report_type == "category":
                return report_generator.get_category_analysis(kwargs.get("transaction_type", "Chi tiêu"))
            elif report_type == "trend":
                return report_generator.get_trend_analysis(kwargs.get("months", 12))
            elif report_type == "health":
                return report_generator.get_financial_health_score()
            elif report_type == "comprehensive":
                return {"report": report_generator.export_comprehensive_report(kwargs.get("format_type", "text"))}
            else:
                return {"error": "Loại báo cáo không hợp lệ"}
                
        except Exception as e:
            return {"error": f"Lỗi khi tạo báo cáo: {e}"}
    
    # Quản lý dữ liệu
    def get_summary_data(self) -> Dict[str, Any]:
        """Lấy dữ liệu tóm tắt"""
        try:
            transactions = self.get_all_transactions()
            
            # Tổng quan tất cả
            total_income = sum(t.amount for t in transactions if t.type in ['Thu nhập', 'income'])
            total_expense = sum(t.amount for t in transactions if t.type in ['Chi tiêu', 'expense'])
            total_balance = total_income - total_expense
            
            # Tháng hiện tại
            current_month = datetime.now().strftime("%m/%Y")
            monthly_transactions = [t for t in transactions if t.get_month_year() == current_month]
            monthly_income = sum(t.amount for t in monthly_transactions if t.type in ['Thu nhập', 'income'])
            monthly_expense = sum(t.amount for t in monthly_transactions if t.type in ['Chi tiêu', 'expense'])
            monthly_balance = monthly_income - monthly_expense
            
            return {
                'total_income': total_income,
                'total_expense': total_expense,
                'total_balance': total_balance,
                'current_month': current_month,
                'monthly_income': monthly_income,
                'monthly_expense': monthly_expense,
                'monthly_balance': monthly_balance,
                'transaction_count': len(transactions)
            }
            
        except Exception as e:
            print(f"Lỗi khi lấy dữ liệu tóm tắt: {e}")
            return {}
    
    def refresh_display(self):
        """Cập nhật lại giao diện"""
        try:
            # Cập nhật danh sách giao dịch
            self.main_window.update_transaction_list()
            # Cập nhật tóm tắt
            self.main_window.update_summary()
        except Exception as e:
            print(f"Lỗi khi refresh giao diện: {e}")
    
    def get_file_info(self) -> Dict[str, Any]:
        """Lấy thông tin file dữ liệu"""
        try:
            file_handler = self.transaction_manager.file_handler
            return file_handler.get_file_info()
        except Exception as e:
            print(f"Lỗi khi lấy thông tin file: {e}")
            return {}
    
    def run(self):
        """Chạy ứng dụng"""
        try:
            self.root.mainloop()
        except Exception as e:
            messagebox.showerror("Lỗi nghiêm trọng", f"Ứng dụng gặp lỗi: {e}") 