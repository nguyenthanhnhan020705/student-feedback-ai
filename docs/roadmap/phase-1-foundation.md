# Phase 1 — Nền tảng dự án

**Trạng thái:** Đã có khung file trống; chưa triển khai hoặc nghiệm thu nền tảng.  
**Thời gian:** Ngày 2–3.  
**Phụ trách:** TV5, TV6; TV1 rà soát tích hợp.  
**Phụ thuộc:** Phase 0 đã thống nhất đặc tả.  
**Quay lại:** [Lộ trình](README.md).

Theo [quyền sở hữu file](../function-ownership.md): leader cập nhật cấu hình/dependencies gốc, TV5 chỉ triển khai Backend, TV6 chỉ triển khai Frontend. File code/tests/requirements hiện trống. Cả Data, Sentiment và Topic cũng có thể chuẩn bị code/tests theo M0 trong thời gian này; chưa cần chờ toàn bộ nền tảng API/UI hoàn thành.

## Mục tiêu

Có môi trường phát triển tái lập được, ứng dụng khởi động được khi chưa có model và hệ thống kiểm thử cơ bản. Đáp ứng phần nền tảng của FR-06, NFR-02–04 và AC-07.

## Công việc

- [ ] P1.1: Xác minh phiên bản Python và bộ dependencies tương thích; lưu cấu hình môi trường và hướng dẫn cài đặt thực tế.
- [x] P1.2: Tạo cấu trúc và file khởi đầu trống theo [manifest](../scaffold-manifest.json); `.gitignore` giữ dataset/model local và cho phép `.gitkeep`. Đây chỉ là bước chuẩn bị, không phải nghiệm thu Phase 1.
- [ ] P1.3: Viết kiểm thử health khi chưa có artifact; triển khai khung FastAPI và trạng thái sẵn sàng theo hợp đồng Phase 0.
- [ ] P1.4: Tạo giao diện nhập phản hồi và vùng thông báo trạng thái; kết nối tới health, biểu thị đúng khi chưa có mô hình.
- [ ] P1.5: Cấu hình pytest, đường dẫn artifact và phục vụ frontend theo quyết định Phase 0; bổ sung hướng dẫn khởi động.
- [ ] P1.6: Chạy kiểm tra từ môi trường mới; lưu lệnh và kết quả thật.

## Sản phẩm dự kiến

| File | Trách nhiệm |
| --- | --- |
| `backend/main.py`, `backend/config.py` | Khởi tạo ứng dụng, health và cấu hình |
| `frontend/index.html`, `frontend/styles.css`, `frontend/app.js` | Khung giao diện và trạng thái dịch vụ |
| `requirements.txt`, `requirements-test.txt`, `pytest.ini` | Dependencies và cấu hình kiểm thử |
| `tests/test_health.py` | Hành vi khởi động và health khi chưa có model |
| `docs/development.md` | Cách cài đặt, chạy và kiểm thử đã xác minh |

## Điều kiện hoàn thành và kiểm chứng

- Cài đặt theo tài liệu trên môi trường mới và khởi động backend thành công.
- Lệnh dự kiến `python -m pytest tests/test_health.py -q` chạy đạt; cập nhật lệnh nếu cấu trúc thực tế thay đổi.
- Health phân biệt ứng dụng đang chạy và mô hình sẵn sàng; giao diện không hiển thị dự đoán giả.
- Rà soát file đưa vào Git, bảo đảm không chứa `.env`, thông tin cá nhân hoặc dataset/model chưa được phép phân phối.

Đầu ra môi trường chuyển sang Phase 2–3; khung API/UI chuyển sang Phase 4. Ghi bằng chứng khi thực hiện, không đánh dấu hoàn thành chỉ từ việc tạo thư mục.
