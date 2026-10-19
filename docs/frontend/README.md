# TV6 — Frontend

**Nhánh:** `feature/frontend-dashboard`. **Issue đề xuất:** TEAM-05. **PR đích:** `develop`.

## File bắt đầu

- `frontend/index.html`, `styles.css`, `app.js`, `api.js`.
- `frontend/batch.js`, `dashboard.js` dành cho P1; chưa được duyệt thì giữ trống.
- `tests/frontend/test_ui.py` là chỗ viết kiểm thử trình duyệt sau khi leader chốt công cụ.
- Bạn điền: `docs/frontend/ui-notes.md`, `report.md`; ảnh/video thật trong `reports/evidence/frontend/`.

## Làm song song ngay sau M0

1. Xây bố cục, form nhập, nút phân tích và trạng thái loading/error/result theo luồng leader chốt.
2. Viết lớp gọi API theo JSON đã thống nhất; xử lý lỗi input, mất kết nối và model chưa sẵn sàng.
3. Khi API chưa có, có thể dùng fixture/mock riêng để thiết kế và kiểm thử UI. Hiển thị rõ dữ liệu mẫu, không dùng làm minh chứng dự đoán thật hoặc làm fallback kết quả trên bản nghiệm thu.
4. Kiểm tra giao diện/trạng thái và ghi hướng dẫn chạy frontend khi đã triển khai.

## Khi Backend bàn giao API

Kết nối health/predict; xác nhận lỗi và dữ liệu đúng hợp đồng. M4 cần chạy câu mới qua trình duyệt → API → hai model thật, có log/ảnh đối chiếu. Không cần đợi model để bắt đầu dựng giao diện.

## Nghiệm thu

- [ ] Trạng thái nhập/chờ/kết quả/lỗi hoạt động đúng và có kiểm tra trình duyệt.
- [ ] Hai nhãn đến từ API thật; ảnh/video demo tương ứng lần chạy thực tế.
- [ ] P1 nếu được duyệt: UI CSV/export/Dashboard khớp dữ liệu thực tế; không sửa logic API/ML.
- [ ] Hoàn thành hướng dẫn UI và phần báo cáo. Đáp ứng phần UI của AC-03, AC-06 nếu có; [Phase 4](../roadmap/phase-4-mvp.md), [Phase 5](../roadmap/phase-5-batch-dashboard.md).
