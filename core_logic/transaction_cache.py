from collections import OrderedDict
from typing import Any, Optional, Dict
from datetime import datetime, timedelta
import time
from functools import lru_cache

class LRUCache:
    """LRU Cache cho kết quả tính toán phổ biến"""
    
    def __init__(self, capacity: int = 100):
        self.cache = OrderedDict()
        self.capacity = capacity
        self.expiry_times = {}
        self.default_ttl = timedelta(minutes=5)  # Time To Live mặc định

    def get(self, key: str) -> Optional[Any]:
        """Lấy giá trị từ cache"""
        if key not in self.cache:
            return None
            
        # Kiểm tra hết hạn
        if datetime.now() > self.expiry_times[key]:
            self.cache.pop(key)
            self.expiry_times.pop(key)
            return None
            
        # Di chuyển item lên đầu cache
        self.cache.move_to_end(key)
        return self.cache[key]

    def put(self, key: str, value: Any, ttl: Optional[timedelta] = None) -> None:
        """Thêm giá trị vào cache"""
        if key in self.cache:
            self.cache.pop(key)
            
        # Xóa item cũ nhất nếu cache đầy
        if len(self.cache) >= self.capacity:
            oldest_key, _ = self.cache.popitem(last=False)
            self.expiry_times.pop(oldest_key)
            
        self.cache[key] = value
        self.cache.move_to_end(key)
        
        # Cập nhật thời gian hết hạn
        expiry = datetime.now() + (ttl if ttl else self.default_ttl)
        self.expiry_times[key] = expiry

    def clear_expired(self) -> None:
        """Xóa các item hết hạn"""
        now = datetime.now()
        expired_keys = [
            key for key, expiry in self.expiry_times.items() 
            if now > expiry
        ]
        for key in expired_keys:
            self.cache.pop(key)
            self.expiry_times.pop(key)

class TransactionCache:
    """Cache cho các tính toán liên quan đến giao dịch"""
    
    def __init__(self, ttl_seconds: int = 300, max_size: int = 1000):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._timestamps: Dict[str, float] = {}
        self._ttl_seconds = ttl_seconds
        self._max_size = max_size
        self.monthly_summary_cache = LRUCache(capacity=12)  # Cache cho 12 tháng
        self.category_analysis_cache = LRUCache(capacity=10)  # Cache cho 10 danh mục
        
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Lấy giá trị từ cache với kiểm tra TTL"""
        if key in self._cache:
            if time.time() - self._timestamps[key] > self._ttl_seconds:
                # TTL hết hạn
                self._remove(key)
                return None
            return self._cache[key]
        return None
    
    def set(self, key: str, value: Dict[str, Any]) -> None:
        """Thêm giá trị vào cache với quản lý kích thước"""
        if len(self._cache) >= self._max_size:
            # Xóa entry cũ nhất
            oldest_key = min(self._timestamps.items(), key=lambda x: x[1])[0]
            self._remove(oldest_key)
        
        self._cache[key] = value
        self._timestamps[key] = time.time()
    
    def _remove(self, key: str) -> None:
        """Xóa một entry khỏi cache"""
        self._cache.pop(key, None)
        self._timestamps.pop(key, None)
    
    def clear(self) -> None:
        """Xóa toàn bộ cache"""
        self._cache.clear()
        self._timestamps.clear()
    
    @property
    def size(self) -> int:
        """Lấy kích thước hiện tại của cache"""
        return len(self._cache)
    
    def cleanup_expired(self) -> None:
        """Dọn dẹp các entry hết hạn"""
        current_time = time.time()
        expired_keys = [
            key for key, timestamp in self._timestamps.items()
            if current_time - timestamp > self._ttl_seconds
        ]
        for key in expired_keys:
            self._remove(key)

    def get_monthly_summary(self, month_year: str) -> Optional[dict]:
        """Lấy tóm tắt tháng từ cache"""
        return self.monthly_summary_cache.get(month_year)
        
    def cache_monthly_summary(self, month_year: str, summary: dict) -> None:
        """Lưu tóm tắt tháng vào cache"""
        self.monthly_summary_cache.put(
            month_year, 
            summary,
            ttl=timedelta(minutes=30)  # Cache trong 30 phút
        )
        
    def get_category_analysis(self, category: str) -> Optional[dict]:
        """Lấy phân tích danh mục từ cache"""
        return self.category_analysis_cache.get(category)
        
    def cache_category_analysis(self, category: str, analysis: dict) -> None:
        """Lưu phân tích danh mục vào cache"""
        self.category_analysis_cache.put(
            category,
            analysis,
            ttl=timedelta(minutes=15)  # Cache trong 15 phút
        )

# Decorator cho phương thức với cache
def cached_method(ttl_seconds: int = 300):
    """Decorator để cache kết quả của method với TTL"""
    def decorator(func):
        cache = {}
        timestamps = {}
        
        def wrapper(*args, **kwargs):
            key = str((args, frozenset(kwargs.items())))
            current_time = time.time()
            
            if key in cache:
                if current_time - timestamps[key] <= ttl_seconds:
                    return cache[key]
                else:
                    # TTL hết hạn
                    del cache[key]
                    del timestamps[key]
            
            result = func(*args, **kwargs)
            cache[key] = result
            timestamps[key] = current_time
            return result
            
        return wrapper
    return decorator 