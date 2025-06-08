from typing import Optional, List, Any
from datetime import datetime
from core_logic.models import Transaction
from functools import lru_cache

class Node:
    """Node trong BST"""
    def __init__(self, transaction: Any):
        self.transaction = transaction
        self.left = None
        self.right = None
        self.height = 1  # Cho cân bằng AVL
        self.size = 1    # Số node trong cây con

class TransactionBST:
    """Binary Search Tree cho giao dịch với cân bằng tự động"""
    
    def __init__(self):
        self.root = None
        self._clear_cache()
    
    def _clear_cache(self):
        """Xóa cache khi cây thay đổi"""
        self.get_transactions_by_date_range.cache_clear()
        self.get_height.cache_clear()
    
    def _get_height(self, node: Optional[Node]) -> int:
        """Lấy chiều cao của node"""
        if not node:
            return 0
        return node.height
    
    def _get_balance(self, node: Optional[Node]) -> int:
        """Lấy hệ số cân bằng của node"""
        if not node:
            return 0
        return self._get_height(node.left) - self._get_height(node.right)
    
    def _update_height_and_size(self, node: Node) -> None:
        """Cập nhật chiều cao và kích thước của node"""
        if not node:
            return
        node.height = max(self._get_height(node.left), self._get_height(node.right)) + 1
        node.size = (node.left.size if node.left else 0) + (node.right.size if node.right else 0) + 1
    
    def _right_rotate(self, y: Node) -> Node:
        """Xoay phải để cân bằng"""
        if not y or not y.left:
            return y
            
        x = y.left
        T2 = x.right
        
        x.right = y
        y.left = T2
        
        self._update_height_and_size(y)
        self._update_height_and_size(x)
        
        return x
    
    def _left_rotate(self, x: Node) -> Node:
        """Xoay trái để cân bằng"""
        if not x or not x.right:
            return x
            
        y = x.right
        T2 = y.left
        
        y.left = x
        x.right = T2
        
        self._update_height_and_size(x)
        self._update_height_and_size(y)
        
        return y
    
    def insert(self, transaction: Any) -> None:
        """Thêm giao dịch vào BST với cân bằng tự động"""
        try:
            self.root = self._insert_recursive(self.root, transaction)
        except Exception as e:
            print(f"Lỗi khi thêm giao dịch vào BST: {e}")
    
    def _insert_recursive(self, node: Optional[Node], transaction: Any) -> Node:
        """Đệ quy thêm node và cân bằng cây"""
        # Thêm node mới
        if not node:
            return Node(transaction)
        
        # Chèn vào cây con phù hợp
        if transaction.date < node.transaction.date:
            node.left = self._insert_recursive(node.left, transaction)
        else:
            node.right = self._insert_recursive(node.right, transaction)
        
        # Cập nhật chiều cao và kích thước
        self._update_height_and_size(node)
        
        # Lấy hệ số cân bằng
        balance = self._get_balance(node)
        
        # Cân bằng cây nếu cần
        # Trường hợp Left Left
        if balance > 1 and transaction.date < node.left.transaction.date:
            return self._right_rotate(node)
        
        # Trường hợp Right Right
        if balance < -1 and transaction.date > node.right.transaction.date:
            return self._left_rotate(node)
        
        # Trường hợp Left Right
        if balance > 1 and transaction.date > node.left.transaction.date:
            node.left = self._left_rotate(node.left)
            return self._right_rotate(node)
        
        # Trường hợp Right Left
        if balance < -1 and transaction.date < node.right.transaction.date:
            node.right = self._right_rotate(node.right)
            return self._left_rotate(node)
        
        return node
    
    @lru_cache(maxsize=128)
    def get_transactions_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Any]:
        """Lấy giao dịch trong khoảng thời gian với cache"""
        result = []
        self._get_transactions_in_range(self.root, start_date, end_date, result)
        return result
    
    def _get_transactions_in_range(self, node: Optional[Node], start_date: datetime, 
                                 end_date: datetime, result: List[Any]) -> None:
        """Đệ quy lấy giao dịch trong khoảng thời gian"""
        if not node:
            return
            
        if node.transaction.date >= start_date:
            self._get_transactions_in_range(node.left, start_date, end_date, result)
            
        if start_date <= node.transaction.date <= end_date:
            result.append(node.transaction)
            
        if node.transaction.date <= end_date:
            self._get_transactions_in_range(node.right, start_date, end_date, result)
    
    @lru_cache(maxsize=1)
    def get_height(self) -> int:
        """Lấy chiều cao của cây với cache"""
        return self._get_height(self.root)
    
    def get_size(self) -> int:
        """Lấy số lượng node trong cây"""
        return self.root.size if self.root else 0

    def find_range(self, start_date: str, end_date: str) -> List[Transaction]:
        """Tìm giao dịch trong khoảng thời gian - O(log n)"""
        result = []
        try:
            start_dt = datetime.strptime(start_date, "%d/%m/%Y")
            end_dt = datetime.strptime(end_date, "%d/%m/%Y")
            self._find_range_recursive(self.root, start_dt, end_dt, result)
        except Exception as e:
            print(f"Lỗi khi tìm giao dịch trong khoảng: {e}")
        return result

    def _find_range_recursive(self, node: Optional[Node], 
                            start_dt: datetime, end_dt: datetime, 
                            result: List[Transaction]) -> None:
        """Đệ quy tìm giao dịch trong khoảng"""
        if not node:
            return
            
        try:
            current_dt = datetime.strptime(node.transaction.date, "%d/%m/%Y")
            
            if current_dt >= start_dt:
                self._find_range_recursive(node.left, start_dt, end_dt, result)
                
            if start_dt <= current_dt <= end_dt:
                result.append(node.transaction)
                
            if current_dt <= end_dt:
                self._find_range_recursive(node.right, start_dt, end_dt, result)
                
        except Exception as e:
            print(f"Lỗi khi xử lý node trong khoảng: {e}")

    def to_list(self) -> List[Transaction]:
        """Chuyển BST thành list - inorder traversal"""
        result = []
        self._inorder_traversal(self.root, result)
        return result

    def _inorder_traversal(self, node: Optional[Node], 
                          result: List[Transaction]) -> None:
        """Duyệt inorder"""
        if node:
            self._inorder_traversal(node.left, result)
            result.append(node.transaction)
            self._inorder_traversal(node.right, result) 