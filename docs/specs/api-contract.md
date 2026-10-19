# Hợp đồng API v1.0

**Trạng thái:** Đề xuất duyệt cùng bộ Phase 0. Ví dụ JSON trong tài liệu là hợp đồng minh họa, không phải kết quả mô hình đã chạy. Base demo: `http://127.0.0.1:8000`. Tất cả response thuộc hợp đồng có `contract_version: "1.0"`.

## 1. Bộ nhãn chuỗi

| Task | Giá trị API/pipeline | Hiển thị tiếng Việt |
| --- | --- | --- |
| sentiment | negative | Tiêu cực |
| sentiment | neutral | Trung tính |
| sentiment | positive | Tích cực |
| topic | lecturer | Giảng viên |
| topic | curriculum | Chương trình đào tạo |
| topic | facility | Cơ sở vật chất |
| topic | other | Khác |

Không trả mã số nguồn hoặc confidence. Nhãn ngoài tập trên là lỗi suy luận/không tương thích, không tự sửa thành other. UI dùng bảng này, không tự dịch khác tên field.

## 2. GET /api/health — P0

HTTP 200 khi ứng dụng phục vụ được request, kể cả thiếu model. Không suy luận trong health.

```json
{"status":"ok","ready":false,"models":{"sentiment":"missing","topic":"ready"},"contract_version":"1.0"}
```

`status` cố định `ok`; `models.sentiment`/`models.topic` là ready, missing hoặc invalid. `ready` chỉ true khi cả hai bằng ready. Không đưa đường dẫn local, stack trace hoặc nội dung artifact vào response. Tắt server/mất mạng là lỗi kết nối, không phải một JSON health mới.

Ví dụ cả hai task sẵn sàng:

```json
{"status":"ok","ready":true,"models":{"sentiment":"ready","topic":"ready"},"contract_version":"1.0"}
```

## 3. POST /api/predict — P0

Content-Type `application/json`. Body là object chỉ có field `text`, bắt buộc là string strict; không ép số/null/list thành chuỗi và không chấp nhận field thừa.

```json
{"text":"Giảng viên giảng bài rất dễ hiểu."}
```

Validation theo thứ tự: parse JSON/object và các field → đúng kiểu string → độ dài raw từ 1 đến 5000 Unicode code point (Python `len`) → `text.strip()` không rỗng. Khoảng trắng đầu/cuối không giúp vượt giới hạn: raw 5001 code point vẫn lỗi trước chuẩn hóa. Body hợp lệ mới kiểm tra model readiness rồi suy luận. Backend không viết thường/bỏ dấu/chuẩn hóa lại nội dung, truyền raw string vào hai pipeline.

HTTP 200 khi cả hai nhãn hợp lệ:

```json
{"sentiment":"positive","topic":"lecturer","contract_version":"1.0"}
```

Nếu một task suy luận lỗi, không trả partial result hoặc nhãn của task còn lại. Giữ thứ tự kiểm tra input trước model: input rỗng nhận 422 ngay cả khi model chưa có.

## 4. Error envelope

```json
{"error":{"code":"INVALID_INPUT","message":"Nội dung phản hồi không hợp lệ.","details":[{"field":"text","reason":"blank"}]},"contract_version":"1.0"}
```

| HTTP | error.code | Khi nào | details |
| --- | --- | --- | --- |
| 422 | INVALID_INPUT | JSON/object/field/type/độ dài/khoảng trắng không hợp lệ | Danh sách field/reason |
| 503 | MODEL_NOT_READY | Một hoặc cả hai model chưa ready | Mảng rỗng |
| 500 | INFERENCE_ERROR | Predict ném lỗi hoặc trả nhãn ngoài hợp đồng | Mảng rỗng |
| 500 | INTERNAL_ERROR | Lỗi không dự kiến khác | Mảng rỗng |

Mỗi details item chỉ có `field`, `reason`. `field` là text, tên field thừa hoặc `$body`. Reason là required, type, too_long, blank, extra_field, invalid_json; raw string rỗng dùng blank. Nếu có nhiều lỗi validation, trả danh sách theo field, không chạy model. `message` là thông báo tiếng Việt cho người dùng; UI dựa vào HTTP/code/reason, không so khớp nguyên câu message. Không echo text, thông tin đường dẫn hay stack trace.

