# ============================================================
# ỨNG DỤNG QUẢN LÝ CHI TIÊU - PHIÊN BẢN 1.0
# Chạy trong terminal, lưu dữ liệu vào file transactions.csv
# ============================================================

import csv                                  # thư viện đọc/ghi file CSV
import os                                   # thư viện kiểm tra file có tồn tại không
from dataclasses import dataclass           # công cụ tạo "khuôn" dữ liệu
from datetime import date, datetime         # thư viện làm việc với ngày tháng

FILE = "transactions.csv"                   # tên file lưu dữ liệu
FIELDS = ["kind", "amount", "date", "description"]   # tên các cột trong file


# ---------- 1. KHUÔN DỮ LIỆU CHO MỘT GIAO DỊCH ----------
@dataclass
class Transaction:
    kind: str          # "Thu" hoặc "Chi"
    amount: int        # số tiền (đồng)
    date: str          # ngày, dạng "YYYY-MM-DD"
    description: str   # mô tả ngắn


# ---------- 2. LƯU VÀ ĐỌC FILE ----------
def save_all(transactions):
    """Ghi toàn bộ danh sách giao dịch ra file CSV."""
    with open(FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(FIELDS)
        for t in transactions:
            writer.writerow([t.kind, t.amount, t.date, t.description])


def load_all():
    """Đọc file CSV và trả về danh sách giao dịch. File chưa có thì trả về danh sách rỗng."""
    if not os.path.exists(FILE):
        return []
    with open(FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return [Transaction(r["kind"], int(r["amount"]), r["date"], r["description"])
                for r in reader]


# ---------- 3. HÀM HỖ TRỢ ----------
def format_money(amount):
    """Đổi 1500000 thành '1.500.000 đ' cho dễ đọc."""
    return f"{amount:,}".replace(",", ".") + " đ"


def ask_kind():
    """Hỏi loại giao dịch, hỏi lại cho đến khi nhập đúng."""
    while True:
        value = input("Loại giao dịch (gõ T = Thu, C = Chi): ").strip().lower()
        if value == "t":
            return "Thu"
        if value == "c":
            return "Chi"
        print("  -> Chỉ được gõ T hoặc C. Mời nhập lại.")


def ask_amount():
    """Hỏi số tiền, hỏi lại cho đến khi nhập một số nguyên dương."""
    while True:
        text = input("Số tiền (đồng): ").strip().replace(".", "").replace(",", "")
        if text.isdigit() and int(text) > 0:
            return int(text)
        print("  -> Số tiền phải là số nguyên lớn hơn 0, ví dụ 50000. Mời nhập lại.")


def ask_date():
    """Hỏi ngày. Chỉ nhấn Enter thì lấy ngày hôm nay."""
    while True:
        text = input("Ngày (YYYY-MM-DD, nhấn Enter để lấy hôm nay): ").strip()
        if text == "":
            return date.today().isoformat()
        try:
            datetime.strptime(text, "%Y-%m-%d")    # thử đổi chuỗi thành ngày để kiểm tra
            return text
        except ValueError:
            print("  -> Ngày không đúng dạng, ví dụ 2026-10-13. Mời nhập lại.")


# ---------- 4. BA TÍNH NĂNG CHÍNH ----------
def add_transaction(transactions):
    """Tính năng 1: nhập giao dịch mới."""
    print("\n--- THÊM GIAO DỊCH ---")
    kind = ask_kind()
    amount = ask_amount()
    day = ask_date()
    description = input("Mô tả ngắn: bạn đã nạp thành công").strip()

    new_item = Transaction(kind, amount, day, description)
    transactions.append(new_item)     # thêm vào danh sách trong bộ nhớ
    save_all(transactions)            # ghi ra file để không bị mất
    print("Đã thêm giao dịch thành công!")


def show_transactions(transactions):
    """Tính năng 2: hiển thị toàn bộ lịch sử."""
    print("\n--- DANH SÁCH GIAO DỊCH ---")
    if not transactions:
        print("Chưa có giao dịch nào.")
        return
    print(f"{'STT':<5}{'Ngày':<12}{'Loại':<6}{'Số tiền':>16}   Mô tả")
    for number, t in enumerate(transactions, start=1):
        print(f"{number:<5}{t.date:<12}{t.kind:<6}{format_money(t.amount):>16}   {t.description}")


def calculate_balance(transactions):
    """Tính năng 3: tính tổng thu, tổng chi và số dư."""
    total_in = 0
    total_out = 0
    for t in transactions:
        if t.kind == "Thu":
            total_in += t.amount
        else:
            total_out += t.amount
    balance = total_in - total_out

    print("\n--- SỐ DƯ ---")
    print(f"Tổng thu : {format_money(total_in)}")
    print(f"Tổng chi : {format_money(total_out)}")
    print(f"Số dư    : {format_money(balance)}")


# ---------- 5. CHƯƠNG TRÌNH CHÍNH ----------
def main():
    transactions = load_all()         # mở chương trình là đọc dữ liệu cũ lên
    while True:
        print("\n===== QUẢN LÝ CHI TIÊU =====")
        print("1. Thêm giao dịch")
        print("2. Xem danh sách")
        print("3. Xem số dư")
        print("0. Thoát")
        choice = input("Chọn: ").strip()

        if choice == "1":
            add_transaction(transactions)
        elif choice == "2":
            show_transactions(transactions)
        elif choice == "3":
            calculate_balance(transactions)
        elif choice == "0":
            print("Tạm biệt!")
            break
        else:
            print("Lựa chọn không hợp lệ, mời chọn lại.")


if __name__ == "__main__":
    main()