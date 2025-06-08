#Quản lý ngân sách

from datetime import datetime
from typing import List, Dict, Any, Tuple
from storage.file_handler import FileHandler
from utils.validators import validate_budget_amount, validate_month_year, validate_category
from config import DEFAULT_CATEGORIES, REPORT_CONFIG


class BudgetManager:
    """Class quản lý ngân sách"""
    
    def __init__(self):
        self.file_handler = FileHandler()
        self.warning_threshold = REPORT_CONFIG["budget_warning_threshold"]
    
    def set_budget(self, category: str, amount: float, month_year: str = None) -> Tuple[bool, str]:
        """
        Đặt ngân sách cho một danh mục
        
        Args:
            category: Danh mục
            amount: Số tiền ngân sách
            month_year: Tháng/năm (MM/YYYY), mặc định là tháng hiện tại
            
        Returns:
            Tuple[bool, str]: (success, message)
        """
        if month_year is None:
            month_year = datetime.now().strftime("%m/%Y")
        
        # Kiểm tra đầu vào
        validations = [
            validate_category(category, "Chi tiêu"),
            validate_budget_amount(amount),
            validate_month_year(month_year)
        ]
        
        for is_valid, error_msg in validations:
            if not is_valid:
                return False, error_msg
        
        try:
            success = self.file_handler.save_budget(category, float(amount), month_year)
            if success:
                return True, f"Đã đặt ngân sách {amount:,.0f} VNĐ cho '{category}' tháng {month_year}"
            else:
                return False, "Không thể lưu ngân sách!"
        except Exception as e:
            return False, f"Lỗi khi đặt ngân sách: {e}"
    
    def get_budget(self, category: str, month_year: str = None) -> float:
        """
        Lấy ngân sách của một danh mục
        
        Args:
            category: Danh mục
            month_year: Tháng/năm (MM/YYYY)
            
        Returns:
            float: Số tiền ngân sách
        """
        if month_year is None:
            month_year = datetime.now().strftime("%m/%Y")
        
        try:
            budgets = self.file_handler.load_budgets()
            for budget in budgets:
                if budget["category"] == category and budget["month_year"] == month_year:
                    return budget["amount"]
            return 0.0
        except Exception as e:
            print(f"Lỗi khi lấy ngân sách: {e}")
            return 0.0
    
    def get_all_budgets(self, month_year: str = None) -> Dict[str, float]:
        """
        Lấy tất cả ngân sách của một tháng
        
        Args:
            month_year: Tháng/năm (MM/YYYY)
            
        Returns:
            Dict[str, float]: Dictionary {category: amount}
        """
        if month_year is None:
            month_year = datetime.now().strftime("%m/%Y")
        
        try:
            budgets = self.file_handler.load_budgets()
            result = {}
            for budget in budgets:
                if budget["month_year"] == month_year:
                    result[budget["category"]] = budget["amount"]
            return result
        except Exception as e:
            print(f"Lỗi khi lấy tất cả ngân sách: {e}")
            return {}
    
    def delete_budget(self, category: str, month_year: str = None) -> Tuple[bool, str]:
        """
        Xóa ngân sách của một danh mục
        
        Args:
            category: Danh mục
            month_year: Tháng/năm (MM/YYYY)
            
        Returns:
            Tuple[bool, str]: (success, message)
        """
        if month_year is None:
            month_year = datetime.now().strftime("%m/%Y")
        
        try:
            budgets = self.file_handler.load_budgets()
            
            # Tìm và xóa budget
            updated_budgets = []
            found = False
            for budget in budgets:
                if budget["category"] == category and budget["month_year"] == month_year:
                    found = True
                    continue  # Bỏ qua budget này (xóa nó)
                updated_budgets.append(budget)
            
            if found:
                success = self.file_handler._save_all_budgets(updated_budgets)
                if success:
                    return True, f"Đã xóa ngân sách cho '{category}' tháng {month_year}"
                else:
                    return False, "Không thể lưu thay đổi!"
            else:
                return False, f"Không tìm thấy ngân sách cho '{category}' tháng {month_year}"
                
        except Exception as e:
            return False, f"Lỗi khi xóa ngân sách: {e}"
    
    def calculate_spent_amount(self, transactions: List[Any], category: str, month_year: str) -> float:
        """
        Tính tổng chi tiêu của một danh mục trong tháng
        
        Args:
            transactions: Danh sách giao dịch
            category: Danh mục
            month_year: Tháng/năm (MM/YYYY)
            
        Returns:
            float: Tổng chi tiêu
        """
        total = 0.0
        for transaction in transactions:
            if (hasattr(transaction, 'type') and transaction.type == "Chi tiêu" and
                hasattr(transaction, 'category') and transaction.category == category and
                hasattr(transaction, 'get_month_year') and transaction.get_month_year() == month_year):
                total += transaction.amount
        return total
    
    def get_budget_status(self, transactions: List[Any], category: str, month_year: str = None) -> Dict[str, Any]:
        """
        Lấy trạng thái ngân sách của một danh mục
        
        Args:
            transactions: Danh sách giao dịch
            category: Danh mục  
            month_year: Tháng/năm (MM/YYYY)
            
        Returns:
            Dict: Trạng thái ngân sách
        """
        if month_year is None:
            month_year = datetime.now().strftime("%m/%Y")
        
        budget_amount = self.get_budget(category, month_year)
        spent_amount = self.calculate_spent_amount(transactions, category, month_year)
        remaining = budget_amount - spent_amount
        
        # Xác định trạng thái
        if budget_amount == 0:
            status = "Chưa đặt"
            percentage = 0
        else:
            percentage = (spent_amount / budget_amount) * 100
            if spent_amount > budget_amount:
                status = "Vượt quá"
            elif spent_amount > budget_amount * self.warning_threshold:
                status = "Cảnh báo"
            else:
                status = "An toàn"
        
        return {
            "category": category,
            "budget": budget_amount,
            "spent": spent_amount,
            "remaining": remaining,
            "percentage": percentage,
            "status": status,
            "month_year": month_year
        }
    
    def get_all_budget_status(self, transactions: List[Any], month_year: str = None) -> List[Dict[str, Any]]:
        """
        Lấy trạng thái ngân sách của tất cả danh mục
        
        Args:
            transactions: Danh sách giao dịch
            month_year: Tháng/năm (MM/YYYY)
            
        Returns:
            List[Dict]: Danh sách trạng thái ngân sách
        """
        if month_year is None:
            month_year = datetime.now().strftime("%m/%Y")
        
        statuses = []
        # Lấy tất cả danh mục chi tiêu từ cấu hình
        all_expense_categories = DEFAULT_CATEGORIES["expense"]
        
        # Lấy tất cả ngân sách đã đặt cho tháng này
        current_budgets = self.get_all_budgets(month_year)
        
        # Lấy chi tiêu cho từng danh mục
        for category in all_expense_categories:
            # Lấy ngân sách nếu có
            budget_amount = current_budgets.get(category, 0.0)
            
            # Tính toán chi tiêu
            spent_amount = self.calculate_spent_amount(transactions, category, month_year)
            remaining = budget_amount - spent_amount
            
            # Xác định trạng thái
            if budget_amount == 0:
                status = "Chưa đặt"
                percentage = 0
            else:
                percentage = (spent_amount / budget_amount) * 100
                if spent_amount > budget_amount:
                    status = "Vượt quá"
                elif spent_amount > budget_amount * self.warning_threshold:
                    status = "Cảnh báo"
                else:
                    status = "An toàn"
            
            # Thêm vào danh sách trạng thái
            statuses.append({
                "category": category,
                "budget": budget_amount,
                "spent": spent_amount,
                "remaining": remaining,
                "percentage": percentage,
                "status": status,
                "month_year": month_year
            })
        
        return statuses
    
    def check_budget_warnings(self, transactions: List[Any], month_year: str = None) -> List[Dict[str, Any]]:
        """
        Kiểm tra các cảnh báo ngân sách
        
        Args:
            transactions: Danh sách giao dịch
            month_year: Tháng/năm (MM/YYYY)
            
        Returns:
            List[Dict]: Danh sách cảnh báo
        """
        warnings = []
        statuses = self.get_all_budget_status(transactions, month_year)
        
        for status in statuses:
            if status["status"] in ["Cảnh báo", "Vượt quá"] and status["budget"] > 0:
                warnings.append(status)
        
        return warnings
    
    def get_budget_summary(self, transactions: List[Any], month_year: str = None) -> Dict[str, Any]:
        """
        Lấy tóm tắt ngân sách tổng thể
        
        Args:
            transactions: Danh sách giao dịch
            month_year: Tháng/năm (MM/YYYY)
            
        Returns:
            Dict: Tóm tắt ngân sách
        """
        if month_year is None:
            month_year = datetime.now().strftime("%m/%Y")
        
        statuses = self.get_all_budget_status(transactions, month_year)
        
        total_budget = sum(status["budget"] for status in statuses if status["budget"] > 0)
        total_spent = sum(status["spent"] for status in statuses)
        total_remaining = total_budget - total_spent
        
        # Đếm số danh mục theo trạng thái
        status_counts = {"An toàn": 0, "Cảnh báo": 0, "Vượt quá": 0, "Chưa đặt": 0}
        for status in statuses:
            status_counts[status["status"]] += 1
        
        return {
            "month_year": month_year,
            "total_budget": total_budget,
            "total_spent": total_spent,
            "total_remaining": total_remaining,
            "percentage_used": (total_spent / total_budget * 100) if total_budget > 0 else 0,
            "status_counts": status_counts,
            "categories_with_budget": len([s for s in statuses if s["budget"] > 0])
        }
    
    def suggest_budget_adjustments(self, transactions: List[Any], month_year: str = None) -> List[Dict[str, Any]]:
        """
        Đề xuất điều chỉnh ngân sách
        
        Args:
            transactions: Danh sách giao dịch
            month_year: Tháng/năm (MM/YYYY)
            
        Returns:
            List[Dict]: Danh sách đề xuất
        """
        if month_year is None:
            month_year = datetime.now().strftime("%m/%Y")
        
        suggestions = []
        statuses = self.get_all_budget_status(transactions, month_year)
        
        for status in statuses:
            category = status["category"]
            current_budget = status["budget"]
            spent = status["spent"]
            
            if current_budget == 0 and spent > 0:
                # Đề xuất đặt ngân sách cho danh mục chưa có
                suggested_budget = spent * 1.2  # 120% chi tiêu hiện tại
                suggestions.append({
                    "category": category,
                    "type": "new_budget",
                    "suggested_amount": suggested_budget,
                    "reason": f"Đề xuất đặt ngân sách vì đã chi tiêu {spent:,.0f} VNĐ"
                })
            elif status["status"] == "Vượt quá":
                # Đề xuất tăng ngân sách cho danh mục vượt quá
                suggested_budget = spent * 1.1  # 110% chi tiêu hiện tại
                suggestions.append({
                    "category": category,
                    "type": "increase_budget",
                    "current_amount": current_budget,
                    "suggested_amount": suggested_budget,
                    "reason": f"Đã vượt quá {spent - current_budget:,.0f} VNĐ"
                })
        
        return suggestions
    
    def copy_budget_to_next_month(self, current_month_year: str = None) -> Tuple[bool, str]:
        """
        Copy ngân sách từ tháng trước sang tháng hiện tại
        
        Args:
            current_month_year: Tháng/năm hiện tại (MM/YYYY)
            
        Returns:
            Tuple[bool, str]: (success, message)
        """
        if current_month_year is None:
            current_month_year = datetime.now().strftime("%m/%Y")
        
        try:
            # Tính tháng trước
            month, year = current_month_year.split('/')
            month = int(month)
            year = int(year)
            
            if month == 1:
                prev_month = 12
                prev_year = year - 1
            else:
                prev_month = month - 1
                prev_year = year
            
            prev_month_year = f"{prev_month:02d}/{prev_year}"
            
            # Lấy ngân sách tháng trước
            prev_budgets = self.get_all_budgets(prev_month_year)
            
            if not prev_budgets:
                return False, f"Không có ngân sách nào trong tháng {prev_month_year}"
            
            # Copy sang tháng hiện tại
            success_count = 0
            for category, amount in prev_budgets.items():
                success, _ = self.set_budget(category, amount, current_month_year)
                if success:
                    success_count += 1
            
            if success_count == len(prev_budgets):
                return True, f"Đã copy {success_count} ngân sách từ tháng {prev_month_year} sang tháng {current_month_year}"
            elif success_count > 0:
                return True, f"Đã copy {success_count}/{len(prev_budgets)} ngân sách từ tháng {prev_month_year} sang tháng {current_month_year}"
            else:
                return False, "Không thể copy ngân sách nào"
                
        except Exception as e:
            return False, f"Lỗi khi copy ngân sách: {e}"
    
    def get_budget_trend(self, category: str, months: int = 6) -> List[Dict[str, Any]]:
        """
        Lấy xu hướng ngân sách của một danh mục
        
        Args:
            category: Danh mục
            months: Số tháng để phân tích
            
        Returns:
            List[Dict]: Dữ liệu xu hướng ngân sách
        """
        try:
            current_date = datetime.now()
            trend_data = []
            
            for i in range(months):
                # Tính tháng/năm
                month = current_date.month - i
                year = current_date.year
                
                while month <= 0:
                    month += 12
                    year -= 1
                
                month_year = f"{month:02d}/{year}"
                budget_amount = self.get_budget(category, month_year)
                
                trend_data.append({
                    "month_year": month_year,
                    "budget": budget_amount
                })
            
            trend_data.reverse()  # Sắp xếp từ cũ đến mới
            return trend_data
            
        except Exception as e:
            print(f"Lỗi khi lấy xu hướng ngân sách: {e}")
            return [] 