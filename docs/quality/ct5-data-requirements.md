# CT5 — Đầu vào đánh giá độc lập còn chờ

Mốc A hoàn tất kỹ thuật không đồng nghĩa đã nghiệm thu khả năng từ chối câu
ngoài miền. UIT-VSFC validation đã lộ qua CT1–CT4; hai subset theo hash trong
CT5 vẫn là development. Test cũ cũng đã lộ, không trở thành final mới khi chia lại.

Hiện chưa có bộ phản hồi mới được hai người rà độc lập, chưa có nhãn
answerability được xác nhận, chưa có người giữ final và quyết định coverage/risk.
Không dùng nhãn `other` thay cho outside-domain hoặc `neutral` thay cho uncertainty.
Không lấy model đoán sai làm ground truth “unanswerable”.

## Thu và gán nhãn

Nhóm cần thu phản hồi tự nhiên được phép dùng; ghi nguồn và quyền sử dụng.
Khoảng 200 câu tự nhiên, cố gắng có 30 mẫu mỗi lớp ít gặp, là đề xuất thực dụng
của CT1, không bảo đảm đủ lực thống kê. Tách challenge ngoài miền/emoji/phủ định/
không dấu/mơ hồ khỏi mẫu tự nhiên; không trộn tỷ lệ nhân tạo để gọi là traffic thật.

Hai người rà không xem model outputs; thống nhất ontology và giải quyết bất đồng.
Mỗi record cần `id`, `text`, `source`, `source_group`, hai nhãn kỳ vọng
`sentiment`/`topic` (có thể null), `answerability` riêng từng task
(`answerable|unanswerable|ambiguous`), lý do, reviewer provenance thật và quyết
định sau phân xử. Không tự tạo tên người rà. Fixture tests chỉ chứng minh tính toán.

Tách development mới và final theo source groups; cùng câu gốc/biến thể không
cắt sang hai phía. Kiểm exact normalized và near-duplicate với train/validation/
test cũ, known cases, stress và CT4 augmentation. Người giữ final đóng băng
text/nhãn/hash trước khi chạy; chỉ mở sau khi chốt policy/config. Nếu chỉnh
policy theo final thì tập đó trở thành development và cần final khác.

## Chỉ số cần nghiệm thu khi có dữ liệu

- Coverage và accepted accuracy/selective risk cùng IDs; C/N là số trả đúng
  trên tất cả input có đủ ground truth, không tính rejected thành đúng.
- False reject = rejected answerable / tất cả answerable.
- Unsafe accept = accepted unanswerable / tất cả unanswerable.
- Precision of abstention = rejected unanswerable / rejected có nhãn rõ.
- Accuracy trên accepted answerable, riêng mỗi task và cả cặp; ambiguous và
  missing báo riêng, mẫu số 0 trả null. Báo support và độ bất định khi có mẫu mới.

`rejected_correct` trên validation chỉ là câu classifier thô đoán đúng mà gate
bỏ đi; không thay thế false reject về ngữ nghĩa. Bộ known hiện có nhãn
assistant_proposed, chưa human-reviewed; chỉ chẩn đoán. Synthetic stress kế thừa
nhãn, không độc lập; sáu overlap sau bỏ dấu với train đã biết cần được nêu rõ.

Trạng thái: `engineering_complete_independent_evaluation_pending`;
`recommended_policy=null`, `needs_coverage_risk_decision`. Người dùng chọn mức
đánh đổi sau khi xem bảng; chưa có policy triển khai hoặc chứng nhận ngoài miền.
