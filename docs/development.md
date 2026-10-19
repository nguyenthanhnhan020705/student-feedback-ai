# Môi trường phát triển và trạng thái khung

**Hiện tại:** file code, tests và requirements được để trống có chủ đích. Chưa có ứng dụng FastAPI, giao diện hay mô hình chạy được. Notebook là notebook rỗng hợp lệ. Chưa kiểm chứng phiên bản Python/dependencies cho bản triển khai mới.

## Leader chuẩn bị trước khi chạy

1. Chốt Python, giao diện module và cách phục vụ frontend trong [đặc tả](specs/README.md).
2. Nhận đề xuất dependencies từ `requirements/data.txt`, `sentiment.txt`, `topic.txt`, `backend.txt`; tổng hợp và khóa phiên bản chung khi đã kiểm tra tương thích.
3. Hoàn thiện `requirements.txt`, `requirements-test.txt`, `requirements-browser.txt`, `pytest.ini`, `.env.example` và `ml/__init__.py` theo nhu cầu thực tế. Không coi file trống là cấu hình hoàn chỉnh.
4. Ghi lệnh tạo môi trường, cài đặt, train, evaluate, chạy API/UI và tests sau khi đã chạy thành công. File này là nơi leader duy trì hướng dẫn dùng chung.

## Thành viên làm việc độc lập

- Đọc hướng dẫn của vai trò trong [phân công](team-assignments.md).
- Viết kiểm thử cho giao diện được chốt rồi triển khai phần của mình. Fixture nhỏ chỉ phục vụ kiểm thử; không thay thế dữ liệu nghiên cứu hay kết quả mô hình thật.
- Các lệnh pytest trong roadmap là lệnh mục tiêu sau khi tests được viết. Với file test trống, pytest có thể báo không thu thập được bài nào; đó không phải kết quả kiểm thử đạt.
- Cài dependencies sau khi leader công bố môi trường chung; không sửa requirements gốc từ nhánh chức năng khác.

## Dữ liệu và artifact

- `data/raw/` và `data/processed/` chỉ có `.gitkeep`; dữ liệu tải thật được ignore. Data ghi nguồn/quyền sử dụng và cách tái lập trong `docs/data/dataset.md`.
- `models/` có hướng dẫn và `.gitkeep`; chưa có `.joblib` hoặc metadata của mô hình thật.
- Metrics, biểu đồ và log nghiệm thu chỉ được thêm khi sinh ra từ lần chạy có cấu hình và dữ liệu đối chiếu được.
- Đọc [hướng dẫn model](../models/README.md), [notebook](../notebooks/README.md), [kiểm thử](../tests/README.md) và [báo cáo](../reports/README.md).
