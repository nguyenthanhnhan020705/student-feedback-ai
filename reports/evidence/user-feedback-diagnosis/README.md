# Kiểm tra phản hồi khi demo — 2026-10-31

Phạm vi: tái hiện và chẩn đoán các câu người dùng báo. Không thực hiện Phase 6,
không train lại, không thay mã ứng dụng, model hoặc hợp đồng API.

Lệnh đã chạy trong bản tích hợp:

```powershell
$env:PYTHONIOENCODING='utf-8'
./.venv/Scripts/python.exe -u reports/diagnose_user_examples.py
```

Yêu cầu server thật đang chạy tại 127.0.0.1:8000. Lệnh hoàn tất exit 0.
Script chỉ bổ sung bằng chứng chẩn đoán, không phải bộ kiểm chứng chất lượng mới.

## Kết quả

- 39 câu tự viết: API HTTP thật khớp model trực tiếp ở cả hai nhãn.
- 6 trường hợp kiểm trên Chrome thật, không mock: UI hiển thị đúng nhãn API,
  gồm neutral/other và các dự đoán sai nghĩa. Xem browser.json.
- Kiểm lại test split 3166 dòng: sentiment dự đoán neutral 49 lần, nhận đúng
  30/167 mẫu neutral (Recall 17,96%); topic dự đoán other 82 lần, nhận đúng
  49/159 mẫu other (Recall 30,82%). Không dùng các điểm test để chọn model mới.
- Hash các file model/metadata trước và sau không đổi. Xem results.json.

## Nguyên nhân và phạm vi kết luận

1. Không thiếu nhãn neutral/other trong artifact hoặc UI. Hai lớp yếu; số mẫu
   train lần lượt 458/11426 và 562/11426. Mất cân bằng là yếu tố cần khảo sát,
   chưa chứng minh là nguyên nhân duy nhất.
2. Hai câu phủ định đã tái hiện sai. Pipeline từ/ngữ đoạn tuyến tính hiện tại
   không bảo đảm hiểu phạm vi phủ định; không có bước xử lý ngữ nghĩa riêng.
3. Câu không dấu chỉ có 3 đặc trưng khác 0, câu có dấu tương ứng có 18;
   kết quả đổi từ positive thành negative. Pipeline không khôi phục dấu.
4. Câu sạch đẹp không emoji, thêm 😍 và thêm 😡 tạo vector hoàn toàn giống nhau
   ở cả hai task. Emoji bị token pattern bỏ qua. Cả ba đều bị đoán negative:
   lỗi câu này tồn tại cả khi không có emoji.
5. abcxyz qwerty 123456 tạo vector 0. Decision scores bằng đúng intercept của
   classifier; negative/lecturer là kết quả chọn điểm cao nhất khi không có
   đặc trưng, không phải hiểu nghĩa. Emoji đơn lẻ cũng tạo vector 0.
6. Tốt. chỉ có một đặc trưng; topic vẫn buộc chọn lecturer. Chưa có cơ chế
   từ chối suy luận khi thiếu thông tin về chủ đề.
7. Câu món phở chỉ có 4 đặc trưng được biết, vẫn bị ép vào các nhãn hiện có.
   other là một lớp học từ corpus, không phải bộ phát hiện ngoài miền.
8. Hai cảm xúc/chủ đề chỉ có một kết quả vì đặc tả và schema hiện tại yêu cầu
   một nhãn/task. Muốn thể hiện từng vế cần thay thiết kế và đánh giá riêng.

## Câu đối chiếu đã kiểm chứng

| Câu | Kết quả thật |
| --- | --- |
| Không có ý kiến. | neutral / other |
| Em không có ý kiến gì. | neutral / other |
| Không có góp ý. | neutral / other |
| Bình thường. | neutral / other |
| Các hoạt động ngoại khóa rất bổ ích. | positive / other |

Các câu trên chỉ chứng minh nhãn có thể xuất hiện, không chứng minh model đã
khắc phục lỗi hoặc tổng quát tốt. Bộ ví dụ trước của trợ lý là nhãn kỳ vọng
theo nội dung, không phải các đầu ra model đã xác minh.

## Việc cần quyết định trước khi cải tiến

- Bổ sung hành vi thiếu thông tin/ngoài phạm vi cần định nghĩa rõ cho API/UI;
  không đồng nhất không chắc chắn với neutral hoặc other.
- Cải tiến neutral/other, phủ định, không dấu và emoji cần thí nghiệm riêng,
  bảo toàn baseline, chọn bằng validation và tập đánh giá độc lập; không vá
  nhãn theo riêng 39 câu này hoặc tối ưu từ test hiện tại.
- Đa cảm xúc/đa chủ đề là thay đổi khỏi hợp đồng một nhãn/task.

224 tests vận hành trước đây không chứng minh hiểu đúng mọi câu mới. Kết quả
chẩn đoán này bổ sung giới hạn nghiệm thu, chưa phải một bản sửa để test lại.
