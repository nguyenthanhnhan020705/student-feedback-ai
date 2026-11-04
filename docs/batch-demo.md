# Demo phân tích danh sách

Chạy từ bản tích hợp `.local-tools/integration-p0`:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-batch.txt
.\.venv\Scripts\python.exe -m uvicorn demo_v3.main:app --host 127.0.0.1 --port 8002
```

Mở http://127.0.0.1:8002/. Ô phân tích riêng vẫn hoạt động; mục danh sách nằm phía dưới.

1. Nhập tên đợt. Dán mỗi phản hồi trên một dòng hoặc chọn CSV UTF-8/Excel .xlsx. Với file, chọn trang tính, cột nội dung và cột mã tùy chọn.
2. Xem trước. Hàng đầu có dữ liệu là tiêu đề file. Một ô nhiều câu/nhiều dòng vẫn là một phản hồi. Mã và số dòng nguồn được giữ; mã tự tạo khi không chọn cột mã. Các mã quá 100 ký tự được rút ngắn khi nhập.
3. Bấm phân tích. Tối đa 500 phản hồi/đợt, 5000 ký tự Unicode/phản hồi. Dòng trống/quá dài được ghi không hợp lệ. Không xóa phản hồi trùng. Một dòng lỗi không chặn dòng tiếp theo; bấm phân tích lần nữa để thử lại dòng lỗi/chưa xử lý. Có thể dừng sau dòng hiện tại.
4. Lọc/tìm kiếm trong bảng. Nội dung đầy đủ có thể cuộn. Biểu đồ luôn thống kê cả đợt trên mẫu số các phản hồi thành công; một phản hồi có thể tính ở nhiều chủ đề.
5. Xuất Excel gồm Tổng quan, Chi tiết, Theo chủ đề. File xuất chứa toàn bộ đợt, kể cả dòng lỗi/chưa chạy, không bị ảnh hưởng bởi bộ lọc. Nội dung bắt đầu bằng dấu bằng được lưu dạng văn bản; ký tự XML không hỗ trợ được biểu diễn bằng mã Unicode.

Giới hạn nhập file: 5 MiB, tối đa 10 trang tính, 100 cột; Excel giải nén tối đa 25 MiB. Mỗi trang tính tối đa 500 hàng sau tiêu đề. Một ô tối đa 20000 ký tự để xem trước; nội dung trên 5000 ký tự không được phân tích.

Phiên được giữ trong bộ nhớ trang; tải lại/đóng sẽ mất danh sách. Không có tài khoản/cơ sở dữ liệu. Cần tải Excel trước khi đóng.

## Phương pháp và phạm vi đã kiểm chứng

Nhãn Hỗn hợp là có cả ý tích cực và tiêu cực. Bộ luật hiện tại quyết định nhãn; CT4 dùng đối chiếu nội bộ. Chưa huấn luyện lại hoặc có tập đánh giá độc lập cho chức năng mới.

Cảm xúc theo chủ đề chỉ tổng hợp từ mệnh đề có đúng một chủ đề rõ ràng. Mệnh đề đồng thời có nhiều chủ đề hoặc chủ ngữ ngầm không được tự gán cảm xúc cho từng chủ đề. Ví dụ `Giảng viên nhiệt tình nhưng phòng học nóng.` cho Giảng viên=Tích cực, Cơ sở vật chất=Tiêu cực. Không suy ra cảm xúc từ mệnh đề thiếu đối tượng; các câu phức tạp vẫn có thể sai.

Kiểm thử: tests/test_batch_v3.py, tests/test_demo_v3.py, tests/test_demo_v3_api.py; kiểm thử Chrome thật tests/test_batch_browser.py cần server 8002 đang chạy.
