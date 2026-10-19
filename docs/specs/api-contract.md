# Hợp đồng API — mẫu chờ leader chốt

**Trạng thái:** Chưa phê duyệt; không suy diễn schema từ file trống.

## GET /api/health

Leader chốt JSON và HTTP status cho dịch vụ đang chạy, đủ/thiếu/hỏng một hoặc cả hai model. Phân biệt tình trạng dịch vụ với mức sẵn sàng suy luận.

## POST /api/predict

Theo BRD, yêu cầu có trường `text`. Leader chốt kiểu/giới hạn, cách xử lý khoảng trắng, JSON hai nhãn sentiment/topic, bảng giá trị và HTTP status. Bổ sung ví dụ request/response hợp lệ và các lỗi rỗng/sai kiểu/vượt giới hạn/model chưa sẵn sàng.

## CSV — P1

Trước khi triển khai P1, chốt `/api/predict-batch`, encoding/cột `text`, giới hạn file/dòng, quy tắc dòng lỗi, giữ thứ tự, định dạng export và thống kê Dashboard. P1 chưa chốt không chặn P0.

## Tích hợp UI

Chốt origin/CORS nếu cần, cách Frontend cấu hình địa chỉ API và hiển thị lỗi. Dữ liệu mock chỉ dành phát triển/tests, không thay phản hồi thật của API khi thiếu model.
