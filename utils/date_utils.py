#Các hàm tiện ích xử lý ngày tháng

from typing import List


def generate_month_range(start_year: int = 2025, end_year: int = 2027) -> List[str]:
    """
    Tạo danh sách các tháng từ đầu năm start_year đến cuối năm end_year
    
    Args:
        start_year: Năm bắt đầu (mặc định: 2025)
        end_year: Năm kết thúc (mặc định: 2027)
        
    Returns:
        List[str]: Danh sách các tháng theo định dạng MM/YYYY
    """
    months = []
    for year in range(start_year, end_year + 1):
        for month in range(1, 13):
            months.append(f"{month:02d}/{year}")
    return months 