# 💰 Quản Lý Chi Tiêu Cá Nhân

Ứng dụng quản lý chi tiêu cá nhân được xây dựng bằng Python, giúp người dùng theo dõi và quản lý chi tiêu một cách hiệu quả.

## ✨ Tính năng

### 1. Quản lý Giao dịch
- 📝 Ghi chép thu chi hàng ngày
- 🔍 Tìm kiếm giao dịch nhanh chóng
- 🗂️ Phân loại theo danh mục
- 📅 Lọc theo thời gian
- 💼 Quản lý nhiều loại chi tiêu

### 2. Phân tích Tài chính
- 📊 Báo cáo chi tiết theo ngày/tháng/năm
- 🎯 Theo dõi và cảnh báo ngân sách
- 📱 Giao diện với CustomTkinter

### 3. Tính năng Nâng cao
- 💡 Thống kê chi tiêu theo danh mục
- 📉 Phân tích xu hướng chi tiêu
- ⚡ Lưu trữ dữ liệu hiệu quả
- 🔒 Bảo mật thông tin người dùng

## 🚀 Cài đặt và Chạy

### Yêu cầu hệ thống
- Python 3.8 trở lên
- Hệ điều hành: Windows, macOS, Linux

### Cài đặt thư viện
```bash
pip install -r requirements.txt
```

### Khởi động ứng dụng
```bash
python main.py
```

## 📁 Cấu trúc Project

```
expense-tracker/
├── core_logic/               # Logic nghiệp vụ chính
│   ├── models.py            # Định nghĩa các model dữ liệu
│   ├── transactions.py      # Quản lý giao dịch
│   ├── transaction_bst.py   # Cây nhị phân tìm kiếm
│   ├── transaction_cache.py # Cache giao dịch
│   ├── budget.py           # Quản lý ngân sách
│   ├── reports.py          # Tạo báo cáo
│   └── analytics.py        # Phân tích dữ liệu
│
├── gui/                    # Giao diện người dùng
│   ├── main_window.py     # Cửa sổ chính
│   ├── transaction_form.py # Form nhập giao dịch
│   ├── reports_window.py  # Cửa sổ báo cáo
│   └── budget_dialog.py   # Dialog ngân sách
│
├── storage/               # Xử lý lưu trữ dữ liệu
├── utils/                # Tiện ích và công cụ
├── data/                 # Dữ liệu 
│
├── main.py              # Điểm khởi chạy ứng dụng
├── app_controller.py    # Controller chính
├── config.py           # Cấu hình ứng dụng
└── requirements.txt    # Thư viện phụ thuộc
```

## 🔧 Công nghệ Sử dụng

### 1. Giao diện người dùng
- CustomTkinter cho UI
- Tkcalendar cho chọn ngày tháng

### 2. Xử lý dữ liệu
- NumPy cho tính toán
- Python-dateutil cho xử lý thời gian

### 3. Lưu trữ
- CSV cho dữ liệu giao dịch
- Pathlib cho quản lý đường dẫn

## 📊 Tính năng Nổi bật

### Giao diện Người dùng
- Theme sáng/tối
- Giao diện thân thiện
- Dễ dàng sử dụng
- Form nhập liệu tiện lợi

### Quản lý Dữ liệu
- Backup dữ liệu
- Kiểm tra dữ liệu
- Xử lý lỗi
- Tìm kiếm nhanh

## 🔒 Bảo mật

### Bảo vệ Dữ liệu
- Kiểm tra tính hợp lệ
- Backup dữ liệu
- Xử lý ngoại lệ an toàn

## 📝 Ghi chú

- Dữ liệu được lưu trong thư mục `data/`
- Cấu hình trong `config.py`

## 👤 Tác giả

**Hồ Xuân Bắc** - *20237301*

# KTLT
