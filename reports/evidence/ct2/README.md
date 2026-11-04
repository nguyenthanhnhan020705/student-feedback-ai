# CT2 — Bằng chứng thí nghiệm trọng số lớp

Ngày 2026-10-31, integration-p0. Runner và báo cáo:
`reports/ct2_class_weights.py`, `docs/quality/ct2-report.md`.

- red-task1.txt: module CT2 chưa tồn tại, collection thất bại đúng feature thiếu.
- green-task1.txt: 27 passed (14 CT2 + 13 CT1), 2 warning iprint từ fixture LR.
- red-task2.txt: 9 failures vì thiếu run/verify; 14 tests Task 1 đạt.
- green-task2.txt: 36 passed (23 CT2 + 13 CT1), 2 warning fixture đã biết.
- run-1.txt: sáu lần fit thật, chỉ train. Không đổi artifact demo.
- replay-1.txt: tiến trình mới replay cả 6 artifact và ghép rank leaders đạt.

Run local chính thức sau sửa review: `.local-tools/ct2-class-weights/run-2/`.
Bản sao JSON/summary/receipt cuối lưu tại `run-2/` trong thư mục bằng chứng này.
Các bản ở gốc thư mục là run-1 lịch sử, giữ nguyên; joblib nghiên cứu chỉ local.

- review-red.txt: regression tái hiện lỗi so hòa dây chuyền (1 failed).
- review-green.txt: 37 passed (24 CT2 + 13 CT1), 2 warning fixture.
- run-2.txt/replay-2.txt: run và fresh-process replay với runner đã sửa đạt.
- run-comparison.txt: toàn bộ dự đoán/metrics/hồi quy từng ứng viên và bộ ghép
  khớp run-1, không đổi kết luận thực nghiệm.
- ct1-preservation.txt: fresh replay 49 đầu vào CT1/1583 câu/39 ca đạt.
- pip-check.txt: No broken requirements found.
- full-suite.txt: trước sửa review, 260 passed, 0 skipped, 14 warnings, 186,06s.
- review.md: một Important đã sửa bằng RED→GREEN; không có Critical/Minor.

Macro F1 validation: Sentiment 75,2966% → 77,5003%; Topic 75,4173% → 76,8397%.
Accuracy mỗi task giảm 0,1895 điểm %, có 13/21 ca validation đúng thành sai.
Hai nhãn cùng đúng giảm 1296 → 1294/1583; known-case Topic giảm 29 → 28/29.
Do đó không tự đưa ứng viên lên demo, không tuyên bố cải thiện độc lập.

Toàn suite cuối sau sửa review được lưu tại full-suite-final.txt. Warning là
Starlette/httpx và SciPy iprint; không có cảnh báo trong sáu lần fit thật.

Kết quả cuối: **261 passed, 0 skipped, 14 warnings**, 155,59 giây với
`TV2_RUN_REAL_DATA=1`. `ct1-preservation-final.txt` xác nhận replay cuối vẫn
khớp đủ 49 đầu vào, 1583 câu validation và 39 ca đã biết. Scoped whitespace
check đạt. Review condition đã đáp ứng bằng regression và suite cuối;
không gọi đây là một vòng review độc lập mới.

CT2 hoàn thành trong phạm vi thí nghiệm local. Baseline demo giữ nguyên,
không commit/push/merge; CT3–CT5 và Phase 6 chưa thực hiện.
