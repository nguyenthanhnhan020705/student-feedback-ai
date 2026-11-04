# CT4 — Augmentation không dấu chỉ từ train, 2026-10-31

Thí nghiệm offline đã chạy hữu hạn 6 cặp / 12 lần fit. Hai model demo trong models/ giữ nguyên. CT5 và Phase 6 không triển khai.

## Phương pháp và nguồn

Chỉ biến đổi train: NFC → NFD → bỏ combining marks → đ/Đ thành d/D → NFC. Giữ dấu câu, chữ số, emoji, khoảng trắng và case; normalizer chính thức vẫn nằm trong pipeline. Không đổi loader/corpus/split.
Chọn floor(25/50/100% số nguồn đủ điều kiện) theo SHA-256 ct4-v1|42|<source-id>; các subset lồng nhau. Thêm tối đa một biến thể/source, không bỏ câu gốc. Nhãn kế thừa là weak supervision, có thể mơ hồ/đổi nghĩa sau bỏ dấu; chưa được người rà từng biến thể.
Clone hai parent cố định: Original và research-selected CT3 (Sentiment char_2_none, Topic CT2 sqrt_balanced). Giữ mọi tham số và class_weight đúng parent, không tính lại trọng số theo augmented rows. Không thêm cấu hình/seed sau xem điểm.
Xếp từng task chỉ theo validation nguyên bản: Macro F1 cao nhất, dải hòa toàn cục 1e-6 rồi Accuracy cùng dung sai, còn hòa Original → CT2 → CT3 → thứ tự ứng viên. Stress/known cases không tham gia chọn. Không suy luận test trong runner; test lịch sử chỉ xuất hiện trong toàn suite hồi quy, không dùng chọn CT4.

## Số dòng và collisions

| Ratio | Source groups | Eligible | Added rows | Training rows |
| --- | ---: | ---: | ---: | ---: |
| 25% | 11426 | 11411 | 2852 | 14278 |
| 50% | 11426 | 11411 | 5705 | 17131 |
| 100% | 11426 | 11411 | 11411 | 22837 |

Không coi các dòng thêm là quan sát độc lập. Mỗi augmentation ID có parent_id, method/version/seed và nhãn nguồn. Các manifest đầy đủ chứa text chỉ lưu trong thư mục nghiên cứu local; không công bố dataset/model.

- 25%: 15 nguồn vốn không dấu; 33 nhóm nguồn trùng sau bỏ dấu, 5 nhóm có nhãn mâu thuẫn. Overlap normalized validation/known: 0/0; sau bỏ dấu: 6/0 source IDs đánh giá.
- 50%: 15 nguồn vốn không dấu; 33 nhóm nguồn trùng sau bỏ dấu, 5 nhóm có nhãn mâu thuẫn. Overlap normalized validation/known: 0/0; sau bỏ dấu: 6/0 source IDs đánh giá.
- 100%: 15 nguồn vốn không dấu; 33 nhóm nguồn trùng sau bỏ dấu, 5 nhóm có nhãn mâu thuẫn. Overlap normalized validation/known: 0/0; sau bỏ dấu: 6/0 source IDs đánh giá.

Collisions/overlap chỉ báo cáo, không xóa/chọn train theo validation hoặc đổi nhãn. Exact overlap không chứng nhận hết near-duplicates. Xem collisions-*.json local để biết ID/nhãn và hash text; bất đồng nhãn/overlap là giới hạn khi diễn giải robustness.

Rà nhãn sáu overlap sau bỏ dấu: 0 nhóm có bất đồng train/validation, giữ nguyên mọi nhãn; xem stress-overlap-label-audit.json. Dù nhãn khớp, các source overlap làm giới hạn tính độc lập của synthetic stress.

## Validation nguyên bản — cùng 1.583 source groups

