from datetime import datetime
from typing import Dict, Any
from config import CSV_CONFIG

class Transaction:
    """Class đại diện cho một giao dịch"""
    
    def __init__(self, date: str, transaction_type: str, category: str, 
                 amount: float, description: str = "", timestamp: str = None):
        self.date = date
        self.type = transaction_type
        self.category = category
        self.amount = amount
        self.description = description
        self.timestamp = timestamp or datetime.now().strftime(CSV_CONFIG["timestamp_format"])
    
    def to_dict(self) -> Dict[str, Any]:
        """Chuyển đổi transaction thành dictionary"""
        return {
            "timestamp": self.timestamp,
            "date": self.date,
            "type": self.type,
            "category": self.category,
            "amount": self.amount,
            "description": self.description
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Transaction':
        """Tạo Transaction từ dictionary"""
        return cls(
            date=data.get("date", ""),
            transaction_type=data.get("type", ""),
            category=data.get("category", ""),
            amount=data.get("amount", 0.0),
            description=data.get("description", ""),
            timestamp=data.get("timestamp")
        )
    
    def get_month_year(self) -> str:
        """Lấy tháng/năm từ ngày giao dịch (MM/YYYY)"""
        try:
            day, month, year = self.date.split('/')
            return f"{month.zfill(2)}/{year}"
        except (ValueError, IndexError):
            return datetime.now().strftime("%m/%Y")
    
    def get_year(self) -> str:
        """Lấy năm từ ngày giao dịch"""
        try:
            return self.date.split('/')[2]
        except (ValueError, IndexError):
            return str(datetime.now().year) 