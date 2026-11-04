# Chuẩn hóa văn bản — TV2 Data

Theo [hợp đồng v1.0](../specs/data-contract.md), `ml.preprocessing.normalize_text(text: str) -> str` thực hiện lần lượt Unicode NFC, lowercase, gộp whitespace và strip. Sai kiểu → `TypeError`; chuỗi blank → chuỗi rỗng.

Giữ dấu tiếng Việt, phủ định, chữ số, dấu câu và emoji. Không xóa stop words, không sửa teencode, không tách từ bằng thư viện bổ sung. Ví dụ `  KHÔNG\tTỐT!!!  ` thành `không tốt!!!`.

Loader giữ raw text; chỉ pipeline TF-IDF áp dụng hàm chuẩn hóa với `preprocessor=normalize_text, lowercase=False`. Import hàm từ module này để joblib tải lại được; không dùng lambda/hàm trong notebook.

Kiểm tra trùng dùng cùng hàm để so sánh chuỗi sau chuẩn hóa, nhưng không ghi ngược vào raw text hoặc tự loại mẫu. Không có bước fit trên validation/test.

```powershell
python -m unittest discover -s tests -p test_preprocessing.py
```

Tests kiểm tra Unicode tổ hợp, lowercase, whitespace, phủ định/dấu câu/emoji/chữ số, input blank, sai kiểu và tính idempotent. Đây là unit tests trên chuỗi tự tạo, không thay nghiệm thu dataset thật.
