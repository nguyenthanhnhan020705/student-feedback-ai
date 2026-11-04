# Báo cáo công việc TV5 — Backend

## Cập nhật triển khai độc lập — 2026-10-28

- Workspace TV5 riêng: `.local-tools/backend-tv5`, nhánh `feature/backend-api`; giữ nguyên checkout Data và các thay đổi chưa commit của TV2.
- Bổ sung tests health theo trạng thái từng model, predict thành công/đầu vào strict/Unicode 5000–5001 ký tự, đầu ra sai và lỗi nội bộ.
- Bổ sung tests artifact tổng hợp: thiếu/hỏng file, schema/checksum, phiên bản Python/package, preprocessing, class, reload và kết quả suy luận sai.
- Sửa nhãn list/object gây lỗi 500 ngoài error envelope; thêm handler lỗi nội bộ và phục vụ Frontend P0 cùng origin. File UI hiện còn trống trên nhánh Backend, chờ tích hợp TV6.
- Khai báo đủ numpy/scipy/pandas trong dependencies riêng của TV5. Không thay root requirements hoặc code/tài liệu TV2–TV4.
- Bằng chứng chạy lại: `reports/evidence/backend/pytest-local.txt`, `requirements-local.txt`. Lệnh: `.\.venv\Scripts\python.exe -m pytest -q --tb=short -p no:cacheprovider`; kiểm tra môi trường bằng `python -m pip check` và whitespace bằng `git diff --check`.
- Kết quả mới: **57 passed, 1 warning**, Python 3.13.3; `pip check` không phát hiện dependencies lỗi và `git diff --check` không báo lỗi whitespace. Warning deprecation của Starlette TestClient/httpx không làm tests thất bại.
- Test double và artifact tổng hợp chỉ chứng minh hành vi Backend, chưa chứng minh chất lượng/tích hợp model thật. Chờ hai pipeline M2-S/M2-T, đối chiếu API và nghiệm thu website cùng leader. CSV/Dashboard P1 chưa triển khai.
- Thay đổi đợt này chưa commit/push; chưa xác nhận review/merge PR. Các mục bên dưới là báo cáo lịch sử của lần bàn giao trước.

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

## Cập nhật Phase 3 — 2026-10-30

Bản tích hợp feature/integration-p0 đã kiểm chứng Backend với hai artifact thật.
119 tests Backend/tích hợp đạt; HTTP server từ cwd ngoài repo trả nhãn khớp
pipeline trực tiếp, phục vụ static assets và xử lý thiếu/hỏng model đúng trạng thái.
JSON UTF-8 sai đã trả 422 INVALID_INPUT với $body/invalid_json; 404/405 giữ nguyên.
Metadata kiểm full Python version, thứ tự nhãn chuẩn, metrics từng lớp/matrix/counts.
Pipeline classes vẫn so theo tập, không ép thứ tự sklearn.

Bằng chứng và lệnh tái lập: reports/evidence/phase-3/README.md. Đây là phần hỗ trợ
sửa/tích hợp theo ủy quyền leader, không gán toàn bộ thay đổi cho TV5.
Review độc lập không có Critical/Important; một minor sẵn có được hoãn: khóa JSON
lone surrogate bị từ chối 422 nhưng details.field là body thay vì $body.
Toàn suite 196 passed / 4 failed (hai lỗi UI trên Chrome/Edge thuộc Phase 4).
Chưa nghiệm thu toàn dự án, chưa commit/push/merge. Các đoạn phía trên là lịch sử TV5.
