import unittest
import sys
import os
from datetime import datetime
from decimal import Decimal
from tkinter import messagebox
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app_controller import AppController
from core_logic.transactions import Transaction

class TestAppController(unittest.TestCase):
    def setUp(self):
        """
        Thiết lập môi trường test trước mỗi test case
        """
        self.app = AppController()
        # Xóa tất cả dữ liệu test cũ
        self.app.transaction_manager.transactions = []
        self.app.budget_manager.budgets = {}
        
        # Mock hộp thoại xác nhận để luôn trả về True
        self.original_askyesno = messagebox.askyesno
        messagebox.askyesno = lambda *args, **kwargs: True
        
    def tearDown(self):
        """
        Dọn dẹp sau mỗi test case
        """
        # Khôi phục hàm gốc
        messagebox.askyesno = self.original_askyesno
        
        # Đóng cửa sổ tkinter
        if hasattr(self, 'app') and hasattr(self.app, 'root'):
            self.app.root.destroy()

    def test_validate_transaction_data_valid(self):
        """
        Test validate dữ liệu giao dịch hợp lệ
        """
        valid_data = {
            "date": "01/01/2024",
            "type": "Chi tiêu",
            "category": "Ăn uống",
            "amount": 100000,
            "description": "Test transaction"
        }
        self.assertTrue(self.app._validate_transaction_data(valid_data))

    def test_validate_transaction_data_invalid(self):
        """
        Test validate dữ liệu giao dịch không hợp lệ
        """
        # Thiếu trường bắt buộc
        invalid_data1 = {
            "date": "01/01/2024",
            "type": "Chi tiêu",
            "amount": 100000
        }
        success, message = self.app._validate_transaction_data(invalid_data1)
        self.assertFalse(success)
        self.assertIn("thiếu thông tin", message.lower())

        # Số tiền không hợp lệ
        invalid_data2 = {
            "date": "01/01/2024",
            "type": "Chi tiêu",
            "category": "Ăn uống",
            "amount": -100,
            "description": "Test transaction"
        }
        success, message = self.app._validate_transaction_data(invalid_data2)
        self.assertFalse(success)
        self.assertIn("số tiền", message.lower())

        # Ngày không hợp lệ
        invalid_data3 = {
            "date": "32/13/2024",
            "type": "Chi tiêu",
            "category": "Ăn uống",
            "amount": 100000,
            "description": "Test transaction"
        }
        success, message = self.app._validate_transaction_data(invalid_data3)
        self.assertFalse(success)
        self.assertIn("định dạng ngày", message.lower())

    def test_add_transaction(self):
        """
        Test thêm giao dịch
        """
        transaction_data = {
            "date": "01/01/2024",
            "type": "Chi tiêu",
            "category": "Ăn uống",
            "amount": 100000,
            "description": "Test transaction"
        }
        success, message = self.app.add_transaction(transaction_data)
        self.assertTrue(success)
        
        # Kiểm tra giao dịch đã được thêm vào
        transactions = self.app.get_all_transactions()
        self.assertEqual(len(transactions), 1)
        latest_transaction = transactions[0]
        self.assertEqual(latest_transaction.amount, 100000)
        self.assertEqual(latest_transaction.category, "Ăn uống")

    def test_delete_transaction(self):
        """
        Test xóa giao dịch
        """
        # Thêm giao dịch mới
        transaction_data = {
            "date": "01/01/2024",
            "type": "Chi tiêu",
            "category": "Ăn uống",
            "amount": 100000,
            "description": "Test transaction"
        }
        self.app.add_transaction(transaction_data)
        
        # Lấy giao dịch vừa thêm
        transactions = self.app.get_all_transactions()
        self.assertEqual(len(transactions), 1)
        transaction_to_delete = transactions[0]
        
        # Test xóa giao dịch
        success = self.app.delete_transaction(vars(transaction_to_delete))
        self.assertTrue(success)
        
        # Kiểm tra giao dịch đã bị xóa
        updated_transactions = self.app.get_all_transactions()
        self.assertEqual(len(updated_transactions), 0)

    def test_set_budget(self):
        """
        Test đặt ngân sách
        """
        category = "Ăn uống"
        amount = 1000000
        month_year = "01/2024"
        
        success = self.app.set_budget(category, amount, month_year)
        self.assertTrue(success)
        
        # Kiểm tra ngân sách đã được đặt
        budget_status = self.app.get_budget_status(category, month_year)
        self.assertEqual(budget_status["budget"], amount)

    def test_get_budget_status(self):
        """
        Test lấy trạng thái ngân sách
        """
        # Đặt ngân sách
        category = "Ăn uống"
        amount = 1000000
        month_year = "01/2024"
        self.app.set_budget(category, amount, month_year)
        
        # Thêm giao dịch
        transaction_data = {
            "date": "01/01/2024",
            "type": "Chi tiêu",
            "category": category,
            "amount": 300000,
            "description": "Test transaction"
        }
        self.app.add_transaction(transaction_data)
        
        # Kiểm tra trạng thái ngân sách
        budget_status = self.app.get_budget_status(category, month_year)
        self.assertEqual(budget_status["budget"], amount)
        self.assertEqual(budget_status["spent"], 300000)
        self.assertEqual(budget_status["remaining"], amount - 300000)

    def test_generate_report(self):
        """
        Test tạo báo cáo
        """
        # Thêm một số giao dịch để test
        transactions = [
            {
                "date": "01/01/2024",
                "type": "Chi tiêu",
                "category": "Ăn uống",
                "amount": 100000,
                "description": "Test 1"
            },
            {
                "date": "02/01/2024",
                "type": "Thu nhập",
                "category": "Lương",
                "amount": 1000000,
                "description": "Test 2"
            }
        ]
        
        # Thêm và kiểm tra từng giao dịch
        for transaction in transactions:
            success, message = self.app.add_transaction(transaction)
            self.assertTrue(success, f"Không thể thêm giao dịch: {message}")
        
        # Kiểm tra các giao dịch đã được thêm đúng
        all_transactions = self.app.get_all_transactions()
        self.assertEqual(len(all_transactions), 2)
        
        # Kiểm tra từng giao dịch
        expense_transaction = next(t for t in all_transactions if t.type == "Chi tiêu")
        income_transaction = next(t for t in all_transactions if t.type == "Thu nhập")
        
        self.assertEqual(expense_transaction.amount, 100000)
        self.assertEqual(income_transaction.amount, 1000000)
        
        # Test báo cáo theo tháng
        report = self.app.generate_report("monthly", month_year="01/2024")
        
        # Kiểm tra cấu trúc báo cáo
        self.assertIn("summary", report)
        self.assertEqual(report["summary"]["income"], 1000000)
        self.assertEqual(report["summary"]["expense"], 100000)
        self.assertEqual(report["summary"]["balance"], 900000)

    def test_add_transaction_invalid_data(self):
        """
        Test thêm giao dịch với dữ liệu không hợp lệ
        """
        # Test với dữ liệu None
        success, message = self.app.add_transaction(None)
        self.assertFalse(success)
        self.assertIn("lỗi validate", message.lower())

        # Test với dữ liệu rỗng
        success, message = self.app.add_transaction({})
        self.assertFalse(success)
        self.assertIn("thiếu thông tin", message.lower())

        # Test với số tiền là chuỗi
        invalid_data = {
            "date": "01/01/2024",
            "type": "Chi tiêu",
            "category": "Ăn uống",
            "amount": "không phải số",
            "description": "Test transaction"
        }
        success, message = self.app.add_transaction(invalid_data)
        self.assertFalse(success)
        self.assertIn("số tiền", message.lower())

    def test_delete_transaction_invalid_data(self):
        """
        Test xóa giao dịch với dữ liệu không hợp lệ
        """
        # Test xóa với dữ liệu None
        success = self.app.delete_transaction(None)
        self.assertFalse(success)

        # Test xóa với dữ liệu không tồn tại
        non_existent_data = {
            "date": "01/01/2024",
            "type": "Chi tiêu",
            "category": "Ăn uống",
            "amount": 100000,
            "description": "Non-existent transaction"
        }
        success = self.app.delete_transaction(non_existent_data)
        self.assertFalse(success)

    def test_set_budget_invalid_data(self):
        """
        Test đặt ngân sách với dữ liệu không hợp lệ
        """
        # Test với số tiền âm
        success = self.app.set_budget("Ăn uống", -1000, "01/2024")
        self.assertFalse(success)

        # Test với danh mục không hợp lệ
        success = self.app.set_budget("", 1000000, "01/2024")
        self.assertFalse(success)

        # Test với định dạng tháng không hợp lệ
        success = self.app.set_budget("Ăn uống", 1000000, "13/2024")
        self.assertFalse(success)

    def test_get_budget_status_invalid_data(self):
        """
        Test lấy trạng thái ngân sách với dữ liệu không hợp lệ
        """
        # Test với danh mục không tồn tại
        status = self.app.get_budget_status("Danh mục không tồn tại", "01/2024")
        self.assertEqual(status["budget"], 0)
        self.assertEqual(status["spent"], 0)

        # Test với định dạng tháng không hợp lệ
        status = self.app.get_budget_status("Ăn uống", "invalid_month")
        self.assertEqual(status["budget"], 0)
        self.assertEqual(status["spent"], 0)

    def test_generate_report_invalid_data(self):
        """
        Test tạo báo cáo với dữ liệu không hợp lệ
        """
        # Test với loại báo cáo không hợp lệ
        report = self.app.generate_report("invalid_type")
        self.assertIn("error", report)  # Kiểm tra có thông báo lỗi

        # Test với tháng không hợp lệ
        report = self.app.generate_report("monthly", month_year="13/2024")
        self.assertEqual(report["summary"]["income"], 0)
        self.assertEqual(report["summary"]["expense"], 0)

        # Test với năm không hợp lệ
        report = self.app.generate_report("yearly", year="invalid_year")
        self.assertEqual(report["summary"]["total_income"], 0)
        self.assertEqual(report["summary"]["total_expense"], 0)
        self.assertEqual(report["summary"]["total_balance"], 0)

    def test_file_operations_exceptions(self):
        """
        Test các trường hợp ngoại lệ khi thao tác với file
        """
        # Test với file không tồn tại
        original_file = self.app.transaction_manager.file_handler.transactions_file
        self.app.transaction_manager.file_handler.transactions_file = Path("non_existent_dir/non_existent_file.csv")
        transaction_data = {
            "date": "01/01/2024",
            "type": "Chi tiêu",
            "category": "Ăn uống",
            "amount": 100000,
            "description": "Test transaction"
        }
        success, message = self.app.add_transaction(transaction_data)
        self.assertFalse(success)
        self.assertIn("không thể lưu", message.lower())

        # Khôi phục file gốc
        self.app.transaction_manager.file_handler.transactions_file = original_file

        # Test với file không có quyền ghi
        # TODO: Implement this test on Unix systems

    def test_transaction_validation_edge_cases(self):
        """
        Test các trường hợp ngoại lệ khi validate giao dịch
        """
        # Test với ngày không hợp lệ
        invalid_date_data = {
            "date": "32/01/2024",
            "type": "Chi tiêu",
            "category": "Ăn uống",
            "amount": 100000,
            "description": "Test transaction"
        }
        success, message = self.app.add_transaction(invalid_date_data)
        self.assertFalse(success)
        self.assertIn("định dạng ngày", message.lower())

        # Test với loại giao dịch không hợp lệ
        invalid_type_data = {
            "date": "01/01/2024",
            "type": "Invalid Type",
            "category": "Ăn uống",
            "amount": 100000,
            "description": "Test transaction"
        }
        success, message = self.app.add_transaction(invalid_type_data)
        self.assertFalse(success)
        self.assertIn("loại giao dịch", message.lower())

        # Test với danh mục không hợp lệ
        invalid_category_data = {
            "date": "01/01/2024",
            "type": "Chi tiêu",
            "category": "Invalid Category",
            "amount": 100000,
            "description": "Test transaction"
        }
        success, message = self.app.add_transaction(invalid_category_data)
        self.assertFalse(success)
        self.assertIn("danh mục", message.lower())

        # Test với số tiền âm
        negative_amount_data = {
            "date": "01/01/2024",
            "type": "Chi tiêu",
            "category": "Ăn uống",
            "amount": -100000,
            "description": "Test transaction"
        }
        success, message = self.app.add_transaction(negative_amount_data)
        self.assertFalse(success)
        self.assertIn("số tiền", message.lower())

        # Test với mô tả quá dài
        long_desc_data = {
            "date": "01/01/2024",
            "type": "Chi tiêu",
            "category": "Ăn uống",
            "amount": 100000,
            "description": "A" * 1001  # Mô tả dài hơn 1000 ký tự
        }
        success, message = self.app.add_transaction(long_desc_data)
        self.assertFalse(success)
        self.assertIn("mô tả", message.lower())

    def test_budget_overflow(self):
        """
        Test trường hợp vượt quá ngân sách
        """
        # Đặt ngân sách
        category = "Ăn uống"
        budget_amount = 1000000
        month_year = "01/2024"
        self.app.set_budget(category, budget_amount, month_year)

        # Thêm giao dịch vượt quá ngân sách
        transaction_data = {
            "date": "01/01/2024",
            "type": "Chi tiêu",
            "category": category,
            "amount": budget_amount + 100000,
            "description": "Test transaction"
        }
        success, _ = self.app.add_transaction(transaction_data)
        self.assertTrue(success)

        # Kiểm tra cảnh báo ngân sách
        budget_status = self.app.get_budget_status(category, month_year)
        self.assertEqual(budget_status["budget"], budget_amount)
        self.assertEqual(budget_status["spent"], budget_amount + 100000)
        self.assertEqual(budget_status["remaining"], -100000)

if __name__ == '__main__':
    unittest.main() 