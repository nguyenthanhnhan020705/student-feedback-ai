# Phase 5 — CSV và Dashboard (P1, tùy chọn)

**Trạng thái:** Chưa bắt đầu — tùy chọn.  
**Thời gian:** Ngày 15–17, chỉ khi đủ thời gian.  
**Phụ trách:** TV5, TV6; TV1 kiểm soát phạm vi.  
**Phụ thuộc:** Phase 4 đạt; bảo đảm thời gian bàn giao Phase 6.  
**Quay lại:** [Lộ trình](README.md).

File P1 đã được dành chỗ trong [manifest](../scaffold-manifest.json) nhưng vẫn trống. Backend sở hữu xử lý CSV/export và dữ liệu thống kê; Frontend sở hữu UI/biểu đồ. Chỉ triển khai sau khi leader cho phép, không coi sự tồn tại file là đã cam kết P1.

## Mục tiêu

Phân tích CSV có cột `text`, xuất kết quả và xem phân bố nhãn của tập vừa phân tích. Đáp ứng BR-04, FR-03/04, AC-05/06. Nếu bỏ qua phase này, ghi rõ P1 chưa triển khai trong báo cáo.

## Công việc

- [ ] P5.1: Trước khi code, chốt encoding CSV, giới hạn file/số dòng, quy tắc dòng rỗng/lỗi, thứ tự dòng và định dạng xuất vào hợp đồng API.
- [ ] P5.2: Viết kiểm thử rồi triển khai đọc/kiểm tra CSV và `POST /api/predict-batch`, tái sử dụng dịch vụ mô hình Phase 4.
- [ ] P5.3: Giữ khả năng đối chiếu từng dòng đầu vào với kết quả; nếu chấp nhận một phần file, ghi rõ dòng lỗi và cách tính tổng.
- [ ] P5.4: Bổ sung UI tải file, xem kết quả và tải xuống CSV có nhãn; xử lý lỗi đúng hợp đồng.
- [ ] P5.5: Tính số lượng và phân bố sentiment/topic từ kết quả vừa trả; hiển thị Dashboard nhất quán với bảng.
- [ ] P5.6: Kiểm tra file rỗng, thiếu cột, tiếng Việt, dấu phẩy/dấu ngoặc kép trong câu, vượt giới hạn và trạng thái thiếu model.

## Sản phẩm dự kiến

| File | Trách nhiệm |
| --- | --- |
| `backend/batch_service.py`, `backend/routes/batch.py` | Kiểm tra CSV, suy luận và xuất kết quả |
| `frontend/batch.js`, `frontend/dashboard.js` | Tải file, bảng kết quả và thống kê |
| `tests/test_batch.py`, `tests/test_dashboard_data.py` | Lỗi CSV, đối chiếu số dòng và tổng số nhãn |
| `reports/evidence/backend/`, `reports/evidence/frontend/` | Minh chứng P1 theo đúng chủ sở hữu |

## Điều kiện hoàn thành và kiểm chứng

- Lệnh dự kiến `python -m pytest tests/test_batch.py tests/test_dashboard_data.py -q` chạy đạt.
- Với file hợp lệ, số dòng và thứ tự kết quả khớp đầu vào; file có dòng lỗi tuân theo chính sách đã chốt ở P5.1.
- Tổng số nhãn trong Dashboard khớp số dòng dự đoán thành công; không tính dòng lỗi thành một nhãn.
- Chạy demo thật từ tải CSV đến xuất file; kiểm tra lại luồng một câu Phase 4 để tránh hồi quy.

Bàn giao minh chứng cho Phase 6. Nếu không đủ thời gian hoàn thiện, bỏ phase này khỏi phạm vi demo cam kết và ghi trạng thái thực tế.
