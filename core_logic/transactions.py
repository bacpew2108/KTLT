#Quản lý giao dịch  

from datetime import datetime
from typing import List, Dict, Any, Tuple
from storage.file_handler import FileHandler
from utils.validators import (
    validate_date, validate_amount, validate_category, 
    validate_description, validate_transaction_type, sanitize_input
)
from config import DEFAULT_CATEGORIES
from core_logic.models import Transaction
from core_logic.transaction_bst import TransactionBST
from core_logic.transaction_cache import TransactionCache

class TransactionManager:
    """Class quản lý các giao dịch"""
    
    def __init__(self):
        self.file_handler = FileHandler()
        self.transactions: List[Transaction] = []
        self.transaction_tree = TransactionBST()
        self.cache = TransactionCache()
        self.load_transactions()
    
    def load_transactions(self) -> bool:
        """Tải tất cả giao dịch từ file"""
        try:
            transaction_dicts = self.file_handler.load_transactions()
            
            self.transactions = []
            self.transaction_tree = TransactionBST()
            
            for data in transaction_dicts:
                transaction = Transaction.from_dict(data)
                self.transactions.append(transaction)
                try:
                    self.transaction_tree.insert(transaction)
                except Exception as e:
                    print(f"Lỗi khi thêm giao dịch vào BST: {e}")
                    continue
            
            return True
        except Exception as e:
            print(f"Lỗi khi tải giao dịch: {e}")
            return False
    
    def add_transaction(self, date: str, transaction_type: str, category: str, 
                       amount: float, description: str = "", timestamp: str = None) -> Tuple[bool, str]:
        """Thêm giao dịch mới"""
        # Validate dữ liệu đầu vào
        validations = [
            validate_date(date),
            validate_transaction_type(transaction_type),
            validate_category(category, transaction_type),
            validate_amount(amount),
            validate_description(description)
        ]
        
        for is_valid, error_msg in validations:
            if not is_valid:
                return False, error_msg
        
        try:
            # Sanitize input
            date = sanitize_input(date)
            category = sanitize_input(category)
            description = sanitize_input(description)
            
            # Tạo transaction mới
            transaction = Transaction(
                date=date,
                transaction_type=transaction_type,
                category=category,
                amount=float(amount),
                description=description,
                timestamp=timestamp
            )
            
            # Lưu vào file
            success = self.file_handler.save_transaction(transaction.to_dict())
            if success:
                # Thêm vào memory và BST
                self.transactions.append(transaction)
                self.transaction_tree.insert(transaction)
                
                # Clear cache vì dữ liệu đã thay đổi
                self.cache = TransactionCache()
                
                return True, "Đã thêm giao dịch thành công!"
            else:
                return False, "Không thể lưu giao dịch vào file!"
            
        except Exception as e:
            return False, f"Lỗi khi thêm giao dịch: {e}"
    
    def get_transactions(self, start_date: str = None, end_date: str = None, 
                        transaction_type: str = None, category: str = None) -> List[Transaction]:
        """Lấy danh sách giao dịch với bộ lọc"""
        try:
            if start_date and end_date:
                # Thử sử dụng BST trước
                try:
                    filtered_transactions = self.transaction_tree.find_range(start_date, end_date)
                except Exception as e:
                    print(f"Lỗi khi tìm trong BST: {e}")
                    # Fallback về tìm kiếm tuần tự
                    filtered_transactions = [
                        t for t in self.transactions 
                        if start_date <= t.date <= end_date
                    ]
            else:
                filtered_transactions = self.transactions.copy()
            
            # Lọc theo loại giao dịch và danh mục
            if transaction_type:
                filtered_transactions = [
                    t for t in filtered_transactions if t.type == transaction_type
                ]
            
            if category:
                filtered_transactions = [
                    t for t in filtered_transactions if t.category == category
                ]
            
            return filtered_transactions
            
        except Exception as e:
            print(f"Lỗi khi lọc giao dịch: {e}")
            return []
    
    def get_monthly_summary(self, month_year: str = None) -> Dict[str, Any]:
        """Tạo tóm tắt theo tháng với cache"""
        if month_year is None:
            month_year = datetime.now().strftime("%m/%Y")
            
        # Kiểm tra cache
        cached_summary = self.cache.get_monthly_summary(month_year)
        if cached_summary:
            return cached_summary
            
        # Tính toán mới nếu không có trong cache
        monthly_transactions = [t for t in self.transactions if t.get_month_year() == month_year]
        
        income = sum(t.amount for t in monthly_transactions if t.type in ["Thu nhập", "income"])
        expense = sum(t.amount for t in monthly_transactions if t.type in ["Chi tiêu", "expense"])
        balance = income - expense
        
        summary = {
            "month_year": month_year,
            "income": income,
            "expense": expense,
            "balance": balance,
            "transaction_count": len(monthly_transactions)
        }
        
        # Lưu vào cache
        self.cache.cache_monthly_summary(month_year, summary)
        
        return summary

    def delete_transaction(self, transaction_data: Dict[str, Any]) -> Tuple[bool, str]:
        """Xóa một giao dịch"""
        try:
            # Validate dữ liệu đầu vào
            if not isinstance(transaction_data, dict):
                return False, "Dữ liệu giao dịch không hợp lệ"
            
            required_fields = ["date", "type", "category", "amount", "timestamp"]
            for field in required_fields:
                if field not in transaction_data:
                    return False, f"Thiếu thông tin {field}"
            
            # Tìm giao dịch cần xóa
            for i, transaction in enumerate(self.transactions):
                # So sánh từng trường
                date_match = transaction.date == transaction_data["date"]
                type_match = transaction.type == transaction_data["type"]
                category_match = transaction.category == transaction_data["category"]
                amount_match = round(float(transaction.amount), 2) == round(float(transaction_data["amount"]), 2)
                desc_match = transaction.description == transaction_data.get("description", "")
                timestamp_match = transaction.timestamp == transaction_data["timestamp"]
                
                if date_match and type_match and category_match and amount_match and desc_match and timestamp_match:
                    # Xóa khỏi memory
                    del self.transactions[i]
                    
                    # Cập nhật file
                    success = self.file_handler.update_transactions([t.to_dict() for t in self.transactions])
                    if success:
                        # Clear cache và rebuild BST
                        self.cache = TransactionCache()
                        self.transaction_tree = TransactionBST()
                        for t in self.transactions:
                            self.transaction_tree.insert(t)
                            
                        return True, "Đã xóa giao dịch thành công!"
                    else:
                        return False, "Không thể cập nhật file dữ liệu!"
            
            return False, "Không tìm thấy giao dịch cần xóa!"
            
        except Exception as e:
            print(f"Error in delete_transaction: {e}")
            return False, f"Lỗi khi xóa giao dịch: {e}"