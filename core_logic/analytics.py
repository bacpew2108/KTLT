from typing import List, Dict, Any
from datetime import datetime
import numpy as np
from core_logic.transactions import Transaction
from .transaction_cache import cached_method

class TransactionAnalytics:
    """Class phân tích dữ liệu nâng cao"""
    
    def __init__(self, transactions: List[Transaction]):
        self.transactions = transactions
        self._transaction_cache = {}
        
    @cached_method(ttl_seconds=300)
    def analyze_spending_patterns(self) -> Dict[str, Any]:
        """Phân tích mẫu chi tiêu với numpy để tối ưu hiệu suất"""
        if not self.transactions:
            return {}
            
        # Chuyển đổi dữ liệu sang numpy array để tính toán nhanh hơn
        amounts = np.array([t.amount for t in self.transactions])
        dates = np.array([datetime.strptime(t.date, "%d/%m/%Y").timestamp() for t in self.transactions])
        categories = np.array([t.category for t in self.transactions])
        
        # Tính toán thống kê cơ bản
        total = np.sum(amounts)
        mean = np.mean(amounts)
        median = np.median(amounts)
        std_dev = np.std(amounts)
        
        # Phát hiện outliers bằng IQR
        q1, q3 = np.percentile(amounts, [25, 75])
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        outliers = amounts[(amounts < lower_bound) | (amounts > upper_bound)]
        
        # Phân tích xu hướng theo thời gian
        sorted_indices = np.argsort(dates)
        sorted_amounts = amounts[sorted_indices]
        
        # Tính moving average để làm mịn dữ liệu
        window_size = min(5, len(sorted_amounts))
        moving_avg = np.convolve(sorted_amounts, np.ones(window_size)/window_size, mode='valid')
        
        # Phân tích theo danh mục
        unique_categories, category_counts = np.unique(categories, return_counts=True)
        category_totals = {cat: np.sum(amounts[categories == cat]) for cat in unique_categories}
        
        # Tính tỷ lệ tăng trưởng
        if len(sorted_amounts) >= 2:
            growth_rate = (sorted_amounts[-1] - sorted_amounts[0]) / sorted_amounts[0] * 100
        else:
            growth_rate = 0
            
        return {
            'total': float(total),
            'mean': float(mean),
            'median': float(median),
            'std_dev': float(std_dev),
            'outliers': outliers.tolist(),
            'moving_average': moving_avg.tolist(),
            'category_analysis': category_totals,
            'growth_rate': float(growth_rate)
        }
        
    @cached_method(ttl_seconds=300)
    def predict_future_spending(self, days_ahead: int = 30) -> Dict[str, Any]:
        """Dự đoán chi tiêu tương lai sử dụng linear regression"""
        if not self.transactions or days_ahead <= 0:
            return {}
            
        # Chuẩn bị dữ liệu
        dates = np.array([datetime.strptime(t.date, "%d/%m/%Y").timestamp() for t in self.transactions])
        amounts = np.array([t.amount for t in self.transactions])
        
        # Chuẩn hóa dữ liệu thời gian
        min_date = dates.min()
        dates = (dates - min_date) / (24 * 3600)  # Chuyển đổi sang số ngày
        
        # Thêm bias term
        X = np.column_stack([np.ones_like(dates), dates])
        
        # Linear regression với numpy
        try:
            # Giải hệ phương trình tuyến tính
            coefficients = np.linalg.solve(X.T @ X, X.T @ amounts)
            
            # Dự đoán cho ngày tiếp theo
            future_days = np.arange(len(dates), len(dates) + days_ahead)
            future_X = np.column_stack([np.ones_like(future_days), future_days])
            predictions = future_X @ coefficients
            
            # Tính độ tin cậy
            y_pred = X @ coefficients
            mse = np.mean((amounts - y_pred) ** 2)
            rmse = np.sqrt(mse)
            confidence = 1 / (1 + rmse / np.mean(amounts))
            
            return {
                'predictions': predictions.tolist(),
                'confidence': float(confidence),
                'mse': float(mse),
                'trend': float(coefficients[1])  # Hệ số góc cho biết xu hướng
            }
            
        except np.linalg.LinAlgError:
            # Fallback khi không thể thực hiện linear regression
            return {
                'predictions': [float(np.mean(amounts))] * days_ahead,
                'confidence': 0.5,
                'mse': float(np.var(amounts)),
                'trend': 0.0
            }
        
    @cached_method(ttl_seconds=300)
    def detect_anomalies(self) -> List[Dict[str, Any]]:
        """Phát hiện giao dịch bất thường sử dụng Z-score và phân tích theo danh mục"""
        if not self.transactions:
            return []
            
        # Chuyển đổi dữ liệu sang numpy array
        amounts = np.array([t.amount for t in self.transactions])
        categories = np.array([t.category for t in self.transactions])
        
        # Tính Z-score cho mỗi giao dịch
        mean = np.mean(amounts)
        std = np.std(amounts)
        z_scores = (amounts - mean) / std if std > 0 else np.zeros_like(amounts)
        
        # Phân tích theo danh mục
        anomalies = []
        for category in np.unique(categories):
            cat_mask = categories == category
            cat_amounts = amounts[cat_mask]
            
            if len(cat_amounts) >= 2:
                cat_mean = np.mean(cat_amounts)
                cat_std = np.std(cat_amounts)
                cat_z_scores = (cat_amounts - cat_mean) / cat_std if cat_std > 0 else np.zeros_like(cat_amounts)
                
                # Phát hiện anomaly dựa trên Z-score
                for i, (t, z) in enumerate(zip(np.array(self.transactions)[cat_mask], cat_z_scores)):
                    if abs(z) > 2:  # Ngưỡng Z-score = 2 (95% confidence)
                        anomalies.append({
                            'transaction': t.to_dict(),
                            'z_score': float(z),
                            'category_mean': float(cat_mean),
                            'category_std': float(cat_std),
                            'deviation_percent': float((t.amount - cat_mean) / cat_mean * 100)
                        })
        
        return sorted(anomalies, key=lambda x: abs(x['z_score']), reverse=True)
        
    @cached_method(ttl_seconds=300)
    def analyze_category_correlations(self) -> Dict[str, Any]:
        """Phân tích mối tương quan giữa các danh mục chi tiêu"""
        if not self.transactions:
            return {}
            
        # Tạo ma trận tương quan giữa các danh mục
        categories = list(set(t.category for t in self.transactions))
        n_categories = len(categories)
        cat_to_idx = {cat: i for i, cat in enumerate(categories)}
        
        # Tạo ma trận số tiền theo danh mục và thời gian
        dates = sorted(set(t.date for t in self.transactions))
        amount_matrix = np.zeros((len(dates), n_categories))
        
        for t in self.transactions:
            date_idx = dates.index(t.date)
            cat_idx = cat_to_idx[t.category]
            amount_matrix[date_idx, cat_idx] += t.amount
        
        # Tính ma trận tương quan
        correlation_matrix = np.corrcoef(amount_matrix.T)
        
        # Tìm các cặp danh mục có tương quan mạnh
        strong_correlations = []
        for i in range(n_categories):
            for j in range(i + 1, n_categories):
                corr = correlation_matrix[i, j]
                if abs(corr) > 0.5:  # Ngưỡng tương quan 0.5
                    strong_correlations.append({
                        'category1': categories[i],
                        'category2': categories[j],
                        'correlation': float(corr)
                    })
        
        return {
            'correlation_matrix': correlation_matrix.tolist(),
            'categories': categories,
            'strong_correlations': strong_correlations
        }
        
    def get_insights(self) -> List[Dict[str, Any]]:
        """Tổng hợp các insights từ phân tích"""
        insights = []
        
        # Phân tích mẫu chi tiêu
        patterns = self.analyze_spending_patterns()
        if patterns:
            if patterns.get('outliers'):
                insights.append({
                    'type': 'warning',
                    'message': f'Phát hiện {len(patterns["outliers"])} giao dịch bất thường',
                    'data': patterns['outliers']
                })
            
            growth_rate = patterns.get('growth_rate', 0)
            if abs(growth_rate) > 20:  # Tăng/giảm hơn 20%
                insights.append({
                    'type': 'info',
                    'message': f'Chi tiêu {"tăng" if growth_rate > 0 else "giảm"} {abs(growth_rate):.1f}%',
                    'data': {'growth_rate': growth_rate}
                })
        
        # Dự đoán tương lai
        predictions = self.predict_future_spending()
        if predictions and predictions.get('confidence', 0) > 0.7:
            trend = predictions.get('trend', 0)
            if abs(trend) > 0:
                insights.append({
                    'type': 'info',
                    'message': f'Dự đoán chi tiêu sẽ {"tăng" if trend > 0 else "giảm"} trong tương lai',
                    'data': predictions
                })
        
        # Phát hiện bất thường
        anomalies = self.detect_anomalies()
        if anomalies:
            insights.append({
                'type': 'warning',
                'message': f'Phát hiện {len(anomalies)} giao dịch có giá trị bất thường',
                'data': anomalies
            })
        
        # Phân tích tương quan
        correlations = self.analyze_category_correlations()
        strong_corrs = correlations.get('strong_correlations', [])
        if strong_corrs:
            insights.append({
                'type': 'info',
                'message': f'Phát hiện {len(strong_corrs)} cặp danh mục có tương quan mạnh',
                'data': strong_corrs
            })
        
        return insights 