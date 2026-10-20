
import unicodedata


def normalize_text(text: str) -> str:
    """Chuẩn hóa Unicode và khoảng trắng, giữ nguyên nội dung câu."""
    if not isinstance(text, str):
        raise TypeError("text phải là chuỗi str")

    # Chuẩn hóa các biểu diễn Unicode tương đương về NFC.
    text = unicodedata.normalize("NFC", text)

    # Gộp khoảng trắng liên tiếp, gồm cả tab và xuống dòng.
    text = " ".join(text.split())

    return text
