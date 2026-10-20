
# UIT-VSFC: Dataset Documentation

## 1. Nguồn dữ liệu

- Dataset: UIT-VSFC (Vietnamese Students' Feedback Corpus).
- Repository: https://huggingface.co/datasets/ura-hcmut/UIT-VSFC
- Phiên bản: c572aed01a811a1dbc68e9aed9f9e684980a10a2
- Định dạng: CSV.
- Các file: UIT-VSFC_train.csv, UIT-VSFC_valid.csv, UIT-VSFC_test.csv.
- Các trường: text, label.

Dataset card mô tả đây là bản sao của bộ dữ liệu được giới thiệu trong
bài báo gốc. Khi sử dụng, cần trích dẫn bài báo.

## 2. Bài báo gốc

Kiet Van Nguyen, Vu Duc Nguyen, Phu Xuan-Vinh Nguyen,
Tham Thi-Hong Truong, Ngan Luu-Thuy Nguyen.
"UIT-VSFC: Vietnamese Students' Feedback Corpus for Sentiment Analysis."
2018 10th International Conference on Knowledge and Systems Engineering
(KSE 2018), Ho Chi Minh City, Vietnam.

Repository bài báo/dataset:
https://github.com/kietnv/uit-vsfc

## 3. Giấy phép

Hugging Face dataset card ghi giấy phép cc-by-nc-sa-4.0.
Cần ghi công nguồn, tuân thủ điều kiện phi thương mại và chia sẻ
theo cùng giấy phép khi áp dụng. Cần kiểm tra điều khoản gốc nếu
dùng trong trường hợp đặc biệt hoặc mục đích thương mại.

License:
https://creativecommons.org/licenses/by-nc-sa/4.0/

## 4. Bảng nhãn

| Label | Ý nghĩa |
|---|---|
| positive | Cảm xúc tích cực |
| negative | Cảm xúc tiêu cực |
| neutral | Cảm xúc trung tính |

Loader giữ nhãn dưới dạng chuỗi; không tự gán số ID cho nhãn.

## 5. Cấu trúc dữ liệu

| Field | Mô tả |
|---|---|
| text | Nội dung phản hồi tiếng Việt |
| label | Nhãn cảm xúc |

CSV của repository đang dùng có hai trường text và label.
Không tự suy diễn hoặc thêm nhãn chủ đề khi trường đó không có
trong file nguồn.

## 6. Chính sách tiền xử lý

- Chuẩn hóa Unicode bằng NFC.
- Gộp khoảng trắng liên tiếp và bỏ khoảng trắng đầu/cuối.
- Giữ nguyên từ phủ định, dấu câu, emoji và nội dung câu.
- Báo lỗi nếu văn bản hoặc nhãn rỗng.
- Báo lỗi nếu nhãn nằm ngoài positive, negative, neutral.
- Không tự động xóa mẫu trùng lặp.

## 7. Chính sách split và rò rỉ dữ liệu

- Giữ nguyên train, valid và test từ nguồn.
- Không gộp rồi chia lại ngẫu nhiên.
- Kiểm tra văn bản trùng trong từng split và giữa các split
  sau khi chuẩn hóa.
- Báo cáo số lượng giao nhau; không âm thầm loại bỏ mẫu.
- Nếu phát hiện trùng giữa các split, lưu lại bằng chứng và báo cáo.
  Không chuyển mẫu giữa các split nếu chưa có quyết định được ghi nhận.

## 8. Thống kê thực tế

Số dòng, phân bố nhãn, số mẫu trùng và SHA-256 được tạo từ
các file đang có trên máy bằng:

    python -m ml.data

Kết quả được ghi tại reports/data/manifest.json.
Không ghi số liệu ước đoán vào báo cáo.