Backend bắt lỗi validation của framework và chuyển về envelope trên thay vì để UI phải xử lý thêm schema `detail` mặc định. Endpoint/HTTP method không thuộc hợp đồng có thể dùng 404/405 mặc định của framework; UI không gọi các endpoint đó trong P0.

Ví dụ HTTP 503:

```json
{"error":{"code":"MODEL_NOT_READY","message":"Mô hình chưa sẵn sàng. Vui lòng thử lại sau.","details":[]},"contract_version":"1.0"}
```

Ví dụ HTTP 500 khi suy luận lỗi:

```json
{"error":{"code":"INFERENCE_ERROR","message":"Không thể phân tích phản hồi lúc này.","details":[]},"contract_version":"1.0"}
```

## 5. Frontend và tests

- Gọi `/api/health` khi mở trang và khi người dùng bấm thử lại kết nối; không polling liên tục trong MVP.
- Gọi `/api/predict` khi nút đang cho phép; một request đang xử lý tại một thời điểm trên trang. Timeout client 10000 ms, không tự retry POST.
- Sau 503, cập nhật trạng thái model chưa sẵn sàng; sau lỗi, giữ input và xóa kết quả cũ để không nhầm kết quả của câu khác.
- Các trường hợp bắt buộc: hợp lệ, text thiếu/null/số/list, field thừa, JSON sai, rỗng/khoảng trắng, 5000 và 5001 code point, emoji tính code point, thiếu một/hai model, artifact invalid, predict lỗi và nhãn sai.
- Fixture success/error chỉ là dữ liệu hợp đồng trong tests/UI development, không được dùng như fallback của API thật.

## 6. POST /api/predict-batch — P1 dự phòng

Chưa bật trong P0: không đăng ký route và không hiển thị UI P1. Chỉ làm khi leader cho phép; quy tắc v1.0 dự phòng dưới đây tránh hai phần tự chọn định dạng khác nhau.

- Multipart field `file`, tên kết thúc `.csv` không phân biệt hoa thường; UTF-8 hoặc UTF-8 BOM, không tự đoán encoding khác.
- Tối đa 2097152 byte (2 MiB), 1000 record dữ liệu; record là dòng logic sau parsing CSV, không phải dòng vật lý trong field có xuống dòng. Bỏ qua dòng vật lý trống; record có field rỗng vẫn là record lỗi.
- Có đúng một cột tên `text` (case-sensitive); cột khác được phép nhưng không đưa vào export. CSV rỗng, header lặp, thiếu text, sai quoting/encoding hoặc 0 record: HTTP 400 INVALID_CSV. File/quá số record: HTTP 413 BATCH_LIMIT_EXCEEDED.
- Kiểm tra toàn file/giới hạn trước readiness; file hợp lệ mà thiếu model trả 503. Sau đó xác thực từng text theo cùng giới hạn P0. Dòng input không hợp lệ được giữ ở kết quả, không chạy model cho dòng đó; các dòng hợp lệ được xử lý.
- Nếu có lỗi suy luận model trong batch, trả 500 cho toàn request, không xuất kết quả dở dang. Row input lỗi không phải lỗi suy luận.
- `row_index` là số thứ tự record dữ liệu từ 1; thứ tự response không đổi. Mỗi row có row_index, text, sentiment, topic, error. Row thành công có hai nhãn/error null; row input lỗi có nhãn null/error cùng cấu trúc code/message/details, không có contract_version lồng.
- HTTP 200 gồm `results` (mảng rows), `summary`, `contract_version`. Summary gồm total/succeeded/failed, sentiment_counts và topic_counts, có đủ mọi nhãn kể cả count 0. Các count chỉ tính row thành công; total = succeeded + failed. File chỉ có row lỗi vẫn nhận 200 với succeeded 0.
- Frontend dùng results để xuất CSV UTF-8 BOM với cột row_index,text,sentiment,topic,error_code,error_message; dùng quoting theo CSV, không nối chuỗi bằng dấu phẩy thủ công. Dashboard chỉ hiển thị summary của request vừa thành công. Chưa có endpoint lưu lịch sử/export riêng.

Các lỗi P1 dùng error envelope và mảng details; không phải cam kết P1 được triển khai chỉ vì hợp đồng đã chuẩn bị.
