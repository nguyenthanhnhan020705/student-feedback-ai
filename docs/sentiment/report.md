# Báo cáo TV3 — Sentiment

Baseline v1.0: TF-IDF + NB/LR/Linear SVM, fit chỉ train; chọn bằng Macro F1 validation rồi Accuracy và thứ tự cố định. Không refit train+validation.

Người dùng xác nhận TV2 hoàn thành và cho phép tiếp tục ngày 2026-10-28. Manifest Data giữ nguyên pending_leader_review; môi trường local chưa phải lock chung leader. Workspace đang ở feature/data-preprocessing, có cả thay đổi TV2 và TV3 chưa commit. Chưa kiểm tích hợp Backend thật.

## Tái lập

Dùng Python 3.13 và môi trường riêng .venv/sentiment; requirements/sentiment.txt là constraints, reports/evidence/sentiment/requirements-local.txt là snapshot local.

```powershell
./.venv/sentiment/Scripts/python.exe -m pytest tests/test_sentiment_training.py tests/test_sentiment_artifacts.py -q
./.venv/sentiment/Scripts/python.exe -m ml.train_sentiment --data-dir data/raw --output-dir models --report-dir reports/metrics/sentiment
./.venv/sentiment/Scripts/python.exe -m ml.evaluate_sentiment --data-dir data/raw --pipeline models/sentiment_pipeline.joblib --output-dir reports/metrics/sentiment
./.venv/sentiment/Scripts/python.exe docs/sentiment/complete_experiment.py
```

Notebook 02 gọi cùng CLI: chạy notebook hoặc lệnh train khi tái lập, tránh train hai lần. Không chỉnh cấu hình theo điểm test.

## Bàn giao Backend

Pipeline và metadata nằm trong models/, joblib bị ignore Git: tái tạo hoặc chuyển nội bộ theo quy trình nhóm. Kiểm checksum trước khi nạp. Backend cần cùng Python minor và năm phiên bản gói trong metadata. API còn cần Topic và kiểm thử tích hợp thật.

comparison.json chứa validation/test của cả ba model; selected_test.json kiểm chứng winner sau tải và không ghi đè comparison. Confusion matrix nằm ở reports/figures/sentiment/. error_analysis.json chứa cặp nhầm và ID ví dụ, không công bố câu nguồn. reload.json chứa câu đối chiếu tự viết và kết quả trước/sau tải trong tiến trình mới.

## Kết quả đo thật

| Split | Model | Accuracy | Macro Precision | Macro Recall | Macro F1 |
|---|---|---:|---:|---:|---:|
| validation | nb | 0.873026 | 0.582215 | 0.611139 | 0.595527 |
| validation | logistic_regression | 0.907770 | 0.877831 | 0.671929 | 0.688945 |
| validation | linear_svm | 0.914719 | 0.849978 | 0.721628 | 0.752966 |
| test | nb | 0.857233 | 0.572207 | 0.604441 | 0.586950 |
| test | logistic_regression | 0.889766 | 0.823527 | 0.646977 | 0.648432 |
| test | linear_svm | 0.897031 | 0.804905 | 0.685335 | 0.705104 |

Winner: linear_svm (validation Macro F1).

| Label (test) | Precision | Recall | F1 | Support |
|---|---:|---:|---:|---:|
| negative | 0.875486 | 0.958126 | 0.914944 | 1409 |
| neutral | 0.612245 | 0.179641 | 0.277778 | 167 |
| positive | 0.926984 | 0.918239 | 0.922591 | 1590 |

326 / 3166 test predictions were incorrect. Confusion pairs:

- positive -> negative: 118
- neutral -> negative: 74
- neutral -> positive: 63
- negative -> positive: 52
- positive -> neutral: 12
- negative -> neutral: 7

Lớp neutral ít mẫu và khó nhận diện; xem Recall/F1 từng lớp ở trên. Đây là giới hạn của baseline, không dùng điểm test để chỉnh lại model. TF-IDF n-gram chưa mô hình hóa đầy đủ ngữ cảnh, câu nhiều cảm xúc hoặc cách nói gián tiếp; đây là giả thuyết giải thích, không phải kết luận nhân quả. Ví dụ lỗi theo ID ở error_analysis.json giúp kiểm tra lại trên corpus local.

Nguồn Data: train 11426, validation 1583, test 3166; giữ hai dòng thuộc nhóm trùng trong train theo chính sách report_only, không có text chuẩn hóa giao nhau giữa split theo manifest. Không coi kiểm tra vocabulary là loại bỏ mọi nguy cơ rò rỉ.

Kiểm chứng tải lại: dự đoán ba câu tự viết trước/sau tải trong tiến trình mới khớp; xem reload.json. Evaluate CLI sinh selected_test.json độc lập, kết quả khớp winner trong comparison.

Cảnh báo môi trường local: scikit-learn 1.6.1 với SciPy mới phát OptimizeWarning về iprint; lệnh hoàn thành và pip check đạt. Matplotlib báo không ghi được font cache ngoài workspace, hình vẫn xuất được. Cần leader khóa/kiểm tra đúng môi trường Backend trước tích hợp.

## Cập nhật xác minh Phase 2 — 2026-10-30

Trên bản tích hợp, model/checksum/runtime/manifest đã được đối chiếu bằng môi
trường khóa Phase 1. Tải trong tiến trình mới khớp các câu lưu trong reload.json;
metrics validation/test tính lại từ winner khớp comparison và selected_test.
Không train lại; cấu hình ba thuật toán và bảng notebook được đối chiếu bằng
script. Vocabulary/IDF của artifact khớp thống kê train. Bộ Data/ML đạt 63 tests,
không skip. Bằng chứng: `reports/evidence/phase-2/`.
Neutral vẫn yếu (Recall 17,96%, F1 27,78%); một cặp trùng train được giữ.
Nguồn vẫn license unknown; demo local được phép theo kế hoạch 2026-10-30,
không xác nhận quyền phân phối. Phần này chưa nghiệm thu Backend/Frontend.
