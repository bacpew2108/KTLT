#Tạo báo cáo và phân tích dữ liệu

from datetime import datetime, timedelta
from collections import defaultdict
from typing import List, Dict, Any
from config import REPORT_CONFIG


class ReportGenerator:
    """Class tạo các báo cáo tài chính"""
    
    def __init__(self, transactions: List[Any]):
        self.transactions = transactions
        self.currency = REPORT_CONFIG["currency"]
        self.date_format = REPORT_CONFIG["date_format"]
    
    def get_monthly_report(self, month_year: str = None) -> Dict[str, Any]:
        """
        Tạo báo cáo tháng
        
        Args:
            month_year: Tháng/năm (MM/YYYY)
            
        Returns:
            Dict: Báo cáo tháng
        """
        if month_year is None:
            month_year = datetime.now().strftime("%m/%Y")
        
        monthly_transactions = [
            t for t in self.transactions 
            if hasattr(t, 'get_month_year') and t.get_month_year() == month_year
        ]
        
        income = sum(t.amount for t in monthly_transactions if t.type in ["Thu nhập", "income"])
        expense = sum(t.amount for t in monthly_transactions if t.type in ["Chi tiêu", "expense"])
        balance = income - expense
        
        # Phân tích theo danh mục
        income_by_category = defaultdict(float)
        expense_by_category = defaultdict(float)
        
        # Thêm phân tích theo tuần
        weekly_data = defaultdict(lambda: {"income": 0, "expense": 0})
        
        for transaction in monthly_transactions:
            # Phân loại theo danh mục
            if transaction.type in ["Thu nhập", "income"]:
                income_by_category[transaction.category] += transaction.amount
            elif transaction.type in ["Chi tiêu", "expense"]:
                expense_by_category[transaction.category] += transaction.amount
            
            # Phân loại theo tuần
            try:
                date_obj = datetime.strptime(transaction.date, "%d/%m/%Y")
                week_num = date_obj.isocalendar()[1]
                if transaction.type in ["Thu nhập", "income"]:
                    weekly_data[week_num]["income"] += transaction.amount
                elif transaction.type in ["Chi tiêu", "expense"]:
                    weekly_data[week_num]["expense"] += transaction.amount
            except ValueError:
                continue
        
        # Tính toán các chỉ số bổ sung
        avg_transaction = sum(t.amount for t in monthly_transactions) / len(monthly_transactions) if monthly_transactions else 0
        max_single_expense = max((t.amount for t in monthly_transactions if t.type in ["Chi tiêu", "expense"]), default=0)
        max_single_income = max((t.amount for t in monthly_transactions if t.type in ["Thu nhập", "income"]), default=0)
        
        return {
            "month_year": month_year,
            "summary": {
                "income": income,
                "expense": expense,
                "balance": balance,
                "transaction_count": len(monthly_transactions),
                "avg_transaction": avg_transaction,
                "max_single_expense": max_single_expense,
                "max_single_income": max_single_income,
                "savings_rate": (income - expense) / income * 100 if income > 0 else 0
            },
            "income_by_category": dict(income_by_category),
            "expense_by_category": dict(expense_by_category),
            "weekly_data": dict(weekly_data),
            "largest_income": max(monthly_transactions, key=lambda x: x.amount if x.type == "Thu nhập" else 0, default=None),
            "largest_expense": max(monthly_transactions, key=lambda x: x.amount if x.type == "Chi tiêu" else 0, default=None)
        }
    
    def get_yearly_report(self, year: str = None) -> Dict[str, Any]:
        """
        Tạo báo cáo năm
        
        Args:
            year: Năm (YYYY)
            
        Returns:
            Dict: Báo cáo năm
        """
        if year is None:
            year = str(datetime.now().year)
        
        yearly_transactions = [
            t for t in self.transactions 
            if hasattr(t, 'get_year') and t.get_year() == year
        ]
        
        income = sum(t.amount for t in yearly_transactions if t.type in ["Thu nhập", "income"])
        expense = sum(t.amount for t in yearly_transactions if t.type in ["Chi tiêu", "expense"])
        balance = income - expense
        
        # Phân tích theo tháng
        monthly_data = defaultdict(lambda: {'income': 0, 'expense': 0, 'balance': 0, 'transaction_count': 0})
        
        for transaction in yearly_transactions:
            month = transaction.get_month_year()
            monthly_data[month]['transaction_count'] += 1
            if transaction.type in ["Thu nhập", "income"]:
                monthly_data[month]['income'] += transaction.amount
            elif transaction.type in ["Chi tiêu", "expense"]:
                monthly_data[month]['expense'] += transaction.amount
            monthly_data[month]['balance'] = monthly_data[month]['income'] - monthly_data[month]['expense']
        
        # Tính toán xu hướng
        trend_analysis = {
            "income_trend": [],
            "expense_trend": [],
            "balance_trend": []
        }
        
        sorted_months = sorted(monthly_data.keys())
        for i in range(1, len(sorted_months)):
            prev_month = sorted_months[i-1]
            curr_month = sorted_months[i]
            
            income_change = monthly_data[curr_month]['income'] - monthly_data[prev_month]['income']
            expense_change = monthly_data[curr_month]['expense'] - monthly_data[prev_month]['expense']
            balance_change = monthly_data[curr_month]['balance'] - monthly_data[prev_month]['balance']
            
            trend_analysis["income_trend"].append({
                "month": curr_month,
                "change": income_change,
                "percentage": (income_change / monthly_data[prev_month]['income'] * 100) if monthly_data[prev_month]['income'] > 0 else 0
            })
            
            trend_analysis["expense_trend"].append({
                "month": curr_month,
                "change": expense_change,
                "percentage": (expense_change / monthly_data[prev_month]['expense'] * 100) if monthly_data[prev_month]['expense'] > 0 else 0
            })
            
            trend_analysis["balance_trend"].append({
                "month": curr_month,
                "change": balance_change,
                "percentage": (balance_change / abs(monthly_data[prev_month]['balance']) * 100) if monthly_data[prev_month]['balance'] != 0 else 0
            })
        
        return {
            "year": year,
            "summary": {
                "total_income": income,
                "total_expense": expense,
                "total_balance": balance,
                "transaction_count": len(yearly_transactions),
                "avg_monthly_income": income / 12 if income > 0 else 0,
                "avg_monthly_expense": expense / 12 if expense > 0 else 0,
                "avg_monthly_balance": balance / 12,
                "savings_rate": (income - expense) / income * 100 if income > 0 else 0
            },
            "monthly_breakdown": dict(monthly_data),
            "trend_analysis": trend_analysis
        }
    
    def get_category_analysis(self, transaction_type: str = "Chi tiêu") -> List[Dict[str, Any]]:
        """
        Phân tích theo danh mục
        
        Args:
            transaction_type: Loại giao dịch
            
        Returns:
            List[Dict]: Phân tích danh mục
        """
        filtered_transactions = [
            t for t in self.transactions if t.type == transaction_type
        ]
        
        category_data = defaultdict(lambda: {
            'total': 0, 
            'count': 0, 
            'transactions': [],
            'avg_amount': 0,
            'min_amount': float('inf'),
            'max_amount': 0,
            'monthly_totals': defaultdict(float)
        })
        
        for transaction in filtered_transactions:
            category = transaction.category
            amount = transaction.amount
            month_year = transaction.get_month_year()
            
            # Cập nhật thống kê
            category_data[category]['total'] += amount
            category_data[category]['count'] += 1
            category_data[category]['transactions'].append(transaction)
            category_data[category]['min_amount'] = min(category_data[category]['min_amount'], amount)
            category_data[category]['max_amount'] = max(category_data[category]['max_amount'], amount)
            category_data[category]['monthly_totals'][month_year] += amount
        
        total_amount = sum(data['total'] for data in category_data.values())
        
        result = []
        for category, data in category_data.items():
            if data['count'] > 0:
                data['avg_amount'] = data['total'] / data['count']
                if data['min_amount'] == float('inf'):
                    data['min_amount'] = 0
                
                monthly_trend = []
                sorted_months = sorted(data['monthly_totals'].keys())
                for i in range(1, len(sorted_months)):
                    prev_month = sorted_months[i-1]
                    curr_month = sorted_months[i]
                    change = data['monthly_totals'][curr_month] - data['monthly_totals'][prev_month]
                    monthly_trend.append({
                        'month': curr_month,
                        'change': change,
                        'percentage': (change / data['monthly_totals'][prev_month] * 100) 
                        if data['monthly_totals'][prev_month] > 0 else 0
                    })
            
            result.append({
                'category': category,
                'total_amount': data['total'],
                'transaction_count': data['count'],
                'percentage': (data['total'] / total_amount * 100) if total_amount > 0 else 0,
                'avg_amount': data['avg_amount'],
                'min_amount': data['min_amount'],
                'max_amount': data['max_amount'],
                'monthly_totals': dict(data['monthly_totals']),
                'monthly_trend': monthly_trend
            })
        
        # Sắp xếp theo tổng số tiền giảm dần
        result.sort(key=lambda x: x['total_amount'], reverse=True)
        return result
    
    def get_trend_analysis(self, months: int = 12) -> Dict[str, Any]:
        """
        Phân tích xu hướng
        
        Args:
            months: Số tháng phân tích
            
        Returns:
            Dict: Phân tích xu hướng
        """
        current_date = datetime.now()
        months_to_analyze = []
        
        for i in range(months):
            date = current_date - timedelta(days=30 * i)
            months_to_analyze.append(date.strftime("%m/%Y"))
        
        months_to_analyze.reverse()
        
        trend_data = []
        for month_year in months_to_analyze:
            monthly_report = self.get_monthly_report(month_year)["summary"]
            trend_data.append({
                "month": month_year,
                "income": monthly_report['income'],
                "expense": monthly_report['expense'],
                "balance": monthly_report['balance'],
                "transaction_count": monthly_report['transaction_count'],
                "savings_rate": monthly_report.get('savings_rate', 0)
            })
        
        # Tính xu hướng
        trends = {
            "income": self._calculate_trend([d['income'] for d in trend_data]),
            "expense": self._calculate_trend([d['expense'] for d in trend_data]),
            "balance": self._calculate_trend([d['balance'] for d in trend_data]),
            "savings_rate": self._calculate_trend([d['savings_rate'] for d in trend_data])
        }
        
        # Tính tốc độ tăng trưởng
        growth_rates = {
            "income": self._calculate_growth_rate([d['income'] for d in trend_data]),
            "expense": self._calculate_growth_rate([d['expense'] for d in trend_data]),
            "balance": self._calculate_growth_rate([d['balance'] for d in trend_data])
        }
        
        return {
            "monthly_data": trend_data,
            "trends": trends,
            "growth_rates": growth_rates,
            "periods_analyzed": months
        }
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Tính xu hướng dựa trên dữ liệu"""
        if len(values) < 2:
            return "không đủ dữ liệu"
        
        increases = sum(1 for i in range(1, len(values)) if values[i] > values[i-1])
        decreases = sum(1 for i in range(1, len(values)) if values[i] < values[i-1])
        
        if increases > decreases:
            return "tăng"
        elif decreases > increases:
            return "giảm"
        return "ổn định"
    
    def _calculate_growth_rate(self, values: List[float]) -> float:
        """Tính tốc độ tăng trưởng"""
        if len(values) < 2 or values[0] == 0:
            return 0
        return ((values[-1] - values[0]) / abs(values[0])) * 100
    
    def get_financial_health_score(self) -> Dict[str, Any]:
        """
        Tính điểm sức khỏe tài chính
        
        Returns:
            Dict: Điểm sức khỏe tài chính
        """
        current_month = datetime.now().strftime("%m/%Y")
        monthly_report = self.get_monthly_report(current_month)
        monthly_summary = monthly_report["summary"]
        
        score = 100
        recommendations = []
        details = {}
        
        # Đánh giá tỷ lệ thu chi
        if monthly_summary['income'] > 0:
            expense_ratio = monthly_summary['expense'] / monthly_summary['income']
            details['expense_ratio'] = expense_ratio
            
            if expense_ratio > 0.9:
                score -= 30
                recommendations.append({
                    "type": "warning",
                    "message": "Chi tiêu quá cao so với thu nhập (>90%)",
                    "action": "Cần giảm chi tiêu hoặc tăng thu nhập"
                })
            elif expense_ratio > 0.7:
                score -= 15
                recommendations.append({
                    "type": "caution",
                    "message": "Chi tiêu cao so với thu nhập (>70%)",
                    "action": "Nên xem xét cắt giảm một số khoản chi tiêu không cần thiết"
                })
        else:
            score -= 50
            recommendations.append({
                "type": "critical",
                "message": "Không có thu nhập trong tháng",
                "action": "Cần tìm kiếm nguồn thu nhập"
            })
        
        # Đánh giá số dư
        details['balance'] = monthly_summary['balance']
        if monthly_summary['balance'] < 0:
            score -= 25
            recommendations.append({
                "type": "warning",
                "message": "Chi tiêu vượt quá thu nhập",
                "action": "Cần cân đối lại chi tiêu"
            })
        
        # Đánh giá tỷ lệ tiết kiệm
        savings_rate = monthly_summary.get('savings_rate', 0)
        details['savings_rate'] = savings_rate
        if savings_rate < 10:
            score -= 15
            recommendations.append({
                "type": "caution",
                "message": "Tỷ lệ tiết kiệm thấp (<10%)",
                "action": "Nên tăng tỷ lệ tiết kiệm lên ít nhất 10-20% thu nhập"
            })
        
        # Đánh giá tính đều đặn của giao dịch
        transaction_count = monthly_summary['transaction_count']
        details['transaction_count'] = transaction_count
        if transaction_count < 5:
            score -= 10
            recommendations.append({
                "type": "info",
                "message": "Số lượng giao dịch ít",
                "action": "Nên ghi chép đầy đủ các giao dịch để theo dõi tốt hơn"
            })
        
        # Phân loại điểm số
        if score >= 80:
            health_level = "Tốt"
            status_color = "#28a745"  # Xanh lá
        elif score >= 60:
            health_level = "Trung bình"
            status_color = "#ffc107"  # Vàng
        elif score >= 40:
            health_level = "Cần cải thiện"
            status_color = "#fd7e14"  # Cam
        else:
            health_level = "Kém"
            status_color = "#dc3545"  # Đỏ
        
        return {
            "score": max(0, score),
            "level": health_level,
            "status_color": status_color,
            "recommendations": recommendations,
            "month_analyzed": current_month,
            "details": details
        }
    
    def get_comparison_report(self, period1: str, period2: str, period_type: str = "month") -> Dict[str, Any]:
        """
        So sánh giữa hai kỳ
        
        Args:
            period1: Kỳ thứ nhất (MM/YYYY hoặc YYYY)
            period2: Kỳ thứ hai (MM/YYYY hoặc YYYY)
            period_type: Loại kỳ ("month" hoặc "year")
            
        Returns:
            Dict: Báo cáo so sánh
        """
        if period_type == "month":
            report1 = self.get_monthly_report(period1)
            report2 = self.get_monthly_report(period2)
            key_prefix = ""
        else:
            report1 = self.get_yearly_report(period1)
            report2 = self.get_yearly_report(period2)
            key_prefix = "total_"
        
        # Tính thay đổi
        changes = {}
        percentages = {}
        
        for key in ['income', 'expense', 'balance']:
            full_key = f"{key_prefix}{key}"
            val1 = report1["summary"][full_key] if key_prefix else report1["summary"][key]
            val2 = report2["summary"][full_key] if key_prefix else report2["summary"][key]
            
            changes[key] = val2 - val1
            percentages[key] = (changes[key] / abs(val1) * 100) if val1 != 0 else 0
        
        # So sánh theo danh mục
        category_comparison = {
            "income": self._compare_categories(report1["income_by_category"], report2["income_by_category"]),
            "expense": self._compare_categories(report1["expense_by_category"], report2["expense_by_category"])
        }
        
        return {
            "period1": period1,
            "period2": period2,
            "period_type": period_type,
            "changes": changes,
            "percentages": percentages,
            "category_comparison": category_comparison,
            "summary": {
                "period1": report1["summary"],
                "period2": report2["summary"]
            }
        }
    
    def _compare_categories(self, categories1: Dict[str, float], categories2: Dict[str, float]) -> List[Dict[str, Any]]:
        """So sánh chi tiết theo danh mục"""
        all_categories = set(categories1.keys()) | set(categories2.keys())
        comparison = []
        
        for category in all_categories:
            val1 = categories1.get(category, 0)
            val2 = categories2.get(category, 0)
            change = val2 - val1
            
            comparison.append({
                "category": category,
                "value1": val1,
                "value2": val2,
                "change": change,
                "percentage": (change / abs(val1) * 100) if val1 != 0 else 0
            })
        
        return sorted(comparison, key=lambda x: abs(x["change"]), reverse=True)
    
    def export_comprehensive_report(self, format_type: str = "text") -> str:
        """
        Xuất báo cáo tổng hợp
        
        Args:
            format_type: Định dạng ("text" hoặc "html")
            
        Returns:
            str: Báo cáo tổng hợp
        """
        current_month = datetime.now().strftime("%m/%Y")
        current_year = str(datetime.now().year)
        
        monthly_report = self.get_monthly_report(current_month)
        yearly_report = self.get_yearly_report(current_year)
        category_analysis = self.get_category_analysis("Chi tiêu")
        health_score = self.get_financial_health_score()
        trend_analysis = self.get_trend_analysis(6)  # 6 tháng gần nhất
        
        if format_type == "text":
            report = f"""