| Pair | Sentiment Accuracy | Macro P | Macro R | Macro F1 | Topic Accuracy | Macro P | Macro R | Macro F1 | Joint |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| original | 91.4719% | 84.9978% | 72.1628% | 75.2966% | 87.9975% | 81.0247% | 73.7291% | 75.4173% | 1296/1583 = 81.8699% |
| ct2 | 91.2824% | 79.3282% | 76.1496% | 77.5003% | 87.8080% | 78.3034% | 76.3660% | 76.8397% | 1294/1583 = 81.7435% |
| ct3 | 91.0929% | 82.2463% | 76.8500% | 78.9855% | 87.8080% | 78.3034% | 76.3660% | 76.8397% | 1291/1583 = 81.5540% |
| original_aug25 | 91.3455% | 85.7496% | 72.0800% | 75.3208% | 87.8080% | 81.2156% | 73.5920% | 75.3023% | 1290/1583 = 81.4908% |
| original_aug50 | 91.4087% | 85.7966% | 72.1155% | 75.3630% | 87.8711% | 81.0263% | 73.5198% | 75.3764% | 1292/1583 = 81.6172% |
| original_aug100 | 91.5982% | 86.8337% | 72.2574% | 75.6109% | 87.9343% | 81.5709% | 73.8769% | 75.6978% | 1294/1583 = 81.7435% |
| ct3parent_aug25 | 91.2824% | 83.3846% | 77.3894% | 79.7354% | 87.8711% | 78.7268% | 76.3158% | 76.9484% | 1292/1583 = 81.6172% |
| ct3parent_aug50 | 91.1560% | 82.8458% | 76.4585% | 78.8858% | 87.6816% | 78.5770% | 76.1068% | 76.7727% | 1285/1583 = 81.1750% |
| ct3parent_aug100 | 91.2824% | 83.3997% | 77.3835% | 79.7398% | 87.5553% | 78.3369% | 75.9914% | 76.6436% | 1288/1583 = 81.3645% |
| CT4-only | 91.2824% | 83.3997% | 77.3835% | 79.7398% | 87.8711% | 78.7268% | 76.3158% | 76.9484% | 1292/1583 = 81.6172% |
| best through CT4 | 91.2824% | 83.3997% | 77.3835% | 79.7398% | 87.8711% | 78.7268% | 76.3158% | 76.9484% | 1292/1583 = 81.6172% |

CT4-only selection: `{'sentiment': 'ct3parent_aug100', 'topic': 'ct3parent_aug25'}`.
Best through CT4 selection: `{'sentiment': 'ct3parent_aug100', 'topic': 'ct3parent_aug25'}`.
Hai lựa chọn là ghép theo Macro F1 từng task; joint tính lại bằng hai pipeline thật trên cùng ID, không lấy trung bình Accuracy.

## Accuracy/joint so Original và CT3

| Pair | Metric | vs Original (điểm %) | vs Original (% tương đối) | vs CT3 (điểm %) | vs CT3 (% tương đối) |
| --- | --- | ---: | ---: | ---: | ---: |
| CT4-only | sentiment | -0.1895 | -0.2072 | +0.1895 | +0.2080 |
| CT4-only | topic | -0.1263 | -0.1436 | +0.0632 | +0.0719 |
| CT4-only | joint | -0.2527 | -0.3086 | +0.0632 | +0.0775 |
| best through CT4 | sentiment | -0.1895 | -0.2072 | +0.1895 | +0.2080 |
| best through CT4 | topic | -0.1263 | -0.1436 | +0.0632 | +0.0719 |
| best through CT4 | joint | -0.2527 | -0.3086 | +0.0632 | +0.0775 |

Kết luận đo trên validation: joint best through CT4 giảm 0.2527 điểm % so Original. Macro F1 là chỉ số cân bằng lớp riêng, không được diễn đạt thành phần trăm trả đúng tổng thể.
Model phục vụ không thay: mức thay đổi chất lượng đã triển khai là 0%. Validation đã được dùng nhiều lần, chưa chứng minh khả năng tổng quát trên phản hồi mới độc lập.

## Từng lớp, confusion matrix và hồi quy

### CT4-only

| Task/lớp | Precision | Recall | F1 | Support |
| --- | ---: | ---: | ---: | ---: |
| sentiment/negative | 91.9944% | 92.9078% | 92.4488% | 705 |
| sentiment/neutral | 66.0000% | 45.2055% | 53.6585% | 73 |
| sentiment/positive | 92.2046% | 94.0373% | 93.1119% | 805 |

sentiment matrix (hàng thật, cột dự đoán, thứ tự ['negative', 'neutral', 'positive']): `[[655, 6, 44], [20, 33, 20], [37, 11, 757]]`.

| Task/lớp | Precision | Recall | F1 | Support |
| --- | ---: | ---: | ---: | ---: |
| topic/lecturer | 93.3102% | 93.3102% | 93.3102% | 1151 |
| topic/curriculum | 72.3906% | 80.5243% | 76.2411% | 267 |
| topic/facility | 88.8889% | 91.4286% | 90.1408% | 70 |
| topic/other | 60.3175% | 40.0000% | 48.1013% | 95 |

topic matrix (hàng thật, cột dự đoán, thứ tự ['lecturer', 'curriculum', 'facility', 'other']): `[[1074, 59, 4, 14], [40, 215, 2, 10], [2, 3, 64, 1], [35, 20, 2, 38]]`.

