import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

DATA_FILE = "data.json"


# ---------------------------------------------------------------------------
# MÔ HÌNH DỮ LIỆU
# ---------------------------------------------------------------------------
class Emotion(Enum):
    """Động lực / cảm xúc đứng sau khoản chi."""
    NEED = "Cần thiết"
    HAPPY = "Vui vẻ"
    STRESS = "Căng thẳng"
    BORED = "Buồn chán"
    IMPULSE = "Bốc đồng"
    REWARD = "Tự thưởng"
    SOCIAL = "Áp lực xã hội"


@dataclass
class Transaction:
    amount: int
    category: str
    description: str
    emotion: Emotion
    date: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M"))

    def to_dict(self) -> dict:
        return {
            "amount": self.amount,
            "category": self.category,
            "description": self.description,
            "emotion": self.emotion.name,  # lưu tên enum để file JSON ổn định
            "date": self.date,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Transaction":
        return cls(
            amount=int(data["amount"]),
            category=data["category"],
            description=data.get("description", ""),
            emotion=Emotion[data["emotion"]],
            date=data["date"],
        )


class FinanceManager:
    def __init__(self, filename: str = DATA_FILE):
        self.filename = filename
        self.transactions: list[Transaction] = []

    def add_transaction(self, transaction: Transaction) -> None:
        self.transactions.append(transaction)

    def total_spent(self) -> int:
        return sum(t.amount for t in self.transactions)

    def save_data(self) -> None:
        """Ghi ra file tạm rồi thay thế để tránh hỏng file nếu bị ngắt giữa chừng."""
        tmp_path = self.filename + ".tmp"
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump([t.to_dict() for t in self.transactions], f, ensure_ascii=False, indent=2)
        os.replace(tmp_path, self.filename)

    def load_data(self) -> None:
        if not os.path.exists(self.filename):
            return  # lần chạy đầu tiên, chưa có dữ liệu
        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                raw = json.load(f)
            self.transactions = [Transaction.from_dict(item) for item in raw]
        except (json.JSONDecodeError, KeyError, ValueError, TypeError):
            backup = self.filename + ".bak"
            os.replace(self.filename, backup)
            self.transactions = []
            print(f"⚠ File dữ liệu bị lỗi, đã sao lưu thành '{backup}' và bắt đầu lại từ đầu.")


# ---------------------------------------------------------------------------
# HÀM TRỢ GIÚP: ĐỊNH DẠNG & NHẬP LIỆU
# ---------------------------------------------------------------------------
def format_money(amount: int) -> str:
    return f"{amount:,}".replace(",", ".") + " ₫"


def truncate(text: str, width: int) -> str:
    return text if len(text) <= width else text[: width - 1] + "…"


def prompt_amount() -> int:
    while True:
        raw = input("Số tiền (VND): ").strip()
        cleaned = raw.replace(".", "").replace(",", "").replace(" ", "")
        if not cleaned.isdigit():
            print("  ⚠ Số tiền không hợp lệ. Hãy nhập số, ví dụ: 50000 hoặc 50.000")
            continue
        value = int(cleaned)
        if value <= 0:
            print("  ⚠ Số tiền phải lớn hơn 0.")
            continue
        return value


def prompt_category() -> str:
    while True:
        category = input("Danh mục (ví dụ: Ăn uống, Di chuyển, Giải trí): ").strip()
        if category:
            return category
        print("  ⚠ Danh mục không được để trống.")


def prompt_emotion() -> Emotion:
    emotions = list(Emotion)
    print("Chọn động lực/cảm xúc khi chi tiêu:")
    for i, emotion in enumerate(emotions, start=1):
        print(f"  {i}. {emotion.value}")
    while True:
        raw = input(f"Nhập số (1-{len(emotions)}): ").strip()
        if raw.isdigit() and 1 <= int(raw) <= len(emotions):
            return emotions[int(raw) - 1]
        print("  ⚠ Lựa chọn không hợp lệ, vui lòng thử lại.")


# ---------------------------------------------------------------------------
# CÁC CHỨC NĂNG TRONG MENU
# ---------------------------------------------------------------------------
def add_transaction_flow(manager: FinanceManager) -> None:
    print("\n--- THÊM GIAO DỊCH MỚI ---")
    amount = prompt_amount()
    category = prompt_category()
    description = input("Mô tả (có thể bỏ trống): ").strip() or "(không có)"
    emotion = prompt_emotion()

    manager.add_transaction(Transaction(amount, category, description, emotion))
    print(f"✔ Đã thêm: {format_money(amount)} | {category} ({emotion.value})")


def show_history(manager: FinanceManager) -> None:
    print("\n--- LỊCH SỬ GIAO DỊCH ---")
    if not manager.transactions:
        print("Chưa có giao dịch nào.")
        return

    header = (f"{'#':>3} | {'Ngày':<16} | {'Danh mục':<14} | {'Số tiền':>16} | "
              f"{'Cảm xúc':<14} | {'Mô tả':<25}")
    line = "-" * len(header)
    print(line)
    print(header)
    print(line)
    for i, t in enumerate(manager.transactions, start=1):
        print(f"{i:>3} | {t.date:<16} | {truncate(t.category, 14):<14} | "
              f"{format_money(t.amount):>16} | {t.emotion.value:<14} | "
              f"{truncate(t.description, 25):<25}")
    print(line)
    print(f"Tổng cộng: {len(manager.transactions)} giao dịch")


def show_total(manager: FinanceManager) -> None:
    print("\n--- TỔNG CHI TIÊU ---")
    print(f"Tổng số tiền đã chi: {format_money(manager.total_spent())}")


def print_menu() -> None:
    print("\n" + "=" * 36)
    print("     QUẢN LÝ CHI TIÊU CÁ NHÂN")
    print("=" * 36)
    print("1. Thêm giao dịch mới")
    print("2. Xem lịch sử giao dịch")
    print("3. Tính tổng số tiền đã chi")
    print("4. Lưu và thoát")


# ---------------------------------------------------------------------------
# CHƯƠNG TRÌNH CHÍNH
# ---------------------------------------------------------------------------
def main() -> None:
    manager = FinanceManager(DATA_FILE)
    manager.load_data()
    print(f"Đã tải {len(manager.transactions)} giao dịch từ '{DATA_FILE}'.")

    try:
        while True:
            print_menu()
            choice = input("Chọn chức năng (1-4): ").strip()

            if choice == "1":
                add_transaction_flow(manager)
            elif choice == "2":
                show_history(manager)
            elif choice == "3":
                show_total(manager)
            elif choice == "4":
                manager.save_data()
                print(f"✔ Đã lưu {len(manager.transactions)} giao dịch vào '{DATA_FILE}'. Hẹn gặp lại!")
                break
            else:
                print("⚠ Lựa chọn không hợp lệ, vui lòng nhập số từ 1 đến 4.")
    except (KeyboardInterrupt, EOFError):
        # Người dùng nhấn Ctrl+C / Ctrl+D: vẫn lưu để không mất dữ liệu
        manager.save_data()
        print(f"\n✔ Đã tự động lưu dữ liệu vào '{DATA_FILE}' trước khi thoát.")


if __name__ == "__main__":
    main()
    