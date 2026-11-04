# Phase 5 — kiểm thử tổng thể và đóng gói demo

Ngày 2026-10-31, feature/integration-p0, BASE 0ebd066.
Không sửa hành vi production, train, đổi artifact hoặc commit/push/merge.

## Lệnh đã chạy

```powershell
$env:TV2_RUN_REAL_DATA='1'
./.venv/Scripts/python.exe -m pytest -q -p no:cacheprovider
./.venv/Scripts/python.exe -m pip check
./.venv/Scripts/python.exe reports/verify_phase5.py
```

- full-suite.txt: 224 passed, 0 skipped, 12 warnings, 177,23 giây; gồm 42 browser cases.
- pip-check.txt: No broken requirements found.
- rehearsal.txt/json: 8 vòng đời server từ cwd ngoài repo; 2 browser, 6 dự đoán
  thật và phục hồi khi server mất/thiếu model. 59 hash Data/ML giữ nguyên.
- *-server.txt: HTTP logs. *-network.jsonl: đúng một probe mạng ngoài cố ý bị
  chặn mỗi process, không có request ngoài của ứng dụng.
- *-offline-real.png: ảnh suy luận thật; *-missing-models.png: chưa sẵn sàng.
  Kết quả trên ảnh thiếu model là lần trước, không phải dự đoán mới; nút bị khóa.
  Khi POST mới thất bại, kết quả cũ bị xóa như suite kiểm.

## Thời gian đo trên máy này

| Browser | Startup có model (giây, 3 lần) | Thiếu model (giây) | Click → kết quả (giây, 3 câu) |
| --- | --- | --- | --- |
| Chrome 147.0.7727.101 | 4,333 / 4,788 / 4,270 | 1,575 | 0,267 / 0,062 / 0,068 |
| Edge 156.0.4314.50 | 4,282 / 4,283 / 4,766 | 2,160 | 0,101 / 0,091 / 0,046 |

Có overhead browser/health polling, không phải benchmark thuần model hoặc SLA.
Lạnh là process mới, không xóa OS disk cache; suite có thể chạy đồng thời.

## Phạm vi offline

Python audit hook chặn DNS/socket ngoài loopback trước import app; browser route
chặn HTTP ngoài loopback và service worker. Có negative control server/browser.
Không thay mạng máy, không chứng nhận mọi native/background socket của OS.
Các luồng demo đã chạy bằng dependencies/model local dưới guard này.

## Đóng gói và review

Đầu mối: DEMO.md, reports/demo-script.md, docs/acceptance.md.
reports/package_demo.py tạo ZIP nội bộ code/lock/data/model/hướng dẫn kèm manifest
SHA-256 và từ chối ghi đè. Giải nén ngoài repo, kiểm mọi file và chạy API/UI/model
thật dưới guard; dùng venv khóa hiện có, không phải cài mới trên máy khác.
Package verification và review cuối sẽ được ghi trước khi kết thúc Phase 5.

Minor lone-surrogate detail field từ Phase 3 vẫn công khai. Giữ giới hạn ML,
license unknown và phạm vi P1. Phase 6 chưa làm.

Biên bản package-verification.json bên cạnh ZIP là nguồn kiểm chứng gói cuối.
Bản sao cũng được ghi tại reports/evidence/phase-5/ của workspace nguồn sau khi
đóng gói. Biên bản/log package cũ không được nhúng vào ZIP mới (ZIP không thể
chứa hash cuối của chính nó); manifest file bên trong chỉ kiểm payload.

## Kết quả review và bàn giao

Review độc lập phase5_review không còn Critical/Important/Minor trong thay đổi
Phase 5. Đã sửa loại biên bản/log gói cũ khỏi ZIP mới. Xem review.md.
Gói cuối mặc định: .local-tools/phase5-delivery/student-feedback-ai-local.zip;
biên bản/hash cuối ở package-verification.json bên cạnh gói. Bản candidate đã
qua kiểm hash 252 file, chạy thật sau giải nén; gói cuối phải được kiểm lại bởi
công cụ và kết quả cuối được ghi trong ledger. Gói không kèm venv hoặc binary.
Kiểm từ chối ghi đè candidate đạt, SHA-256 candidate giữ nguyên.

## Xác nhận cuối

Gói cuối đã kiểm chứng: 252 file, 2.360.983 byte; SHA-256
c7905ea0da9f0ed77663792f92412f8c6c40b38a8f3b795544289f3a49a313fc.
Giải nén ngoài repo: health ready, 4 assets, hai nhãn thật đều đạt dưới guard;
startup 4,337 giây, tiến trình đã dừng. Kiểm lại ZIP/hash sau tạo đạt, không có
biên bản/log package cũ; 59 hash Data/ML giữ nguyên. Review condition đã đáp ứng.
Snapshot ZIP được tạo trước biên bản kết thúc này; sidecar cạnh ZIP và ledger
workspace ghi kết quả cuối. Phase 5 hoàn thành; Phase 6 chưa triển khai.
