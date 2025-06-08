"""
Ứng dụng Quản lý Chi tiêu Cá nhân
"""

from app_controller import AppController

def main():
    """Hàm main của ứng dụng"""
    try:
        app = AppController()
        app.root.mainloop()
    except Exception as e:
        print(f"Lỗi khởi động ứng dụng: {e}")
        raise

if __name__ == "__main__":
    main() 