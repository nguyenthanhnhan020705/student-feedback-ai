# CT1 — Quy trình đánh giá cải tiến

CT1 chuẩn bị phép đo cho CT2–CT5. Hoàn thành CT1 không có nghĩa chất lượng model
đã tăng. Baseline vẫn là hai Linear SVM đang chạy. Phase 6 tiếp tục chưa triển khai.

## Phân vai dữ liệu

| Nguồn | Vai trò | Được dùng chọn cấu hình? |
| --- | --- | --- |
| UIT-VSFC train, 11426 dòng | Huấn luyện ở CT sau | Có, chỉ fit trên train |
| UIT-VSFC validation, 1583 dòng | So sánh/điều chỉnh cấu hình | Có; điểm có thể lạc quan do thử nhiều lần |
| UIT-VSFC test, 3166 dòng | Kết quả lịch sử đã xem nhiều lần | Không; không gọi là tập mù mới |
| 39 câu đã chẩn đoán | Kiểm tra lỗi đã biết, nhóm tình huống | Chỉ kiểm hồi quy/chẩn đoán; không coi là phép đo độc lập |
| Bộ câu mới cuối kỳ | Đánh giá cuối sau khi đóng băng cấu hình | Không dùng để chọn/điều chỉnh |

## Nhãn và cách chấm

Sentiment: negative, neutral, positive. Topic: lecturer, curriculum, facility, other.
Giữ một nhãn/task theo hợp đồng 1.0. Chuẩn hóa chỉ trong pipeline.

Metrics validation mỗi task: Accuracy, Macro Precision/Recall/F1, Precision/Recall/F1
từng lớp, support và confusion matrix theo thứ tự canonical. Có thêm tỷ lệ cả hai
task cùng đúng trên một câu; không gộp hai Accuracy thành một điểm trung bình.

39 câu do trợ lý gợi ý trước đây đã lộ và đã được xem kết quả. Nhãn kỳ vọng mới
được ghi là assistant_proposed, chưa được người dùng/nhóm rà soát. Điểm trên bộ
này là exploratory, không phải ground truth học thuật đã xác nhận. Null nghĩa
chưa có một nhãn đủ căn cứ: không tính vào mẫu số của task đó. Câu ngoài miền,
vô nghĩa, emoji đơn lẻ, câu đa chủ đề/cảm xúc vẫn lưu đầu ra để khảo sát, không
ép thành neutral/other. Nhóm có ít mẫu chỉ dùng để thấy lỗi, không suy rộng.

## Quy tắc chọn ứng viên cho CT2–CT4

- So từng task với baseline và bản tốt nhất trước đó trên cùng validation.
- Xếp theo Macro F1; hòa trong 1e-6 thì Accuracy, còn hòa giữ bản đơn giản hơn/
  baseline để không thêm độ phức tạp khi chưa có lợi ích.
- Bắt buộc báo delta Accuracy, Macro F1 và từng lớp; đặc biệt neutral/other.
- Không tự thay model chỉ vì điểm xếp hạng cao hơn. Mọi giảm Precision/Recall/F1
  của lớp khác, giảm Accuracy hoặc ca đã đúng thành sai phải xuất hiện trong
  biên bản để cân nhắc. Không tự đặt một ngưỡng chất lượng cam kết với giảng viên.
- Chỉ đưa vào demo sau kiểm tương thích metadata/API/UI và quyết định chọn bản.
  Mỗi run lưu cấu hình, phiên bản, hash, seed, thời gian, nguồn dữ liệu bổ sung.
- Chỉ fit dữ liệu bổ sung sau chia nhóm; biến thể có dấu/không dấu/paraphrase của
  cùng câu phải ở cùng nhóm. Không đưa câu đánh giá cuối hoặc bản gần trùng vào train.

CT5 phải báo riêng coverage (tỷ lệ nhận trả lời), chất lượng trên câu được nhận,
và lỗi từ chối nhầm/chấp nhận nhầm. Từ chối không đồng nghĩa với dự đoán đúng.
Điểm margin SVM không phải xác suất confidence; ngưỡng cần chọn trên development.

## Bộ đánh giá mới độc lập — đầu vào còn cần bổ sung

Chưa có tập mù mới đã gán nhãn độc lập. Không lấy một phần test cũ để gọi là mới.
Trước CT5, nhóm/người đánh giá khác thu phản hồi mới được phép dùng, không xem
đầu ra model khi gán nhãn; hai người rà và giải quyết bất đồng, lưu nguồn và
định nghĩa nhãn. Có tập phản hồi tự nhiên để đo chất lượng, thêm challenge set
riêng cho phủ định/không dấu/emoji; không trộn tỷ lệ nhân tạo rồi gọi là phân bố thật.

Đề xuất tối thiểu thực dụng cho tập tự nhiên: 200 câu, cố gắng có ít nhất 30 mẫu
mỗi lớp ít gặp ở mỗi task; đây là đề xuất thu thập, không phải bằng chứng đủ
độ tin cậy thống kê. Báo support/độ bất định khi kết luận. Nếu cần lấy mẫu thêm
theo lớp, báo điểm phân tầng riêng với điểm trên mẫu tự nhiên.

Lưu ngoài dữ liệu phát triển, người giữ tập đóng băng SHA-256 trước khi mở kết
quả. Kiểm exact normalized overlap và rà near-duplicate với corpus/known cases.
Chỉ mở sau khi chốt cấu hình. Nếu sửa theo kết quả đó, tập đã thành development;
cần tập độc lập khác để tuyên bố đánh giá cuối. CT1 không bịa tên người rà hoặc
khẳng định đã có tập dữ liệu này.

## Cách chạy và bảo toàn baseline

```powershell
./.venv/Scripts/python.exe reports/ct_evaluation.py freeze
./.venv/Scripts/python.exe reports/ct_evaluation.py verify
```

freeze chỉ chạy một lần, từ chối output đã tồn tại. Snapshot artifact local ở
.local-tools/ct1-baseline-v2; bằng chứng ở reports/evidence/ct1/baseline-v2. verify
kiểm hash và chạy lại snapshot trên validation/known cases, so kết quả chính xác.
Tool không có tùy chọn đánh giá test hoặc fit. Dùng --output và --snapshot khác
nếu cần một mốc mới; không ghi đè baseline cũ. Snapshot không phải bản backup
toàn bộ môi trường; cần giữ runtime lock và code đi kèm.
