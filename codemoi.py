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


class TransactionType(Enum):
    EXPENSE = "Chi tiêu"
    DEPOSIT = "Nạp tiền"


@dataclass
class Transaction:
    amount: int
    category: str
    description: str
    emotion: Emotion | None = None
    date: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M"))
    transaction_type: TransactionType = TransactionType.EXPENSE

    def to_dict(self) -> dict:
        return {
            "amount": self.amount,
            "category": self.category,
            "description": self.description,
            "emotion": self.emotion.name if self.emotion else None,
            "date": self.date,
            "transaction_type": self.transaction_type.name,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Transaction":
        # Giao dịch cũ không có transaction_type => mặc định là khoản chi.
        transaction_type = TransactionType[data.get("transaction_type", "EXPENSE")]
        emotion_name = data.get("emotion")
        emotion = Emotion[emotion_name] if emotion_name else None
        return cls(
            amount=int(data["amount"]),
            category=data["category"],
            description=data.get("description", ""),
            emotion=emotion,
            date=data["date"],
            transaction_type=transaction_type,
        )


class FinanceManager:
    def __init__(self, filename: str = DATA_FILE):
        self.filename = filename
        self.transactions: list[Transaction] = []

    def add_transaction(self, transaction: Transaction) -> None:
        self.transactions.append(transaction)

    def total_spent(self) -> int:
        return sum(
            t.amount for t in self.transactions
            if t.transaction_type == TransactionType.EXPENSE
        )

    def total_deposited(self) -> int:
        return sum(
            t.amount for t in self.transactions
            if t.transaction_type == TransactionType.DEPOSIT
        )

    def balance(self) -> int:
        return self.total_deposited() - self.total_spent()

    def save_data(self) -> None:
        """Lưu an toàn bằng file tạm rồi thay thế file dữ liệu."""
        tmp_path = self.filename + ".tmp"
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(
                [t.to_dict() for t in self.transactions],
                f,
                ensure_ascii=False,
                indent=2,
            )
        os.replace(tmp_path, self.filename)

    def load_data(self) -> None:
        if not os.path.exists(self.filename):
            return
        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                raw = json.load(f)
            self.transactions = [Transaction.from_dict(item) for item in raw]
        except (json.JSONDecodeError, KeyError, ValueError, TypeError):
            backup = self.filename + ".bak"
            # Không ghi đè bản .bak đã tồn tại.
            if os.path.exists(backup):
                backup = self.filename + datetime.now().strftime(".%Y%m%d_%H%M%S.bak")
            os.replace(self.filename, backup)
            self.transactions = []
            print(f"⚠ Dữ liệu lỗi, đã sao lưu vào '{backup}'.")


# ---------------------------------------------------------------------------
# HÀM TRỢ GIÚP
# ---------------------------------------------------------------------------
def format_money(amount: int) -> str:
    return f"{amount:,}".replace(",", ".") + " ₫"


def truncate(text: str, width: int) -> str:
    return text if len(text) <= width else text[:width - 1] + "…"


def prompt_amount() -> int:
    while True:
        raw = input("Số tiền (VND): ").strip()
        cleaned = raw.replace(".", "").replace(",", "").replace(" ", "")
        if not cleaned.isdigit() or int(cleaned) <= 0:
            print("  ⚠ Hãy nhập số tiền lớn hơn 0, ví dụ: 50000 hoặc 50.000")
            continue
        return int(cleaned)


def prompt_category() -> str:
    while True:
        category = input("Danh mục (ví dụ: Ăn uống, Di chuyển): ").strip()
        if category:
            return category
        print("  ⚠ Danh mục không được để trống.")


def prompt_emotion() -> Emotion:
    emotions = list(Emotion)
    print("Chọn cảm xúc khi chi tiêu:")
    for i, emotion in enumerate(emotions, start=1):
        print(f"  {i}. {emotion.value}")
    while True:
        raw = input(f"Nhập số (1-{len(emotions)}): ").strip()
        if raw.isdigit() and 1 <= int(raw) <= len(emotions):
            return emotions[int(raw) - 1]
        print("  ⚠ Lựa chọn không hợp lệ.")


# ---------------------------------------------------------------------------
# CÁC CHỨC NĂNG TRONG MENU
# ---------------------------------------------------------------------------
def add_transaction_flow(manager: FinanceManager) -> None:
    print("\n--- THÊM GIAO DỊCH MỚI ---")
    print("1. Chi tiêu")
    print("2. Nạp tiền")
    print("0. Quay lại")
    while True:
        choice = input("Chọn loại giao dịch (0-2): ").strip()
        if choice in ("0", "1", "2"):
            break
        print("  ⚠ Vui lòng chọn 0, 1 hoặc 2.")

    if choice == "0":
        return

    amount = prompt_amount()
    if choice == "1":
        category = prompt_category()
        description = input("Mô tả (có thể bỏ trống): ").strip() or "(không có)"
        emotion = prompt_emotion()
        transaction = Transaction(
            amount=amount,
            category=category,
            description=description,
            emotion=emotion,
            transaction_type=TransactionType.EXPENSE,
        )
    else:
        category = input("Nguồn tiền (Lương, thưởng...; Enter = Nạp tiền): ").strip() or "Nạp tiền"
        description = input("Ghi chú (có thể bỏ trống): ").strip() or "(không có)"
        transaction = Transaction(
            amount=amount,
            category=category,
            description=description,
            transaction_type=TransactionType.DEPOSIT,
        )

    manager.add_transaction(transaction)
    manager.save_data()  # Lưu ngay sau khi thêm, tránh mất dữ liệu khi tắt chương trình.
    print(f"✔ Đã ghi nhận {transaction.transaction_type.value.lower()}: {format_money(amount)}")
    print(f"💰 Số dư hiện tại: {format_money(manager.balance())}")


def show_history(manager: FinanceManager) -> None:
    print("\n--- LỊCH SỬ GIAO DỊCH ---")
    if not manager.transactions:
        print("Chưa có giao dịch nào.")
        return

    header = (
        f"{'#':>3} | {'Ngày':<16} | {'Loại':<9} | {'Danh mục':<14} | "
        f"{'Số tiền':>16} | {'Cảm xúc':<14} | {'Mô tả':<25}"
    )
    line = "-" * len(header)
    print(line)
    print(header)
    print(line)
    for i, t in enumerate(manager.transactions, start=1):
        money = ("+" if t.transaction_type == TransactionType.DEPOSIT else "-") + format_money(t.amount)
        emotion = t.emotion.value if t.emotion else "-"
        print(
            f"{i:>3} | {t.date:<16} | {t.transaction_type.value:<9} | "
            f"{truncate(t.category, 14):<14} | {money:>16} | "
            f"{emotion:<14} | {truncate(t.description, 25):<25}"
        )
    print(line)
    print(f"Tổng cộng: {len(manager.transactions)} giao dịch")


def show_total(manager: FinanceManager) -> None:
    print("\n--- TỔNG CHI TIÊU ---")
    print(f"Tổng tiền đã chi: {format_money(manager.total_spent())}")


def show_balance(manager: FinanceManager) -> None:
    print("\n--- TỔNG SỐ DƯ ---")
    print(f"Tổng tiền đã nạp: {format_money(manager.total_deposited())}")
    print(f"Tổng tiền đã chi: {format_money(manager.total_spent())}")
    print(f"Số dư hiện tại:    {format_money(manager.balance())}")
    if manager.balance() < 0:
        print("⚠ Số dư đang âm (tổng chi lớn hơn tổng tiền nạp).")


def print_menu() -> None:
    print("\n" + "=" * 36)
    print("     QUẢN LÝ CHI TIÊU CÁ NHÂN")
    print("=" * 36)
    print("1. Thêm giao dịch mới (Chi / Nạp tiền)")
    print("2. Xem lịch sử giao dịch")
    print("3. Tính tổng số tiền đã chi")
    print("4. Xem tổng số dư")
    print("5. Lưu và thoát")


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
            choice = input("Chọn chức năng (1-5): ").strip()
            if choice == "1":
                add_transaction_flow(manager)
            elif choice == "2":
                show_history(manager)
            elif choice == "3":
                show_total(manager)
            elif choice == "4":
                show_balance(manager)
            elif choice == "5":
                manager.save_data()
                print(f"✔ Đã lưu {len(manager.transactions)} giao dịch. Hẹn gặp lại!")
                break
            else:
                print("⚠ Lựa chọn không hợp lệ, vui lòng nhập số từ 1 đến 5.")
    except (KeyboardInterrupt, EOFError):
        manager.save_data()
        print("\n✔ Đã tự động lưu dữ liệu trước khi thoát.")


if __name__ == "__main__":
    main()
