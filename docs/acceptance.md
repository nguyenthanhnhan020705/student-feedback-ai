# Ma trận nghiệm thu P0 — Phase 5, 2026-10-31

Kết quả kỹ thuật local không thay quyết định nghiệm thu/nộp bài của leader.
Phase 6 Word/slide và thông tin hành chính còn thiếu.

| Mã BRD | Điều kiện | Trạng thái và bằng chứng |
| --- | --- | --- |
| AC-01 | Nguồn, nhãn/split, chất lượng, EDA | Đạt kỹ thuật local: 11426/1583/3166, 9 checksum nguồn; reports/evidence/phase-2/verification.json. Quyền phân phối unknown. |
| AC-02 | 3 thuật toán/task, chọn validation, metrics test | Đạt baseline: hai winner Linear SVM; reports/metrics/{sentiment,topic}/comparison.json và báo cáo vai trò. Không train lại. |
| AC-03 | UI/API/hai model thật | Đạt kỹ thuật local: Chrome/Edge, ảnh/response tại reports/evidence/phase-5/, full-suite.txt. |
| AC-04 | Input rỗng, thiếu model | Đạt tình huống demo: blank/quá dài, 422, thiếu model 503, giữ input và phục hồi. Suite kiểm model hỏng, Unicode, lỗi inference. Minor ghi bên dưới. |
| AC-05 | CSV/export | Không áp dụng P0, P1 chưa được giao. |
| AC-06 | Dashboard | Không áp dụng P0, P1 chưa được giao. |
| AC-07 | Health sống/sẵn sàng | Đạt: ready/missing/invalid trong suite; 8 vòng đời server thực với ready/missing trong diễn tập. |
| AC-08 | Tái lập, code, report/slide, đóng góp | Đạt phần chạy/hướng dẫn local: DEMO.md, docs/development.md, reports/demo-script.md. Word/PPTX, đóng góp và duyệt cuối thuộc Phase 6, chưa đạt toàn mục. |

## Kiểm chứng

- 224 passed, 0 skipped, 12 warnings, 177,23 giây với TV2_RUN_REAL_DATA=1.
- Chrome 147.0.7727.101, Edge 156.0.4314.50: tiến trình mới, restart cùng cổng,
  mất server, thiếu model và phục hồi; cwd ngoài repo. Không xóa OS disk cache.
- Chặn socket/DNS ngoài loopback trong Python server và HTTP ngoài loopback
  trong browser context; service worker bị khóa. Guard có negative control.
  Không có request ngoài của ứng dụng trong các luồng được diễn tập; không
  chứng nhận mọi native-library/browser background socket hoặc firewall toàn máy.
- pip check đạt; 59 hash Data/ML giữ nguyên. Không train lại.
- Trạng thái cuối đóng gói/review tại reports/evidence/phase-5/README.md và ledger;
  không suy ra hoàn thành chỉ từ sự tồn tại của script.

## Hạn chế và việc còn chờ

- Minor Backend từ Phase 3: khóa JSON chứa lone surrogate vẫn bị từ chối 422
  INVALID_INPUT nhưng field có thể là body thay vì $body. Không tuyên bố mọi
  trường hợp biên đều đúng envelope; lỗi không chặn demo thường.
- Neutral test Recall 17,96%, F1 27,78%; Other Recall 30,82%, F1 40,66%.
  Một nhãn/task, không confidence hoặc bảo đảm đúng mọi câu.
- Một cặp trùng train; không giao text chuẩn hóa giữa split, chưa kiểm mọi
  near-duplicate. Không thay corpus hoặc tối ưu theo test.
- Warning Starlette/httpx và SciPy iprint đã ghi trong log; không nâng gói ML.
- Kernel notebook tương tác và máy/OS khác chưa chứng nhận. Gói không kèm Python,
  browser hoặc package cache; suy luận offline sau khi cài dependencies.
- Leader duyệt cuối/PR, bổ sung tên và lịch nộp. Không tự merge/push/nộp bài hoặc
  công bố dataset/model. Phase 6 chưa thực hiện.
