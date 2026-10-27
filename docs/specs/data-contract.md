# Hợp đồng Data, mô hình và artifact v1.0

**Trạng thái:** Leader đã duyệt cùng Phase 0 v1.0 ngày 2026-10-19. Chưa tải/kiểm đếm dataset hoặc huấn luyện mô hình trong phase này.

## 1. Nguồn và quy tắc nhãn

Dùng UIT-VSFC làm nguồn dự kiến cho học phần. [Repository tác giả](https://github.com/kietnv/uit-vsfc) và [dataset card UIT-NLP](https://huggingface.co/datasets/uitnlp/vietnamese_students_feedback/blob/main/README.md) là điểm đối chiếu. Dataset card mô tả train 11426, validation 1583, test 3166; trường nguồn sentence và nhãn số như bảng dưới. Đây là số tham khảo từ nguồn, chưa phải số kiểm đếm bản tải của nhóm.

| Task | Mã nguồn được mô tả | Nhãn chuỗi chuẩn trong dự án |
| --- | --- | --- |
| sentiment | 0 | negative |
| sentiment | 1 | neutral |
| sentiment | 2 | positive |
| topic | 0 — lecturer | lecturer |
| topic | 1 — training_program | curriculum |
| topic | 2 — facility | facility |
| topic | 3 — others | other |

Dataset card hiện ghi license unknown. Data phải xác minh điều kiện sử dụng từ nguồn/đầu mối cung cấp, lưu bằng chứng và leader chấp thuận trước M1/training thật. Không coi dữ liệu truy cập được là đã được phép phân phối. Dataset giữ local, không commit lên repo public; chưa tự gán giấy phép. Các phần khác vẫn viết code/tests bằng fixture tự tạo được trong lúc việc xác minh này thực hiện.

## 2. Giao diện loader — Data sở hữu

`ml/data.py` cung cấp:

```python
def load_split(data_dir: str | Path, split: Literal["train", "validation", "test"]) -> pandas.DataFrame: ...
def load_dataset(data_dir: str | Path) -> dict[str, pandas.DataFrame]: ...
```

DataFrame có đúng các cột theo thứ tự: `id`, `text`, `sentiment`, `topic`, `split`; giá trị không null, dtype object/string được phép nhưng mỗi cell là Python string. `load_dataset` trả đủ ba key train/validation/test.

- `id`: `<split>:<số thứ tự 6 chữ số>`, đếm từ 1 trước biến đổi; ví dụ train:000001.
- `text`: câu nguồn raw được giải mã UTF-8, chỉ bỏ ký tự phân cách dòng của file nguồn. Không lower/chuẩn hóa ở loader; không làm mất dấu, phủ định hay dấu câu.
- sentiment/topic: chuỗi chuẩn từ bảng, không còn số. `split` là tên chuẩn; tên thư mục dev nếu có được adapter ánh xạ thành validation.
- Giữ nguyên thứ tự và phân hoạch nguồn. Loader không shuffle, chia lại hoặc âm thầm bỏ dòng. UTF-8 BOM được chấp nhận nếu có.
- File thiếu: FileNotFoundError; schema/mã nhãn/số dòng lệch/text chỉ khoảng trắng: ValueError có vị trí/id và nguyên nhân. Không âm thầm ép kiểu nhãn lạ hoặc bỏ dòng lỗi; Data báo leader trước khi thay chính sách xử lý.

`ml/labels.py` cung cấp `SENTIMENT_LABELS = ("negative", "neutral", "positive")`, `TOPIC_LABELS = ("lecturer", "curriculum", "facility", "other")` và bảng chuyển mã nguồn được Data đối chiếu khi tải thật. Canonical labels là hợp đồng; nếu bản tải không khớp mã nguồn tham khảo, không tự đảo mapping mà ghi nguồn và xin leader duyệt adapter.

## 3. Chuẩn hóa — áp dụng trong pipeline

`ml/preprocessing.py` cung cấp `normalize_text(text: str) -> str`: kiểm tra kiểu string, Unicode NFC, `.lower()`, thay chuỗi whitespace bằng một space và strip hai đầu. Chuỗi rỗng có thể trả rỗng để unit test; loader/API ngăn input rỗng trước train/suy luận. Sai kiểu ném TypeError.

Ở bước chuẩn hóa không xóa dấu tiếng Việt, dấu câu, chữ số hoặc từ phủ định/stop words; không sửa teencode hoặc tách từ bằng thư viện ngoài trong P0. TF-IDF vẫn chọn token bằng token_pattern ở mục 5, nên dấu câu không trở thành token riêng. Thí nghiệm tiền xử lý khác baseline v1.0 phải có quyết định riêng nếu thêm.

TF-IDF dùng `preprocessor=normalize_text` và `lowercase=False`; không thêm bước normalize khác trong loader/Backend/Frontend. Hàm phải được import từ `ml.preprocessing`, không định nghĩa lambda hoặc hàm trong notebook khiến joblib không tải lại ở tiến trình khác.

## 4. Gói M1 tối thiểu và dữ liệu trùng

M1 có nguồn/quyền sử dụng đã chấp thuận, bảng mã đối chiếu, loader/normalize/labels có tests, ba split đọc được và `reports/data/manifest.json`.

Manifest ghi schema_version 1.0, URL/revision hoặc định danh bản dữ liệu, bằng chứng quyền dùng, đường dẫn tương đối và SHA-256 file nguồn, số row từng split, số lượng từng nhãn, số rỗng/nhãn lạ, trùng trong split và giao nhau giữa split. Không ghi thông tin riêng tư hoặc toàn bộ câu vào manifest public.

Mặc định giữ split chính thức và không tự deduplicate để giữ khả năng so sánh baseline. Data báo trùng trong/giữa split, leader ghi giới hạn và quyết định trước training. Không thay split hoặc xử lý khác nhau giữa hai task, không tuyên bố đã loại sạch nguy cơ rò rỉ khi chỉ kiểm tra fit. Nếu có lỗi nguồn cần thay dữ liệu/split, đóng băng revision/manifest mới trước thí nghiệm.

Data tiếp tục EDA/biểu đồ/report sau M1; không buộc hai người mô hình chờ toàn bộ EDA hoàn thành.

## 5. Pipeline và baseline cho từng nhiệm vụ

Hai người dùng cùng cấu hình baseline nhưng code/file riêng. Train/predict bằng list raw strings; target là cột sentiment hoặc topic chuỗi chuẩn. Không đưa id/split/nhãn còn lại thành feature.

| Thành phần | Giá trị baseline v1.0 |
| --- | --- |
| TF-IDF | ngram_range=(1,2), min_df=2, max_df=1.0, sublinear_tf=True, norm=l2, strip_accents=None, lowercase=False, preprocessor=normalize_text |
| Token pattern | `(?u)\b\w+\b` — giữ token một ký tự, không thêm word segmenter |
| MultinomialNB | alpha=1.0 |
| LogisticRegression | C=1.0, solver=lbfgs, max_iter=2000, class_weight=None, random_state=42 |
| LinearSVC | C=1.0, dual=auto, max_iter=5000, class_weight=None, random_state=42 |
| Thứ tự pipeline | tfidf → classifier |

Không grid search trong P0 baseline; đủ ba mô hình mỗi nhiệm vụ. Mọi bước fit chỉ học train. Train phải có đủ toàn bộ nhãn task; thiếu nhãn là lỗi kiểm tra dữ liệu. Giữ seed 42 tại nơi thuật toán có tham số random_state; không cam kết bitwise-identical giữa các hệ điều hành.

Mỗi task cung cấp các giao diện trong module riêng:

```python
# ml/train_sentiment.py hoặc ml/train_topic.py
def train_models(train_frame: pandas.DataFrame) -> dict[str, sklearn.pipeline.Pipeline]: ...
def select_model(models: dict[str, sklearn.pipeline.Pipeline], validation_frame: pandas.DataFrame) -> dict[str, Any]: ...
# ml/evaluate_sentiment.py hoặc ml/evaluate_topic.py
def evaluate_models(models: dict[str, sklearn.pipeline.Pipeline], frame: pandas.DataFrame) -> dict[str, Any]: ...
# ml/predict_sentiment.py hoặc ml/predict_topic.py
def predict_texts(pipeline: sklearn.pipeline.Pipeline, texts: list[str]) -> list[str]: ...
```

Model keys là nb, logistic_regression, linear_svm. `train_models` kiểm tra mọi row có split=train, `select_model` kiểm tra split=validation, sai thì ValueError. Hàm trong mỗi module biết task của mình, không dùng biến target toàn cục do task khác sửa. `predict_texts` giữ thứ tự/độ dài, trả nhãn chuẩn và trả [] với input []; list có item sai kiểu/blank thì ValueError. Batch/API giới hạn 5000 code point riêng, không đưa giới hạn web vào việc đọc corpus nguồn.

## 6. Chọn mô hình và đánh giá cuối

`select_model` chỉ đọc validation, trả object gồm algorithm, metric (=macro_f1), validation_metrics. Chọn Macro F1 cao nhất; chênh lệch <= 0.000001 coi hòa, so tiếp Accuracy cùng tolerance; còn hòa dùng thứ tự cố định nb → logistic_regression → linear_svm. Không lấy tốc độ hoặc điểm test để phá hòa trong v1.0.

Sau khi ghi mô hình thắng và đóng băng ba cấu hình, đánh giá cả ba trên test một lần để có bảng so sánh đầy đủ. Mô hình có điểm test cao hơn không thay winner đã chọn bằng validation. Không fit lại trên train+validation trong baseline, không chỉnh cấu hình sau khi nhìn test cuối; thí nghiệm bổ sung phải đánh dấu riêng và giữ nguyên kết quả baseline.

Metrics mỗi thuật toán/split có đúng các key `accuracy`, `macro_precision`, `macro_recall`, `macro_f1`, `per_class`, `confusion_matrix`, `label_order`, `n_rows`. Bốn score là số từ 0 đến 1; per_class là mảng object label/precision/recall/f1/support theo label_order, support/n_rows là số nguyên không âm. Macro dùng labels theo thứ tự constants ở mục 2, average=macro, zero_division=0. Confusion Matrix hàng=nhãn thật, cột=dự đoán, phần tử nguyên không âm và cùng label_order. Ghi số liệu đầy đủ ở JSON, chỉ làm tròn khi trình bày; validation và test tách field rõ.

`evaluate_models` trả object theo ba model keys (hoặc tập model keys được truyền vào), mỗi value là metrics object trên; không fit hoặc tự chọn winner. Lưu `reports/metrics/<task>/comparison.json`, `reports/figures/<task>/confusion_matrix.png` của winner và phân tích lỗi trong `docs/<task>/report.md`. comparison.json có contract_version, task, dataset_manifest_sha256, configuration, selection (cùng object algorithm/metric/validation_metrics từ select_model), validation và test theo ba model keys. Không ghi chỉ số tự đặt trước khi chạy.

## 7. Artifact bàn giao và metadata

| Task | Pipeline | Metadata |
| --- | --- | --- |
| sentiment | models/sentiment_pipeline.joblib | models/sentiment_metadata.json |
| topic | models/topic_pipeline.joblib | models/topic_metadata.json |

Pipeline là sklearn Pipeline đã fit gồm TF-IDF + classifier, nhận list raw strings và trả list/array nhãn chuỗi. Không tách vectorizer thành artifact thứ ba. Trên pipeline `.classes_` có thể sắp xếp khác thứ tự canonical; Backend đối chiếu **tập** class, metrics vẫn dùng label_order chuẩn.

Metadata mỗi task bắt buộc có các trường sau:

| Field | Kiểu/nội dung |
| --- | --- |
| contract_version | string 1.0 |
| task | sentiment hoặc topic, khớp file được tải |
| algorithm | một trong ba model keys |
| artifact_filename | tên pipeline của chính task, không chứa thư mục khác |
| artifact_sha256 | 64 ký tự hex SHA-256 của artifact thật |
| labels | mảng labels chuẩn theo thứ tự task |
| python_version | phiên bản đầy đủ dùng train |
| package_versions | object phiên bản đầy đủ numpy, scipy, pandas, scikit-learn, joblib |
| dataset_manifest_sha256 | SHA-256 manifest dùng train |
| preprocessing | object name=ml.preprocessing.normalize_text, version=1.0 |
| parameters | object cấu hình TF-IDF và classifier thực tế |
| selection | object algorithm/metric=macro_f1, validation_metrics thật |
| trained_at | ISO 8601 UTC của lần train |

Backend kiểm tra schema/task/labels/checksum trước khi nạp; Python major.minor phải bằng 3.13 và package_versions của năm gói phải khớp chính xác môi trường khóa dùng cho server. Chỉ joblib.load artifact do nhóm bàn giao từ nguồn tin cậy. Thiếu artifact/metadata → missing, schema/checksum/môi trường/load/class sai → invalid. Chỉ cả hai ready mới suy luận. [Hướng dẫn scikit-learn](https://scikit-learn.org/stable/model_persistence.html) không hỗ trợ coi việc tải model khác phiên bản thư viện là tương thích mặc định.

## 8. Hợp đồng CLI để bàn giao

Trong Phase 3, mỗi task triển khai CLI tương ứng:

```text
python -m ml.train_sentiment --data-dir data/raw --output-dir models --report-dir reports/metrics/sentiment
python -m ml.train_topic --data-dir data/raw --output-dir models --report-dir reports/metrics/topic
python -m ml.evaluate_sentiment --data-dir data/raw --pipeline models/sentiment_pipeline.joblib --output-dir reports/metrics/sentiment
python -m ml.evaluate_topic --data-dir data/raw --pipeline models/topic_pipeline.joblib --output-dir reports/metrics/topic
```

Train orchestrates train → validation → select/freeze → test evaluation → xuất winner/metadata/comparison. Evaluate chỉ tải winner/metadata đã có và đánh giá test để kiểm chứng, lưu selected_test.json riêng; không fit, chọn lại hoặc ghi đè comparison.json. Các lệnh này là giao diện yêu cầu cho thành viên, chưa phải lệnh chạy được từ file code trống hiện tại.

M2 cần artifact thật + metadata + checksum, hướng dẫn nhận/cài môi trường, ít nhất một tập câu đối chiếu trước/sau tải lại và log tests. Model không được tạo file rỗng để giả làm đã có; quyền phân phối theo nguồn dữ liệu cần được xem xét trước khi công bố.
