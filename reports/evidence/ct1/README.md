# CT1 — Mốc đánh giá đã thiết lập, 2026-10-31

CT1 hoàn thành phần công cụ, bảo toàn baseline và quy trình. Chất lượng model
chưa được cải tiến; CT2–CT5 và Phase 6 chưa triển khai.

## Mốc chính thức

**baseline-v2/** và **.local-tools/ct1-baseline-v2/** là mốc CT1 cuối.
baseline/ và snapshot ct1-baseline đầu tiên được giữ nguyên để truy vết lần
review; không dùng công cụ bản đó cho các CT sau. Model/điểm số hai bản giống
nhau; v2 bổ sung kiểm tra độ dài đầu ra known cases trước khi chấm.

| Validation 1583 câu | Accuracy | Macro F1 | Recall lớp ít mẫu | F1 lớp ít mẫu |
| --- | --- | --- | --- | --- |
| Sentiment | 91,47% | 75,30% | neutral 27,40% | neutral 39,60% |
| Topic | 88,00% | 75,42% | other 29,47% | other 41,18% |

Hai nhãn cùng đúng: 1296/1583 = 81,87%. Không nhầm với điểm test lịch sử
89,70%/70,51% sentiment và 86,17%/73,54% topic (Accuracy/Macro F1).
Metrics validation khớp chính xác comparison.json gốc; không fit/reselect.

## Bộ ca đã biết

39 câu, 20 nhóm tình huống. Nhãn do trợ lý đề xuất, chưa có người rà độc lập.
Null loại khỏi mẫu số của task; vẫn lưu dự đoán thực tế và nhóm để theo dõi.

- Sentiment: đúng 21/30 ca có kỳ vọng một nhãn, 9 ca chưa chấm.
- Topic: đúng 29/29 ca có kỳ vọng một nhãn, 10 ca chưa chấm.
- Cả hai: đúng 18/25 ca có kỳ vọng đủ hai nhãn, 14 ca chưa chấm.

29/29 không có nghĩa model chủ đề đạt 100% chất lượng: các câu thiếu ngữ cảnh,
ngoài miền/đa chủ đề chưa được chấm bằng schema một nhãn. Xem toàn bộ rows và
groups trong baseline-v2/baseline.json, không chỉ tổng điểm. Các ca chưa chấm
chính là những tình huống cần thiết kế hành vi ở CT5.

## Kiểm chứng thực tế

```powershell
$env:TV2_RUN_REAL_DATA='1'
./.venv/Scripts/python.exe -m pytest tests/test_ct_evaluation.py tests/test_labels.py tests/test_preprocessing.py tests/test_data.py -q -p no:cacheprovider
./.venv/Scripts/python.exe reports/ct_evaluation.py verify
./.venv/Scripts/python.exe -m pip check
```

- tests.txt: 38 passed, 0 skipped, 8,36 giây; gồm 13 tests CT1 và real-data tests.
- replay.txt: replay snapshot thật, 49 hash và 39 câu; metrics/predictions khớp.
- pip check: No broken requirements found.
- RED trước triển khai: import module đánh giá chưa tồn tại. GREEN: 11 tests.
- Review phát hiện thừa/thiếu số lượng case predictions: RED 2 tests, sửa
  kiểm length/labels trước ghép rows; GREEN suite cuối 38 tests.
- Cả hai artifact và metadata vẫn khớp hash từ lần chẩn đoán trước CT1.
- 47 đầu vào app/ML/data/lock/cases không đổi giữa hai snapshot; chỉ script
  CT1 và tài liệu đường dẫn snapshot thay đổi trong lần sửa review.
- Không chạy lại test split, browser/full app suite: CT1 không sửa hành vi
  ứng dụng; chưa tuyên bố một chứng nhận mới cho toàn sản phẩm.

Sau này nếu code live đã thay đổi, replay trực tiếp từ bản script snapshot
bằng Python của môi trường khóa, truyền --output và --snapshot đường dẫn tuyệt
đối về baseline-v2 và snapshot-v2. Lệnh verify ở live hiện cố ý báo nếu đầu vào
live khác mốc. Snapshot chứa dữ liệu/model local, không tự publish.

## Phần cần bổ sung ở các CT sau

Bộ dữ liệu đánh giá mới cuối kỳ chưa được thu thập/rà nhãn độc lập. Quy trình
thu thập, chống trùng, giữ kín và sử dụng một lần đã ghi trong
docs/quality/ct1-protocol.md. Chưa coi phần đó là đã có hoặc được nghiệm thu.
Trước các kết luận học thuật về known cases, nhóm cần rà nhãn và version hóa
bản đã duyệt; không chỉnh trực tiếp mốc v2 đã đóng băng.

CT2 tiếp theo: thử trọng số lớp trên train, chọn bằng validation theo protocol,
báo delta từng lớp và ca hồi quy. Không thay model demo tự động.