╔══════════════════════════════════════════════════════════════╗
║                   BÁO CÁO TÀI CHÍNH TỔNG HỢP                 ║
╚══════════════════════════════════════════════════════════════╝

📅 Ngày tạo: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}

💰 TỔNG QUAN THÁNG {current_month}
────────────────────────────────────────────────────────────────
• Thu nhập: {monthly_report['summary']['income']:,.0f} {self.currency}
• Chi tiêu: {monthly_report['summary']['expense']:,.0f} {self.currency}
• Số dư: {monthly_report['summary']['balance']:,.0f} {self.currency}
• Tỷ lệ tiết kiệm: {monthly_report['summary']['savings_rate']:.1f}%
• Số giao dịch: {monthly_report['summary']['transaction_count']}

📈 TỔNG QUAN NĂM {current_year}
────────────────────────────────────────────────────────────────
• Tổng thu nhập: {yearly_report['summary']['total_income']:,.0f} {self.currency}
• Tổng chi tiêu: {yearly_report['summary']['total_expense']:,.0f} {self.currency}
• Số dư năm: {yearly_report['summary']['total_balance']:,.0f} {self.currency}
• Thu nhập TB/tháng: {yearly_report['summary']['avg_monthly_income']:,.0f} {self.currency}
• Chi tiêu TB/tháng: {yearly_report['summary']['avg_monthly_expense']:,.0f} {self.currency}
• Tỷ lệ tiết kiệm năm: {yearly_report['summary']['savings_rate']:.1f}%

