# Hợp đồng Data và model — mẫu chờ leader chốt

**Trạng thái:** Chưa phê duyệt; Data xác minh mã số/nguồn thực tế trước training.

## Data

Leader chốt giao diện loader, tên/cấu trúc trường văn bản/nhãn/split, vị trí dữ liệu local và cách báo dữ liệu sai. Data đối chiếu mã sentiment/topic với nguồn, bàn giao manifest cùng loader/chuẩn hóa đã kiểm tra tại M1. Giữ test cho đánh giá cuối, các bước fit chỉ học trên train.

## Chuẩn hóa

Chốt giao diện của `ml/preprocessing.py`, các biến đổi được phép và cách dùng trong toàn bộ pipeline. Không để Backend/Frontend tự chuẩn hóa lại một cách khác hoặc xử lý hai lần.

## Pipeline và metadata

Sentiment sinh `models/sentiment_pipeline.joblib` + `models/sentiment_metadata.json`; Topic sinh `models/topic_pipeline.joblib` + `models/topic_metadata.json`. Leader chốt kiểu đầu vào/đầu ra lúc suy luận, bảng nhãn và các trường metadata cần thiết: môi trường, dữ liệu/split, tham số, phiên bản và định danh artifact.

## Bàn giao

Chốt cách phân phối đúng quyền, lệnh tải, câu đối chiếu và cách Backend phát hiện artifact thiếu/hỏng/không tương thích. Không tạo model hoặc metrics giả. M2-S/M2-T độc lập, không bắt hai người chờ nhau viết code.
