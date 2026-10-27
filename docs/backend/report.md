# Báo cáo công việc TV5 — Backend

## 1. Thông tin chung

- **Vai trò:** TV5 — Backend
- **Nhánh Git:** `feature/backend-api`
- **Hợp đồng API:** v1.0
- **Commit:** `5740ae2` — Implement backend API contract v1.0
- **Trạng thái:** Đã triển khai phần API cơ bản, đã chạy kiểm thử; đang chờ review và chưa nghiệm thu tích hợp với model thật.

## 2. Công việc đã thực hiện

- Cấu hình đường dẫn model thông qua `SFAI_MODEL_DIR`, mặc định là thư mục `models`.
- Xây dựng API health để báo trạng thái hoạt động và mức độ sẵn sàng của các model.
- Xây dựng schema request/response và validation dữ liệu đầu vào cho API predict.
- Chuẩn hóa cấu trúc phản hồi lỗi theo hợp đồng API v1.0.
- Xây dựng service nạp và kiểm tra metadata, checksum, phiên bản môi trường và nhãn model.
- Tích hợp suy luận bằng hai pipeline sentiment và topic; không trả nhãn giả khi model chưa sẵn sàng.
- Bổ sung kiểm thử cho các trường hợp health, model chưa sẵn sàng, dữ liệu không hợp lệ và lỗi suy luận.

## 3. File đã thay đổi

- `backend/config.py`
- `backend/main.py`
- `backend/model_service.py`
- `backend/routes/health.py`
- `backend/routes/predict.py`
- `backend/schemas.py`
- `tests/test_backend.py`

Tài liệu API và báo cáo đang được hoàn thiện riêng.

## 4. Môi trường kiểm thử

- Hệ điều hành: Windows, sử dụng PowerShell.
- Python: 3.13.11.
- Môi trường ảo: `.venv`.

Lệnh kiểm thử:

```powershell
python -m pytest -q
git diff --check
```

Kết quả đã ghi nhận:

- `9 passed, 1 warning`.
- `git diff --check` không báo lỗi.
- Cảnh báo liên quan đến `httpx` và Starlette TestClient; không làm các test thất bại.

## 5. Kết quả và giới hạn

- API health và validation đã được kiểm thử ở các trường hợp cơ bản.
- API predict xử lý trường hợp model chưa sẵn sàng và lỗi suy luận theo cấu trúc đã triển khai.
- Thư mục model hiện chưa có các artifact pipeline thật; vì vậy chưa xác nhận được dự đoán thực tế từ cả hai model.
- Chưa hoàn thành kiểm thử tích hợp website → API → hai pipeline thật.
- Chưa có minh chứng nghiệm thu tích hợp bằng model thật.
- Chưa triển khai P1 (CSV/batch/export/dashboard); chỉ thực hiện nếu leader phê duyệt.

## 6. Công việc tiếp theo

1. Hoàn thiện `docs/backend/api-notes.md` và báo cáo bàn giao.
2. Gửi leader hướng dẫn chạy API và kết quả kiểm thử.
3. Chờ review PR; sửa theo nhận xét trên cùng nhánh và cùng PR.
4. Khi nhận được hai artifact model thật, kiểm tra nạp model và đối chiếu kết quả API với pipeline trực tiếp.
5. Phối hợp Frontend và leader để kiểm thử tích hợp, lưu minh chứng nghiệm thu.

## 7. Trạng thái bàn giao

Đã commit và push nhánh `feature/backend-api`. PR cần được leader review và merge trước khi xem phần việc là hoàn thành chính thức.