📊 PHÂN TÍCH CHI TIÊU THEO DANH MỤC
────────────────────────────────────────────────────────────────"""

            for i, category in enumerate(category_analysis[:5], 1):
                report += f"""
{i}. {category['category']}
   • Tổng chi tiêu: {category['total_amount']:,.0f} {self.currency} ({category['percentage']:.1f}%)
   • Số giao dịch: {category['transaction_count']}
   • TB/giao dịch: {category['avg_amount']:,.0f} {self.currency}"""

            report += f"""

📈 XU HƯỚNG TÀI CHÍNH (6 THÁNG GẦN NHẤT)
────────────────────────────────────────────────────────────────
• Thu nhập: {trend_analysis['trends']['income']}
• Chi tiêu: {trend_analysis['trends']['expense']}
• Số dư: {trend_analysis['trends']['balance']}
• Tỷ lệ tăng trưởng thu nhập: {trend_analysis['growth_rates']['income']:.1f}%
• Tỷ lệ tăng trưởng chi tiêu: {trend_analysis['growth_rates']['expense']:.1f}%

💡 ĐÁNH GIÁ SỨC KHỎE TÀI CHÍNH
────────────────────────────────────────────────────────────────
• Điểm số: {health_score['score']}/100 ({health_score['level']})

🔍 KHUYẾN NGHỊ:"""

            for i, rec in enumerate(health_score['recommendations'], 1):
                report += f"""
{i}. {rec['message']}
   ➤ {rec['action']}"""

            report += f"""

═══════════════════════════════════════════════════════════════
💡 Lưu ý: Báo cáo được tạo tự động dựa trên dữ liệu giao dịch.
          Hãy cập nhật đầy đủ giao dịch để có báo cáo chính xác!
"""

            return report
        
        return "Format không được hỗ trợ" 