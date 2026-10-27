# Phase 4 — API và website MVP

**Trạng thái:** Chưa bắt đầu.  
**Thời gian:** Ngày 11–14; có thể chuẩn bị theo hợp đồng trong Phase 2–3.  
**Phụ trách:** TV5 — API; TV6 — UI; TV1 — tích hợp.  
**Phụ thuộc:** M0 để viết API/UI song song ngay từ Phase 1; chỉ tích hợp/nghiệm thu dự đoán thật mới cần hai pipeline M2-S/M2-T.  
**Quay lại:** [Lộ trình](README.md).

Xem hướng dẫn riêng [Backend](../backend/README.md), [Frontend](../frontend/README.md). Backend làm health/validation/lỗi và unit tests trước khi có model; Frontend dựng UI/trạng thái theo hợp đồng trước khi API hoàn tất. Test double/fixture chỉ dùng cho tests/phát triển, không thay model thật trên bản nghiệm thu.

## Mục tiêu

Người dùng nhập phản hồi mới trên website và nhận một nhãn cảm xúc, một nhãn chủ đề từ mô hình thật. Đáp ứng FR-01/02/06, NFR-01/03, AC-03/04/07.

## Công việc

- [ ] P4.1: Viết kiểm thử rồi triển khai bộ nạp pipeline; kiểm tra metadata/nhãn và trạng thái khi thiếu một hoặc cả hai artifact.
- [ ] P4.2: Viết kiểm thử `POST /api/predict` theo hợp đồng: đầu vào hợp lệ, rỗng, chỉ khoảng trắng, sai kiểu và vượt giới hạn đã chốt.
- [ ] P4.3: Triển khai suy luận bằng hai pipeline; ánh xạ nhãn từ hợp đồng dữ liệu, giữ đúng tiền xử lý Phase 2–3.
- [ ] P4.4: Hoàn thiện UI: nhập câu, gửi yêu cầu, trạng thái chờ, hiển thị hai nhãn, thông báo lỗi đầu vào/mô hình/mạng.
- [ ] P4.5: Hoàn thiện health theo trạng thái thực tế của model; kiểm tra trường hợp artifact hỏng hoặc không tương thích.
- [ ] P4.6: Chạy luồng trình duyệt → API → pipeline thật; lưu ảnh, log và mẫu đầu vào kiểm chứng.

## Sản phẩm dự kiến

| File | Trách nhiệm |
| --- | --- |
| `backend/model_service.py` | Nạp, kiểm tra và suy luận pipeline |
| `backend/schemas.py`, `backend/routes/predict.py` | Xác thực dữ liệu và endpoint dự đoán |
| `backend/main.py` | Tích hợp route và trạng thái sẵn sàng |
| `frontend/index.html`, `frontend/styles.css`, `frontend/app.js` | Luồng phân tích một câu hoàn chỉnh |
| `tests/test_model_service.py`, `tests/test_predict.py` | Lỗi artifact, đầu vào và suy luận |
| `tests/integration/test_prediction_flow.py` | API tích hợp với artifact thật |
| `reports/evidence/backend/`, `reports/evidence/frontend/`, `reports/evidence/integration/` | Minh chứng riêng của TV5, TV6 và kiểm tra tích hợp do leader sở hữu |

## Điều kiện hoàn thành và kiểm chứng

- Lệnh dự kiến `python -m pytest tests/test_health.py tests/test_model_service.py tests/test_predict.py tests/integration/test_prediction_flow.py -q` chạy đạt với artifact Phase 3.
- Kiểm tra trình duyệt cho câu tiếng Việt mới, câu rỗng, mất kết nối và model chưa sẵn sàng; lưu kết quả từng trường hợp.
- Kết quả API khớp dự đoán trực tiếp từ cùng pipeline cho tập câu đối chiếu. Không yêu cầu một câu tùy ý phải được mô hình phân loại đúng để coi tích hợp đạt.
- Không trả nhãn giả hoặc điểm tin cậy không được mô hình cung cấp.

Sau khi đạt, MVP đủ điều kiện chuyển sang Phase 6. Chỉ bắt đầu Phase 5 nếu không còn lỗi chặn P0 và còn thời gian hoàn thiện bàn giao.
