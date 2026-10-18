# Phase 2 — Dữ liệu và tiền xử lý

**Trạng thái:** Chưa bắt đầu.  
**Thời gian:** Ngày 3–6; có thể xác minh nguồn sau Phase 0.  
**Phụ trách:** TV2; TV3, TV4 đối chiếu nhãn và đầu vào mô hình.  
**Phụ thuộc:** Hợp đồng Phase 0 và môi trường Phase 1 để chạy xử lý.  
**Quay lại:** [Lộ trình](README.md).

## Mục tiêu

Cung cấp dữ liệu được xác minh, EDA và tiền xử lý dùng chung, đáp ứng DR-01–03, RULE-01/03, AC-01. Không suy diễn mã nhãn từ ví dụ trong BRD.

## Công việc

- [ ] P2.1: Xác minh nguồn UIT-VSFC, quyền sử dụng/phân phối, phiên bản và cách tải; ghi lại dấu nhận diện dữ liệu sử dụng.
- [ ] P2.2: Viết kiểm thử đọc dữ liệu và triển khai loader; kiểm tra số dòng, số nhãn, dòng rỗng, nhãn lạ và độ khớp giữa văn bản/nhãn.
- [ ] P2.3: Đối chiếu bảng mã sentiment/topic với nguồn; cập nhật hợp đồng dữ liệu cho TV3–TV6.
- [ ] P2.4: Thực hiện EDA: phân bố từng nhãn, độ dài văn bản, trùng lặp trong và giữa các split; ghi cách xử lý, không tự thay đổi split nghiên cứu.
- [ ] P2.5: Viết kiểm thử rồi triển khai chuẩn hóa Unicode/khoảng trắng; giữ thông tin phủ định và sắc thái cảm xúc, ghi rõ mọi phép biến đổi.
- [ ] P2.6: Lưu manifest split và thống kê trước/sau xử lý; kiểm tra tiền xử lý cho train và suy luận dùng cùng một hàm.

## Sản phẩm dự kiến

| File | Trách nhiệm |
| --- | --- |
| `ml/data.py` | Đọc và kiểm tra cấu trúc dữ liệu |
| `ml/preprocessing.py` | Chuẩn hóa văn bản dùng chung |
| `notebooks/01_eda.ipynb` | Phân tích khám phá và biểu đồ |
| `docs/data/dataset.md` | Nguồn, quyền sử dụng, phiên bản, bảng mã và chính sách split |
| `reports/data/manifest.json` | Số lượng, định danh dữ liệu và thông tin kiểm tra |
| `tests/test_data.py`, `tests/test_preprocessing.py` | Kiểm thử loader và chuẩn hóa |

## Điều kiện hoàn thành và kiểm chứng

- Đạt AC-01 với notebook/biểu đồ và nguồn dữ liệu có thể đối chiếu; số lượng ghi theo bản thực tế, không chép số tham khảo thành kết quả.
- Lệnh dự kiến `python -m pytest tests/test_data.py tests/test_preprocessing.py -q` chạy đạt.
- Kiểm thử bao gồm văn bản tiếng Việt tổ hợp Unicode, khoảng trắng, phủ định, dữ liệu rỗng, nhãn không hợp lệ và lệch số dòng.
- Các nguy cơ trùng lặp giữa train/validation/test có kết luận và cách xử lý được ghi nhận trước huấn luyện.
- Không có bước học tham số hoặc `fit` trên validation/test.

Bàn giao loader, hợp đồng nhãn, tiền xử lý và manifest cho Phase 3. Nếu không xác minh được nguồn/quyền sử dụng, ghi phase bị chặn và xử lý nguồn dữ liệu trước khi huấn luyện.
