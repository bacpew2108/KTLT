#Các hàm kiểm tra dữ liệu đầu vào

import re
from datetime import datetime, timedelta
from typing import Union
from config import DEFAULT_CATEGORIES, VALIDATION_CONFIG


def validate_date(date_str: str) -> tuple[bool, str]:
    """
    Kiểm tra tính hợp lệ của ngày tháng
    
    Args:
        date_str: Chuỗi ngày tháng theo format DD/MM/YYYY
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not date_str or not isinstance(date_str, str):
        return False, "Ngày không được để trống"
    
    # Kiểm tra format
    date_pattern = r'^\d{2}/\d{2}/\d{4}$'
    if not re.match(date_pattern, date_str):
        return False, "Định dạng ngày phải là DD/MM/YYYY"
    
    try:
        # Kiểm tra tính hợp lệ của ngày
        date_obj = datetime.strptime(date_str, "%d/%m/%Y")
        
        # Kiểm tra ngày không quá xa trong quá khứ hoặc tương lai
        current_date = datetime.now()
        min_date = current_date - timedelta(days=365 * VALIDATION_CONFIG["date_range_years"])
        max_date = current_date + timedelta(days=365)
        
        if date_obj < min_date:
            return False, f"Ngày không được quá {VALIDATION_CONFIG['date_range_years']} năm trong quá khứ"
        
        if date_obj > max_date:
            return False, "Ngày không được quá 1 năm trong tương lai"
        
        return True, ""
        
    except ValueError:
        return False, "Ngày tháng không hợp lệ"


def validate_amount(amount: Union[str, float, int]) -> tuple[bool, str]:
    """
    Kiểm tra tính hợp lệ của số tiền
    
    Args:
        amount: Số tiền cần kiểm tra
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if amount is None or amount == "":
        return False, "Số tiền không được để trống"
    
    try:
        # Chuyển đổi sang float
        if isinstance(amount, str):
            # Loại bỏ dấu phẩy nếu có
            amount = amount.replace(",", "").replace(" ", "")
            amount_float = float(amount)
        else:
            amount_float = float(amount)
        
        # Kiểm tra số âm
        if amount_float <= 0:
            return False, "Số tiền phải lớn hơn 0"
        
        # Kiểm tra giới hạn tối thiểu
        if amount_float < VALIDATION_CONFIG["min_amount"]:
            return False, f"Số tiền phải >= {VALIDATION_CONFIG['min_amount']:,.2f} VNĐ"
        
        # Kiểm tra giới hạn tối đa
        if amount_float > VALIDATION_CONFIG["max_amount"]:
            return False, f"Số tiền không được vượt quá {VALIDATION_CONFIG['max_amount']:,.0f} VNĐ"
        
        return True, ""
        
    except ValueError:
        return False, "Số tiền không hợp lệ"


def validate_category(category: str, transaction_type: str) -> tuple[bool, str]:
    """
    Kiểm tra tính hợp lệ của danh mục
    
    Args:
        category: Danh mục cần kiểm tra
        transaction_type: Loại giao dịch ("Thu nhập" hoặc "Chi tiêu")
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not category or not isinstance(category, str):
        return False, "Danh mục không được để trống"
    
    category = category.strip()
    if not category:
        return False, "Danh mục không được để trống"
    
    # Kiểm tra loại giao dịch
    if transaction_type not in ["Thu nhập", "Chi tiêu"]:
        return False, "Loại giao dịch không hợp lệ"
    
    # Kiểm tra danh mục có trong danh sách cho phép
    valid_categories = (DEFAULT_CATEGORIES["income"] if transaction_type == "Thu nhập" 
                       else DEFAULT_CATEGORIES["expense"])
    
    if category not in valid_categories:
        return False, f"Danh mục '{category}' không hợp lệ cho {transaction_type.lower()}"
    
    return True, ""


def validate_description(description: str) -> tuple[bool, str]:
    """
    Kiểm tra tính hợp lệ của mô tả
    
    Args:
        description: Mô tả giao dịch
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if description is None:
        description = ""
    
    if not isinstance(description, str):
        return False, "Mô tả phải là chuỗi ký tự"
    
    description = description.strip()
    
    # Kiểm tra độ dài
    if len(description) > VALIDATION_CONFIG["max_description_length"]:
        return False, f"Mô tả không được quá {VALIDATION_CONFIG['max_description_length']} ký tự"
    
    return True, ""


def validate_transaction_type(transaction_type: str) -> tuple[bool, str]:
    """
    Kiểm tra tính hợp lệ của loại giao dịch
    
    Args:
        transaction_type: Loại giao dịch
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not transaction_type or not isinstance(transaction_type, str):
        return False, "Loại giao dịch không được để trống"
    
    valid_types = ["Thu nhập", "Chi tiêu"]
    if transaction_type not in valid_types:
        return False, f"Loại giao dịch phải là một trong: {', '.join(valid_types)}"
    
    return True, ""


def validate_budget_amount(amount: Union[str, float, int]) -> tuple[bool, str]:
    """
    Kiểm tra tính hợp lệ của số tiền ngân sách
    
    Args:
        amount: Số tiền ngân sách
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if amount is None or amount == "":
        return False, "Ngân sách không được để trống"
    
    # Sử dụng validate_amount nhưng với thông báo khác
    is_valid, error_msg = validate_amount(amount)
    if not is_valid:
        return False, error_msg.replace("Số tiền", "Ngân sách")
    
    return True, ""


def validate_month_year(month_year: str) -> tuple[bool, str]:
    """
    Kiểm tra tính hợp lệ của tháng/năm
    
    Args:
        month_year: Chuỗi tháng/năm theo format MM/YYYY
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not month_year or not isinstance(month_year, str):
        return False, "Tháng/năm không được để trống"
    
    # Kiểm tra format
    month_year_pattern = r'^\d{2}/\d{4}$'
    if not re.match(month_year_pattern, month_year):
        return False, "Định dạng tháng/năm phải là MM/YYYY"
    
    try:
        month, year = month_year.split('/')
        month = int(month)
        year = int(year)
        
        # Kiểm tra tháng hợp lệ
        if month < 1 or month > 12:
            return False, "Tháng phải từ 01 đến 12"
        
        # Kiểm tra năm hợp lệ
        current_year = datetime.now().year
        if year < current_year - 10 or year > current_year + 1:
            return False, "Năm phải trong khoảng hợp lệ"
        
        return True, ""
        
    except ValueError:
        return False, "Tháng/năm không hợp lệ"


def sanitize_input(input_str: str) -> str:
    """
    Làm sạch dữ liệu đầu vào
    
    Args:
        input_str: Chuỗi cần làm sạch
        
    Returns:
        str: Chuỗi đã được làm sạch
    """
    if not isinstance(input_str, str):
        return str(input_str)
    
    # Loại bỏ khoảng trắng thừa
    cleaned = input_str.strip()
    
    # Loại bỏ các ký tự đặc biệt nguy hiểm
    cleaned = re.sub(r'[<>"\']', '', cleaned)
    
    return cleaned 