- vs original, sentiment: sai→đúng 27, đúng→sai 30, thay nhãn 65 (giữ cả sai→sai).
- vs original, topic: sai→đúng 17, đúng→sai 19, thay nhãn 41 (giữ cả sai→sai).
- vs original, joint: sai→đúng 33, đúng→sai 37, thay ít nhất một nhãn 99.
- vs ct3, sentiment: sai→đúng 11, đúng→sai 8, thay nhãn 21 (giữ cả sai→sai).
- vs ct3, topic: sai→đúng 5, đúng→sai 4, thay nhãn 9 (giữ cả sai→sai).
- vs ct3, joint: sai→đúng 10, đúng→sai 9, thay ít nhất một nhãn 30.

### best through CT4

| Task/lớp | Precision | Recall | F1 | Support |
| --- | ---: | ---: | ---: | ---: |
| sentiment/negative | 91.9944% | 92.9078% | 92.4488% | 705 |
| sentiment/neutral | 66.0000% | 45.2055% | 53.6585% | 73 |
| sentiment/positive | 92.2046% | 94.0373% | 93.1119% | 805 |

sentiment matrix (hàng thật, cột dự đoán, thứ tự ['negative', 'neutral', 'positive']): `[[655, 6, 44], [20, 33, 20], [37, 11, 757]]`.

| Task/lớp | Precision | Recall | F1 | Support |
| --- | ---: | ---: | ---: | ---: |
| topic/lecturer | 93.3102% | 93.3102% | 93.3102% | 1151 |
| topic/curriculum | 72.3906% | 80.5243% | 76.2411% | 267 |
| topic/facility | 88.8889% | 91.4286% | 90.1408% | 70 |
| topic/other | 60.3175% | 40.0000% | 48.1013% | 95 |

topic matrix (hàng thật, cột dự đoán, thứ tự ['lecturer', 'curriculum', 'facility', 'other']): `[[1074, 59, 4, 14], [40, 215, 2, 10], [2, 3, 64, 1], [35, 20, 2, 38]]`.

- vs original, sentiment: sai→đúng 27, đúng→sai 30, thay nhãn 65 (giữ cả sai→sai).
- vs original, topic: sai→đúng 17, đúng→sai 19, thay nhãn 41 (giữ cả sai→sai).
- vs original, joint: sai→đúng 33, đúng→sai 37, thay ít nhất một nhãn 99.
- vs ct3, sentiment: sai→đúng 11, đúng→sai 8, thay nhãn 21 (giữ cả sai→sai).
- vs ct3, topic: sai→đúng 5, đúng→sai 4, thay nhãn 9 (giữ cả sai→sai).
- vs ct3, joint: sai→đúng 10, đúng→sai 9, thay ít nhất một nhãn 30.

### Đánh đổi từng lớp của best through CT4

| Task/lớp | Δ Precision vs Original (điểm %) | Δ Recall vs Original | Δ F1 vs Original | Δ Precision vs CT3 | Δ Recall vs CT3 | Δ F1 vs CT3 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| sentiment/negative | +1.0355 | -1.2766 | -0.0947 | +0.6295 | -0.1418 | +0.2493 |
| sentiment/neutral | -5.4286 | +17.8082 | +14.0546 | +3.2549 | +1.3699 | +2.0456 |
| sentiment/positive | -0.4014 | -0.8696 | -0.6304 | -0.4244 | +0.3727 | -0.0320 |
| topic/lecturer | +1.2561 | -1.3032 | -0.0060 | -0.0696 | +0.1738 | +0.0522 |
| topic/curriculum | -1.2205 | +1.1236 | -0.1553 | -0.0926 | -0.3745 | -0.2190 |
| topic/facility | -1.2520 | +0.0000 | -0.6393 | +0.0000 | +0.0000 | +0.0000 |
| topic/other | -7.9752 | +10.5263 | +6.9248 | +1.8559 | +0.0000 | +0.6013 |

Neutral/other có thay đổi Recall/F1 đi kèm Precision và các lớp còn lại như bảng; không coi Macro F1 tăng là mọi lớp đều tăng.

results.json chứa đầy đủ metrics/per-class/matrix/prediction rows và mọi changed/improved/regressed IDs cho cả 6 cặp, mỗi cặp ghép, so Original/CT2/CT3.

## Stress không dấu và known cases — tách riêng

