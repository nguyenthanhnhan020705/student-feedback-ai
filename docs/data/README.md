# TV2 — Data

**Nhánh:** `feature/data-preprocessing`. **Issue đề xuất:** TEAM-01. **PR đích:** `develop`.

## File bắt đầu

- Code trống: `ml/data.py`, `ml/preprocessing.py`, `ml/labels.py`.
- Tests trống: `tests/test_data.py`, `test_preprocessing.py`, `test_labels.py`.
- Notebook rỗng: `notebooks/01_eda.ipynb`.
- Bạn điền: `docs/data/dataset.md`, `preprocessing.md`, `report.md`, `requirements/data.txt`.
- Nơi lưu kết quả thật: `reports/data/`, `reports/evidence/data/`; dataset local trong `data/raw/` và `data/processed/`.

## Làm ngay

1. Xác minh nguồn UIT-VSFC, quyền sử dụng, phiên bản, bảng nhãn và split; ghi nguồn trong `dataset.md`.
2. Theo hợp đồng leader chốt, viết loader, chuẩn hóa Unicode/khoảng trắng và bảng nhãn; tests cho rỗng, lệch dòng, nhãn lạ và giữ phủ định.
3. Kiểm tra số dòng, trùng lặp trong/giữa split và các nguy cơ rò rỉ dữ liệu; ghi chính sách xử lý.

## Bàn giao M1 sớm

Mở PR nhỏ với nguồn đã xác minh, schema, bảng nhãn, loader/chuẩn hóa có tests và manifest split. Sau khi leader duyệt, Sentiment/Topic nhận Data từ `develop` và có thể train thật. Bạn tiếp tục EDA, biểu đồ và báo cáo; không cần đợi toàn bộ EDA xong mới bàn giao M1.

## Hoàn thiện và nghiệm thu

- [ ] Dataset được kiểm đếm và đối chiếu nguồn thực tế, không chép số tham khảo thành số đo.
- [ ] EDA và biểu đồ phân bố nhãn/độ dài, phát hiện rỗng/trùng/mất cân bằng.
- [ ] Tests Data/chuẩn hóa/nhãn thực sự chạy đạt; ghi lệnh và log.
- [ ] Viết hướng dẫn tái lập và phần báo cáo Data. Đáp ứng AC-01, [Phase 2](../roadmap/phase-2-data.md).

Không sửa code mô hình/API/UI. Không công bố dataset chưa rõ quyền sử dụng. Thay đổi giao diện loader/nhãn/chuẩn hóa phải được leader duyệt và báo các phần dùng Data.
