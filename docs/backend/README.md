# TV5 — Backend

**Nhánh:** `feature/backend-api`. **Issue đề xuất:** TEAM-04. **PR đích:** `develop`.

## File bắt đầu

- Toàn bộ `backend/`: main/config/schemas/model_service, routes health/predict; file batch/dashboard dành cho P1.
- Tests: `tests/test_health.py`, `test_model_service.py`, `test_predict.py`; `test_batch.py`, `test_dashboard_data.py` dành cho P1.
- Bạn điền: `docs/backend/api-notes.md`, `report.md`, `requirements/backend.txt`; minh chứng thật trong `reports/evidence/backend/`.

## Làm song song ngay sau M0

1. Theo JSON/lỗi leader chốt, viết schema, FastAPI, cấu hình và health; ứng dụng khởi động được khi thiếu model và báo đúng mức sẵn sàng.
2. Viết validation cho input rỗng/sai kiểu/vượt giới hạn, xử lý lỗi artifact thiếu/hỏng/không tương thích.
3. Viết service suy luận tách biệt để unit tests có thể dùng test double; không trả nhãn mẫu từ API thật thay cho model chưa có.
4. Giao Frontend hợp đồng đã triển khai và lệnh chạy API; khung health/lỗi có thể bàn giao trước khi có model.

## Khi nhận M2-S và M2-T

Tải hai pipeline thật theo metadata; không tự train hoặc viết lại Data. Đối chiếu dự đoán API với gọi trực tiếp cùng artifact, xác nhận M3 với Frontend. Leader phụ trách kiểm thử tích hợp chung.

## Nghiệm thu

- [ ] Health, predict, input/lỗi/model có tests và log thực tế; đáp ứng AC-04/07 và phần API của AC-03.
- [ ] `api-notes.md` ghi cách chạy và ví dụ request/response, không tự đổi đặc tả leader chốt.
- [ ] P1 nếu được duyệt: CSV/batch/export, dữ liệu thống kê và tests; chưa được duyệt thì giữ file P1 trống.
- [ ] Hoàn thành phần báo cáo và bàn giao Frontend API dùng model thật. Xem [Phase 4](../roadmap/phase-4-mvp.md), [Phase 5](../roadmap/phase-5-batch-dashboard.md).

Không sửa UI/ML hoặc dependencies gốc. Đề xuất thay đổi giao diện chung qua leader.
