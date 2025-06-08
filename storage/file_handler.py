#Xử lý việc lưu trữ và đọc file dữ liệu

import csv
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
from config import TRANSACTIONS_FILE, BUDGET_FILE, CSV_CONFIG

class FileHandler:
    """Class xử lý việc lưu trữ và đọc file dữ liệu"""
    
    def __init__(self):
        """Khởi tạo với các đường dẫn file"""
        self.transactions_file = Path(TRANSACTIONS_FILE)
        self.budget_file = Path(BUDGET_FILE)
        self.encoding = CSV_CONFIG["encoding"]
        self.delimiter = CSV_CONFIG["delimiter"]
        
        # Tạo file headers nếu chưa tồn tại
        self._initialize_files()
    
    def _initialize_files(self):
        """Khởi tạo file với headers nếu chưa tồn tại"""
        # Initialize transactions file
        if not self.transactions_file.exists():
            self._create_transactions_file()
        
        # Initialize budget file
        if not self.budget_file.exists():
            self._create_budget_file()
    
    def _create_transactions_file(self):
        """Tạo file giao dịch với headers"""
        headers = [
            "timestamp", "date", "type", "category", 
            "amount", "description"
        ]
        
        try:
            with open(self.transactions_file, 'w', newline='', encoding=self.encoding) as file:
                writer = csv.writer(file, delimiter=self.delimiter)
                writer.writerow(headers)
        except Exception as e:
            print(f"Lỗi khi tạo file giao dịch: {e}")
    
    def _create_budget_file(self):
        """Tạo file ngân sách với headers"""
        headers = ["category", "amount", "month_year"]
        
        try:
            with open(self.budget_file, 'w', newline='', encoding=self.encoding) as file:
                writer = csv.writer(file, delimiter=self.delimiter)
                writer.writerow(headers)
        except Exception as e:
            print(f"Lỗi khi tạo file ngân sách: {e}")
    
    def save_transaction(self, transaction_data: Dict[str, Any]) -> bool:
        """
        Lưu một giao dịch vào file CSV
        
        Args:
            transaction_data: Dictionary chứa thông tin giao dịch
            
        Returns:
            bool: True nếu thành công, False nếu thất bại
        """
        try:
            # Thêm timestamp (chỉ thời gian)
            timestamp = datetime.now().strftime(CSV_CONFIG["timestamp_format"])
            
            # Chuẩn bị dữ liệu
            row_data = [
                timestamp,
                transaction_data.get("date", ""),
                transaction_data.get("type", ""),
                transaction_data.get("category", ""),
                transaction_data.get("amount", 0),
                transaction_data.get("description", "")
            ]
            
            # Ghi vào file
            with open(self.transactions_file, 'a', newline='', encoding=self.encoding) as file:
                writer = csv.writer(file, delimiter=self.delimiter)
                writer.writerow(row_data)
            
            return True
            
        except Exception as e:
            print(f"Lỗi khi lưu giao dịch: {e}")
            return False
    
    def load_transactions(self) -> List[Dict[str, Any]]:
        """
        Tải tất cả giao dịch từ file CSV
        
        Returns:
            List[Dict]: Danh sách các giao dịch
        """
        transactions = []
        
        try:
            if not self.transactions_file.exists():
                print("File giao dịch không tồn tại")
                return transactions
            
            with open(self.transactions_file, 'r', encoding=self.encoding) as file:
                reader = csv.DictReader(file, delimiter=self.delimiter)
                
                for row in reader:
                    # Chuyển đổi amount sang float
                    try:
                        amount = float(row.get("amount", 0))
                    except (ValueError, TypeError):
                        print(f"Lỗi chuyển đổi số tiền: {row.get('amount')}")
                        amount = 0.0
                    
                    transaction = {
                        "timestamp": row.get("timestamp", ""),
                        "date": row.get("date", ""),
                        "type": row.get("type", ""),
                        "category": row.get("category", ""),
                        "amount": amount,
                        "description": row.get("description", "")
                    }
                    transactions.append(transaction)
            
        except Exception as e:
            print(f"Lỗi khi tải giao dịch: {e}")
        
        return transactions
    
    def update_transactions(self, transactions: List[Dict[str, Any]]) -> bool:
        """
        Cập nhật toàn bộ file giao dịch
        
        Args:
            transactions: Danh sách tất cả giao dịch
            
        Returns:
            bool: True nếu thành công, False nếu thất bại
        """
        try:
            # Ghi lại file với dữ liệu mới
            with open(self.transactions_file, 'w', newline='', encoding=self.encoding) as file:
                writer = csv.writer(file, delimiter=self.delimiter)
                
                # Ghi headers
                headers = ["timestamp", "date", "type", "category", "amount", "description"]
                writer.writerow(headers)
                
                # Ghi dữ liệu
                for transaction in transactions:
                    row_data = [
                        transaction.get("timestamp", ""),
                        transaction.get("date", ""),
                        transaction.get("type", ""),
                        transaction.get("category", ""),
                        transaction.get("amount", 0),
                        transaction.get("description", "")
                    ]
                    writer.writerow(row_data)
            
            return True
            
        except Exception as e:
            print(f"Lỗi khi cập nhật giao dịch: {e}")
            return False
    
    def save_budget(self, category: str, amount: float, month_year: str) -> bool:
        """
        Lưu ngân sách cho một danh mục
        
        Args:
            category: Danh mục
            amount: Số tiền ngân sách
            month_year: Tháng/năm (MM/YYYY)
            
        Returns:
            bool: True nếu thành công, False nếu thất bại
        """
        try:
            # Đọc dữ liệu hiện tại
            budgets = self.load_budgets()
            
            # Cập nhật hoặc thêm mới
            found = False
            for budget in budgets:
                if budget["category"] == category and budget["month_year"] == month_year:
                    budget["amount"] = amount
                    found = True
                    break
            
            if not found:
                budgets.append({
                    "category": category,
                    "amount": amount,
                    "month_year": month_year
                })
            
            # Lưu lại tất cả
            return self._save_all_budgets(budgets)
            
        except Exception as e:
            print(f"Lỗi khi lưu ngân sách: {e}")
            return False
    
    def load_budgets(self) -> List[Dict[str, Any]]:
        """
        Tải tất cả ngân sách từ file CSV
        
        Returns:
            List[Dict]: Danh sách ngân sách
        """
        budgets = []
        
        try:
            if not self.budget_file.exists():
                return budgets
            
            with open(self.budget_file, 'r', encoding=self.encoding) as file:
                reader = csv.DictReader(file, delimiter=self.delimiter)
                
                for row in reader:
                    # Chuyển đổi amount sang float
                    try:
                        amount = float(row.get("amount", 0))
                    except (ValueError, TypeError):
                        amount = 0.0
                    
                    budget = {
                        "category": row.get("category", ""),
                        "amount": amount,
                        "month_year": row.get("month_year", "")
                    }
                    budgets.append(budget)
            
        except Exception as e:
            print(f"Lỗi khi tải ngân sách: {e}")
        
        return budgets
    
    def _save_all_budgets(self, budgets: List[Dict[str, Any]]) -> bool:
        """
        Lưu tất cả ngân sách vào file
        
        Args:
            budgets: Danh sách tất cả ngân sách
            
        Returns:
            bool: True nếu thành công, False nếu thất bại
        """
        try:
            # Ghi file mới
            with open(self.budget_file, 'w', newline='', encoding=self.encoding) as file:
                writer = csv.writer(file, delimiter=self.delimiter)
                
                # Ghi headers
                headers = ["category", "amount", "month_year"]
                writer.writerow(headers)
                
                # Ghi dữ liệu
                for budget in budgets:
                    row_data = [
                        budget.get("category", ""),
                        budget.get("amount", 0),
                        budget.get("month_year", "")
                    ]
                    writer.writerow(row_data)
            
            return True
            
        except Exception as e:
            print(f"Lỗi khi lưu tất cả ngân sách: {e}")
            return False
    
    def delete_transaction(self, transaction_to_delete: Dict[str, Any]) -> bool:
        """
        Xóa một giao dịch
        
        Args:
            transaction_to_delete: Giao dịch cần xóa
            
        Returns:
            bool: True nếu thành công, False nếu thất bại
        """
        try:
            transactions = self.load_transactions()
            
            # Tìm và xóa giao dịch
            for i, transaction in enumerate(transactions):
                if (transaction["date"] == transaction_to_delete.get("date") and
                    transaction["type"] == transaction_to_delete.get("type") and
                    transaction["category"] == transaction_to_delete.get("category") and
                    abs(float(transaction["amount"]) - float(transaction_to_delete.get("amount", 0))) < 0.01 and
                    transaction["description"] == transaction_to_delete.get("description", "")):
                    
                    del transactions[i]
                    return self.update_transactions(transactions)
            
            return False  # Không tìm thấy giao dịch
            
        except Exception as e:
            print(f"Lỗi khi xóa giao dịch: {e}")
            return False
    
    def export_data(self, export_path: str) -> bool:
        """
        Xuất dữ liệu ra file
        
        Args:
            export_path: Đường dẫn file xuất
            
        Returns:
            bool: True nếu thành công, False nếu thất bại
        """
        try:
            export_path = Path(export_path)
            
            # Copy file giao dịch
            if self.transactions_file.exists():
                shutil.copy2(self.transactions_file, 
                           export_path.parent / f"exported_transactions_{datetime.now().strftime('%Y%m%d')}.csv")
            
            # Copy file ngân sách
            if self.budget_file.exists():
                shutil.copy2(self.budget_file, 
                           export_path.parent / f"exported_budget_{datetime.now().strftime('%Y%m%d')}.csv")
            
            return True
            
        except Exception as e:
            print(f"Lỗi khi xuất dữ liệu: {e}")
            return False
    
    def get_file_info(self) -> Dict[str, Any]:
        """
        Lấy thông tin về các file dữ liệu
        
        Returns:
            Dict: Thông tin file
        """
        info = {
            "transactions": self._get_single_file_info(self.transactions_file),
            "budget": self._get_single_file_info(self.budget_file)
        }
        return info
    
    def _get_single_file_info(self, file_path: Path) -> Dict[str, Any]:
        """
        Lấy thông tin của một file
        
        Args:
            file_path: Đường dẫn file
            
        Returns:
            Dict: Thông tin file
        """
        if file_path.exists():
            stat = file_path.stat()
            return {
                "exists": True,
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%d/%m/%Y %H:%M:%S"),
                "path": str(file_path)
            }
        else:
            return {
                "exists": False,
                "size": 0,
                "modified": "N/A",
                "path": str(file_path)
            } 