| Pair | Stress sentiment Accuracy | Stress topic Accuracy | Stress joint | Known sentiment | Known topic | Known joint |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| original | 51.6740% | 63.1712% | 513/1583 | 21/30 | 29/29 | 18/25 |
| ct2 | 43.2091% | 46.8099% | 384/1583 | 21/30 | 28/29 | 18/25 |
| ct3 | 51.5477% | 46.8099% | 416/1583 | 25/30 | 28/29 | 22/25 |
| CT4-only | 91.3455% | 84.4599% | 1241/1583 | 25/30 | 29/29 | 22/25 |
| best through CT4 | 91.3455% | 84.4599% | 1241/1583 | 25/30 | 29/29 | 22/25 |

Stress dùng đúng source groups validation, chỉ bỏ dấu và kế thừa nhãn weak supervision; không là tập độc lập. Known cases là 39 câu đã lộ, nhãn assistant_proposed chưa human-reviewed, null bị loại mẫu số từng task/joint. Không gộp stress/known với validation thành benchmark chung.

## Chi phí và artifact

| Candidate | Fit sentiment (s) | Fit topic (s) | Eval validation pair (s) | Model bytes sentiment/topic | Fit warnings |
| --- | ---: | ---: | ---: | --- | ---: |
| original_aug25 | 0.599 | 0.797 | 0.093 | 848112/991176 | 0 |
| original_aug50 | 0.780 | 0.866 | 0.107 | 997504/1166728 | 0 |
| original_aug100 | 1.388 | 1.235 | 0.081 | 1240048/1451720 | 0 |
| ct3parent_aug25 | 3.116 | 0.900 | 0.261 | 1301328/991256 | 0 |
| ct3parent_aug50 | 3.087 | 0.818 | 0.204 | 1492160/1166808 | 0 |
| ct3parent_aug100 | 4.516 | 1.266 | 0.225 | 1804848/1451800 | 0 |

Thời gian là đo local gồm overhead Python, không SLA/benchmark nhiều lần. Cấu hình không tăng class weight theo số dòng thêm; kết quả không cô lập việc tăng dữ liệu khỏi độ lặp của source groups.

## Tái lập và trạng thái kiểm chứng

Run chính thức: `.local-tools/ct4-augmentation/run-1/`. Chạy `./.venv/Scripts/python.exe -B reports/ct4_augmentation.py verify` từ bản tích hợp; verify không fit. Run từ chối output cũ/live, symlink/junction ngoài research và overlap với controls.
Replay tái tạo subset/biến đổi/manifest/collisions, kiểm receipt schema_version/promotion/deployment và chính xác tập payload/path/checksum, nguồn/runtime/parent hashes, metadata/readiness, train-only vocabulary/IDF mỗi nhánh, params/class_weight, metrics/ranking/delta/stress/ghép thật.
Bằng chứng RED/GREEN, replay, full suite, pip check và preservation tại reports/evidence/ct4/. Review độc lập do agent khác thực hiện sau implementation; kết quả cuối ghi ở review.md và ct4-progress.md, không suy ra đã review từ sự tồn tại của report này.
Giữ quyền nguồn license unknown; chỉ local, không công bố/phân phối. Chưa có tập đánh giá mới gán nhãn độc lập; exact overlaps/collisions và nhãn kế thừa giới hạn suy luận. CT3 minor receipt semantics cũ và Backend lone-surrogate field minor giữ nguyên, không sửa để làm vô hiệu controls.

## Kiểm chứng cuối và review

Toàn suite dữ liệu thật và Chrome/Edge: **306 passed, 0 skipped, 14 cảnh báo thư viện đã biết, 227,62 giây**. Pip check đạt; fresh-process replay cấm Pipeline.fit và LinearSVC.fit đạt. Không nâng dependencies.

Review độc lập đã duyệt, không còn Critical/Important/Minor trong CT4; xem reports/evidence/ct4/review.md. Hai phát hiện ban đầu về fixture ASCII không sinh augmentation và nested receipt payload đã có regression RED→GREEN; lỗi định dạng bảng báo cáo đã sửa. Các minor cũ CT3/Backend ngoài phạm vi giữ nguyên và công khai.

Bảo toàn: **335/335 file có trước khớp hash**; CT1 live/snapshot49 mỗi bộ, CT2 19 payloads, CT3 31 payloads và CT4 41 payloads đều khớp. Sáu file ảnh/JSON browser được sao riêng trong evidence CT4; bản cũ đã khớp byte nên không cần khôi phục. Hai model demo, runner CT1–CT3 và công việc chưa commit giữ nguyên. Không CT5/Phase6, commit/push/merge hay công bố dữ liệu/model.
