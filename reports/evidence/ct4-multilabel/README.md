# Bằng chứng demo CT4 theo ontology 3.0

Yêu cầu gốc: `docs/quality/ct4-multilabel-agent-handoff.md`, mục 1–8.
Hướng dẫn và giới hạn: `docs/quality/ct4-multilabel-demo.md`.
Nhật ký: `docs/superpowers/plans/ct4-multilabel-progress.md`.

Ứng dụng mới: `demo_v3.main:app`, API `/api/v3/predict`, local
`http://127.0.0.1:8002/`. Bộ tổng hợp đúng bảng nghiệp vụ; bộ nhận diện là luật
ngữ cảnh thử nghiệm có phiên bản, CT4 chỉ phân tích đoạn để audit.

## Chứng cứ và ý nghĩa

| File | Nội dung |
| --- | --- |
| `preexisting.json`, `git-before.txt` | 708 file gốc được inventory trước khi tạo mã/thiết kế mới |
| `design-review.md` | Kiểm khả thi thiết kế bằng agent độc lập |
| `engine-red.txt`, `engine-green.txt` | RED 78 thất bại vì thiếu engine; GREEN 78 đạt |
| `api-context-*`, `accent-*`, `pronoun-*` | Vòng tests API/ngữ cảnh/phân biệt dấu trước đóng băng |
| `browser-red.txt`, `task1-green.txt` | UI chưa có → toàn scoped ban đầu 173 đạt, 1 warning |
| `core-freeze.json`, `task1-verification.json` | Nguồn/cấu hình ban đầu và checksum nguồn tái sử dụng |
| `exploratory-cases.json`, `evaluation.json` | 36 biến thể soạn sau đóng băng; điểm ở mốc ban đầu |
| `review.md` | Review độc lập: ba lỗi ngữ cảnh R1–R3 cần sửa |
| `review-red.txt`, `review-green.txt`, `review-fix-verification.json` | RED 22 lỗi/4 đạt → scoped 199 đạt, 1 warning |
| `review-fix-rereview.md` | Kiểm lại độc lập: R1–R3 đã sửa, phát hiện hồi quy R4 |
| `review-r4-*` | RED 6 lỗi/4 đạt → 167 tests engine/API đạt; rules/UI giữ nguyên |
| `evaluation-after-r1-r3.json` | Giữ lại điểm ở bản sửa trước R4, không gán cho mã cuối |
| `evaluation-final.json` | Chạy lại hữu hạn trên mã cuối, hash ràng buộc riêng |
| `historical-replay.json`, `replay-*.txt` | CT1–CT5 replay riêng tiến trình; fitting APIs bị cấm, cả năm exit 0 |
| `pip-check.txt` | Không có dependency hỏng |
| `live-demo.json`, `live-browser/` | Health/assets/API thật và ảnh Chrome/Edge desktop/mobile |
| `preservation.json` | Đối chiếu byte gốc sau suite, chỉ restore ảnh/JSON browser từ backup đã kiểm hash |
| `handoff-verification.json` | Receipt cuối; chỉ tạo khi toàn bộ điều kiện đóng kỹ thuật đạt |

`full-suite.txt` là run 608 tests đạt, 14 warnings, 642,00 giây, nhưng chạy
giao thời với các sửa detector nên được giữ làm lịch sử, không chứng nhận mã cuối.
Chỉ `full-suite-final.txt` được receipt cuối kiểm nhận; run chưa bao gồm R4 sẽ được
giữ riêng dưới tên `full-suite-before-r4.txt` trước khi chạy lại trên mã ổn định.
Không suy ra suite đã đạt từ việc file log tồn tại.

Kết quả cuối thực tế: **644 passed, 0 skipped, 14 warnings trong 628,67 giây**,
exit 0. Mười ba hash source/tests v3 khớp trước và sau suite; receipt R4 cũng khớp.
`pip check` đạt. Cả năm replay CT1–CT5 có exit 0 với fitting bị cấm. Đối chiếu cuối
**708/708 file gốc khớp**, không có file cần phục hồi từ backup ở lần chạy này.
Server mã cuối đã được restart trên 8002; health/assets, bốn ví dụ nghiệp vụ,
bốn ca review qua HTTP và Chrome/Edge desktop/mobile đã được kiểm thực tế.

## Diễn giải chất lượng

Ở mốc đầu: 15/15 ví dụ đặc tả và 32/36 biến thể có cả hai nhãn khớp nhãn đề xuất.
Sau R1–R3 và sau R4, điểm vẫn 15/15 và 32/36. Bốn lỗi thăm dò 02, 17, 30, 31 được
giữ nguyên; không chỉnh lexicon/ngưỡng để nâng điểm. JSON có confusion matrix,
per-class/support, joint exact match và audit theo đoạn, tách hai tập.

Nhãn biến thể do trợ lý đề xuất, chưa có người rà độc lập. Các lần chạy lại sau
review là hồi quy trên tập đã lộ, không phải holdout mới. Không so trực tiếp điểm
này với Accuracy/F1 UIT-VSFC cũ, không coi aggregator đúng là detector hiểu đúng.
Không có confidence đã hiệu chỉnh, không chứng nhận phủ định tổng quát/OOD.

R1–R3 được kiểm lại độc lập. R4 được tái hiện/sửa bằng tests trước code và kiểm
tích hợp cuối; không có lượt review độc lập thứ ba. Đọc log/receipt để phân biệt
chứng cứ người triển khai chạy với những gì reviewer tự kiểm.

Trạng thái bàn giao kỹ thuật cuối sau các checks:
`engineering_complete_independent_evaluation_pending`. Thiếu tập final theo
ontology mới được người rà là giới hạn đánh giá; không bịa người rà hoặc điểm số.

Giữ nguyên baseline/v2, corpus, artifact và mọi mốc CT1–CT5. Không fit lại artifact
lịch sử, cài dependency, dùng dịch vụ ngoài, commit/push/merge hoặc công bố dữ liệu.
Quyền phân phối nguồn còn unknown; chỉ demo local.
