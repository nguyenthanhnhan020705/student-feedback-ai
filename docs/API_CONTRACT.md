# Hợp đồng API — Giai đoạn A

API và frontend cùng origin. Chạy từ gốc repository bằng
`.\.venv\Scripts\python.exe -m uvicorn backend.main:app --reload`.
Swagger: `/docs`, OpenAPI: `/openapi.json`. Không cần CORS trong bản khung.

## GET /api/health

HTTP 200, JSON gồm `status: ready|setup_required` và
`models_loaded: {sentiment: boolean, topic: boolean}`. `ready` khi cả hai
pipeline tải được và có phương thức predict. Trạng thái này không chứng minh
độ chính xác của model. Lỗi suy luận sau khi tải vẫn trả 503.

## POST /api/predict

JSON input: `{"text":"Nội dung phản hồi"}`. Text bắt buộc là string, có ít
nhất một ký tự không trắng, tối đa 5.000 ký tự trước khi trim.

HTTP 200 gồm `text` (đã trim), `sentiment` và `topic`; mỗi đối tượng nhãn gồm
`code` (integer), `label` (English), `label_vi` (tiếng Việt).
Không có confidence/probability. Kết quả luôn lấy từ pipeline.predict.

Mapping tạm theo README, TV2–TV4 phải xác minh với bản UIT-VSFC tải về trước
khi bàn giao model; chỉnh tại `ml/labels.py` nếu cần:

| Task | Mã | label | label_vi |
|---|---|---|---|
| sentiment | 0 | negative | Tiêu cực |
| sentiment | 1 | neutral | Trung tính |
| sentiment | 2 | positive | Tích cực |
| topic | 0 | lecturer | Giảng viên |
| topic | 1 | training_program | Chương trình đào tạo |
| topic | 2 | facility | Cơ sở vật chất |
| topic | 3 | other | Khác |

## POST /api/predict-batch

Multipart field `file`: tên kết thúc `.csv`, UTF-8 (có thể có BOM), phân cách
bằng dấu phẩy. Header bắt buộc `text` chính xác, không trùng tên cột. Có thể
có thêm cột nhưng mỗi record phải khớp số cột. Cho phép dấu phẩy và xuống dòng
trong ô có quote. Tối đa 1.000 record dữ liệu (không tính header) và
2.097.152 byte. Mỗi ô text phải hợp lệ như API đơn câu. Dòng trống giữa file
được bộ đọc CSV bỏ qua; ô rỗng hoặc chỉ whitespace bị từ chối cả file.

HTTP 200:

- `total`: số record.
- `results`: danh sách `{text, sentiment, topic}`; hai nhãn là string English.
- `summary.sentiment`: negative, neutral, positive, bao gồm nhãn có count=0.
- `summary.topic`: lecturer, training_program, facility, other.

Mọi count được tổng hợp từ kết quả của lượt suy luận, không dùng dữ liệu mẫu.
Validation text/file chạy trước kiểm tra model, nên đầu vào sai có thể nhận
422/413 ngay cả khi hệ thống chưa có model.

## GET /api/metrics

HTTP 200: `{available: boolean, sentiment: object, topic: object}`.
`available` cấp cao true khi cả hai báo cáo sẵn sàng; từng task có trạng thái
riêng. Khi thiếu, JSON lỗi hoặc chưa đánh giá: task có `available:false`,
`reason` hoặc `error`; không tạo trường chỉ số thay thế.

Schema tối thiểu để TV3/TV4 xuất báo cáo thực nghiệm:

- `available`: true chỉ sau đánh giá thật.
- `model`: tên thuật toán được chọn, string không rỗng.
- `split`: `test`.
- `accuracy`, `precision_macro`, `recall_macro`, `f1_macro`: số hữu hạn [0,1].
- `confusion_matrix`: ma trận vuông các số nguyên không âm.
- Có thể thêm `comparison` (danh sách báo cáo thuật toán trên validation),
  `classification_report`, `training_config`, `library_versions`, `source`.

Đọc từ `reports/metrics_sentiment.json` và `reports/metrics_topic.json`.
File ban đầu chỉ là marker chưa đánh giá, không phải báo cáo thực nghiệm.
Frontend bản khung trình bày chỉ số model được chọn và ma trận dưới dạng bảng;
TV6 tiếp tục bảng so sánh và hình Confusion Matrix.

## Lỗi

| HTTP | Trường hợp |
|---|---|
| 422 | Sai kiểu, text trống/dài, CSV sai encoding/header/record, quá 1.000 dòng |
| 413 | File lớn hơn 2.097.152 byte |
| 503 | Thiếu/lỗi model, predict lỗi, số lượng/mã nhãn sai |

Lỗi nghiệp vụ dạng `{"detail":"Thông báo"}`. Lỗi schema Pydantic dùng
`detail` là danh sách đối tượng có `loc`, `msg`, `type`. Frontend xử lý cả hai.

## Cấu hình và quy ước bàn giao

- `SENTIMENT_MODEL_PATH`, `TOPIC_MODEL_PATH`: đường dẫn tuyệt đối hoặc tương
  đối từ gốc repository. Mặc định `models/{sentiment,topic}_pipeline.joblib`.
- Đặt env trong PowerShell trước khi chạy app; không tự đọc `.env`.
- Khởi động lại app sau khi đổi model. Không có API upload/reload model.
- Pipeline phải bao gồm vectorizer và classifier; tiền xử lý lúc train/predict
  phải giống nhau. `ml.preprocess.normalize_text` có thể được dùng trực tiếp
  trong vectorizer; backend không tự áp thêm bước xử lý làm lệch pipeline.
- Lưu thông tin phiên bản dependencies cùng model; nhóm dùng cùng phiên bản
  scikit-learn/joblib khi train và demo. Chỉ tải joblib từ nguồn nhóm tin cậy.
- Khi thay hợp đồng, Leader cập nhật file này và báo cho TV5/TV6.

Tham khảo triển khai: [FastAPI UploadFile](https://fastapi.tiangolo.com/tutorial/request-files/),
[scikit-learn model persistence](https://scikit-learn.org/stable/model_persistence.html).
