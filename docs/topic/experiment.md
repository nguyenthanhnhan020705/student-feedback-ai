# TV4 — Thiết kế và tái lập thí nghiệm Topic v1.0

Thực hiện local ngày 2026-10-29 theo yêu cầu hoàn thiện TV4. Kế thừa ba module từ
commit `74330f3` của `origin/feature/topic-model`, bổ sung kiểm thử và minh chứng.
Workspace vẫn ở `feature/data-preprocessing` để sử dụng Data chưa commit.

## Thiết kế đã chốt trước khi xem test

- Dữ liệu: loader chung `ml.data`, split gốc 11426/1583/3166; chỉ raw text là feature.
- Target: `lecturer`, `curriculum`, `facility`, `other` theo `TOPIC_LABELS`.
- Tiền xử lý trong pipeline: `ml.preprocessing.normalize_text` v1.0; không đổi Data.
- TF-IDF: ngram (1,2), min_df=2, max_df=1.0, sublinear_tf=True, norm=l2,
  lowercase=False, strip_accents=None, token_pattern=`(?u)\b\w+\b`.
- NB alpha=1.0; LR C=1.0/lbfgs/max_iter=2000; LinearSVC C=1.0/dual=auto/max_iter=5000.
  LR/SVC class_weight=None và random_state=42.
- Chỉ fit train; chọn Macro F1 validation, hòa trong 1e-6 thì Accuracy rồi
  thứ tự nb → logistic_regression → linear_svm. Không refit train+validation.
- Đánh giá ba model trên test sau chọn; không dùng test để đổi winner/cấu hình.
- SHA-256 từng file nguồn và thống kê phải khớp manifest trước training/evaluate.

## Môi trường và chạy lại

Python 3.13.x 64-bit. `requirements/topic.txt` là constraints; phiên bản local chính xác
ở `reports/evidence/topic/requirements-local.txt`, không phải lock chung leader.
Phiên làm việc này dùng `.venv/sentiment/Scripts/python.exe` đã có đủ ML packages;
không thay thư viện của môi trường đó. Có thể tạo môi trường riêng như sau:

```powershell
python -m venv .venv/topic
./.venv/topic/Scripts/python.exe -m pip install -r reports/evidence/topic/requirements-local.txt
./.venv/topic/Scripts/python.exe -m pytest tests/test_topic_training.py tests/test_topic_artifacts.py -q
```

CLI từ repository root (thay `python` bằng interpreter phù hợp):

```powershell
python -m ml.train_topic --data-dir data/raw --manifest reports/data/manifest.json --output-dir models --report-dir reports/metrics/topic --figure-dir reports/figures/topic
python -m ml.evaluate_topic --data-dir data/raw --manifest reports/data/manifest.json --pipeline models/topic_pipeline.joblib --output-dir reports/metrics/topic
python docs/topic/complete_experiment.py
python docs/topic/run_notebook.py
```

Train từ chối ghi đè artifact/metadata/comparison/figure đã tồn tại. Để tái lập độc lập,
dùng ba đường dẫn mới cùng nhau, ví dụ `--output-dir .local-tools/topic-rerun/models
--report-dir .local-tools/topic-rerun/metrics --figure-dir .local-tools/topic-rerun/figures`.
Evaluate ghi `selected_test.json` riêng và cũng từ chối ghi đè; dùng output-dir mới nếu cần.
`complete_experiment.py` và notebook kiểm chứng/reuse baseline hiện có, không huấn luyện lại;
nếu chưa có baseline, notebook gọi train CLI. Không chạy lại train chỉ để chạy notebook.

Notebook `03_topic.ipynb` có output thật. Runner chạy tuần tự các cell Python và thu stdout/stderr,
không sử dụng Jupyter kernel; không có magic/rich display. Có thể mở notebook bằng Jupyter/VS Code
với kernel cùng phiên bản ML; các gói notebook UI là tùy chọn, không cần để chạy runner.

## Phạm vi và hạn chế bàn giao

Manifest Data vẫn `pending_leader_review`, license nguồn còn `unknown`; yêu cầu hoàn thiện
local không thay thế việc xác nhận quyền sử dụng/phân phối hay nghiệm thu M1.
Dataset và joblib giữ local/ignore Git. Không sửa split hay xử lý mẫu trùng ngoài chính sách
Data report-only. Leader cần khóa môi trường chung, nhận artifacts và kiểm tích hợp Backend.
