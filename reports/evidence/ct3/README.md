# CT3 — Bằng chứng thí nghiệm từ + ký tự

Ngày 2026-10-31; workspace integration-p0. Báo cáo chính:
`docs/quality/ct3-report.md`; runner: `reports/ct3_word_char.py`.

- red-task1.txt: module CT3 chưa có, lỗi import đúng feature thiếu.
- green-task1.txt: 46 passed (9 CT3, 13 CT1, 24 CT2), 2 warning fixture đã biết.
- red-task2.txt: 11 lỗi đúng do lifecycle API chưa có, 9 tests trước đạt.
- green-task2.txt: 57 passed (20 CT3, 13 CT1, 24 CT2), 2 warning fixture.
- run-1.txt: 12 fits thật, chỉ train, không warning; giữ model đang phục vụ.
- replay.txt: tiến trình mới kiểm 12 artifact, vocabulary/IDF train, metadata,
  nguồn/runtime, metrics, hồi quy, phần trăm và bộ ghép. Không fit, không test inference.
- config.json/results.json/summary.md/receipt.json: bản sao run-1 chính thức.
  Các artifact nghiên cứu ở `.local-tools/ct3-word-char/run-1/`, không đưa vào Git.
- pip-check.txt: kiểm dependencies môi trường hiện có.
- full-suite.txt: toàn suite thật với TV2_RUN_REAL_DATA=1; đọc dòng kết quả cuối,
  không suy ra hoàn tất khi log còn đang chạy.

Kết quả: ghép nghiên cứu giữ Topic CT2, chọn Sentiment CT3 char_2_none.
Macro F1 cảm xúc +3,6889 điểm % so original; Accuracy cảm xúc −0,3790 điểm %.
Hai nhãn cùng đúng 1296 → 1291/1583 (−0,3159 điểm %, −0,3858% tương đối).
Ghép thuần hai ứng viên mới CT3 đạt 1286/1583, không vượt control Topic CT2.
Known-case joint tăng 18/25 → 22/25 nhưng nhãn chưa rà độc lập, không coi đó
là điểm chất lượng tổng quát. Ứng dụng giữ baseline, không tự deploy.

Kiểm chứng cuối: **281 passed, 0 skipped, 14 known warnings, 197.07s**;
pip check đạt. `preservation.json` xác nhận 49 đầu vào live CT1 và 19 payload
CT2 giữ nguyên, runner CT2 khớp hash; fresh replay còn kiểm snapshot và metrics.
`review.md`: review độc lập không có Critical/Important; một minor hoãn ở hai
trường mô tả schema_version/promotion của receipt, không đổi model/metrics.
CT3 hoàn thành trong phạm vi thí nghiệm local; model phục vụ vẫn baseline.
CT4–CT5/Phase 6, commit/push/merge/publication ngoài phạm vi.
