# Báo cáo TV2 — Data

## Phạm vi và trạng thái

Hoàn thiện kỹ thuật **trên local** ngày 2026-10-28, nhánh `feature/data-preprocessing`. Đã có dữ liệu thật, loader/labels/chuẩn hóa, pytest, EDA có output, manifest/checksum và hướng dẫn tái lập. Chưa commit/push, chưa training model; không sửa phần TV3–TV6 hoặc hợp đồng chung.

**Nghiệm thu M1/AC-01 còn chờ xác nhận quyền sử dụng và leader duyệt.** Nguồn UIT-NLP ghi license unknown; đã lưu bằng chứng thay vì tự gán giấy phép. Đây là điều kiện ngoài kiểm tra kỹ thuật local.

## Dữ liệu và chất lượng đo được

Nguồn UIT-NLP `uitnlp/vietnamese_students_feedback`, revision `7b56c6cb1c9c8523249f407044c838660df3811a`; 9 file gốc tải trực tiếp từ URL trong script nguồn, đã lưu SHA-256. Xem `reports/data/source.json` và `manifest.json`.

| Split | Số câu | Text rỗng | Nhãn lạ | Số dòng thuộc nhóm trùng |
| --- | ---: | ---: | ---: | ---: |
| train | 11.426 | 0 | 0 | 2 |
| validation | 1.583 | 0 | 0 | 0 |
| test | 3.166 | 0 | 0 | 0 |

Ba file text/sentiment/topic của từng split khớp số dòng. Mỗi câu đủ hai nhãn. Không có dòng nguồn nào bị loại hoặc chỉnh sửa. Lỗi CSV validation 1585 trong báo cáo cũ không xuất hiện ở bộ file gốc này; không mang lỗi của bản CSV sentiment-only sang kết luận về nguồn mới.

### Phân bố cảm xúc

| Nhãn | Train | Validation | Test |
| --- | ---: | ---: | ---: |
| negative | 5.325 | 705 | 1.409 |
| neutral | 458 | 73 | 167 |
| positive | 5.643 | 805 | 1.590 |

Train neutral chỉ 4,01%, positive 49,39% và negative 46,60%. Neutral ít hơn rõ rệt; Accuracy có thể che khuất chất lượng lớp này. Giữ tiêu chí chọn model bằng Macro F1 trên validation theo hợp đồng, chưa có kết quả model trong phần Data.

### Phân bố chủ đề

| Nhãn | Train | Validation | Test |
| --- | ---: | ---: | ---: |
| lecturer | 8.166 | 1.151 | 2.290 |
| curriculum | 2.201 | 267 | 572 |
| facility | 497 | 70 | 145 |
| other | 562 | 95 | 159 |

Lecturer chiếm khoảng 71,47% train, facility khoảng 4,35%. Cần báo cáo từng lớp và Macro F1 khi huấn luyện; không cân bằng mẫu hoặc sửa split trong Data baseline.

### Độ dài và trùng lặp

| Split | Min ký tự | Median | Mean | Max |
| --- | ---: | ---: | ---: | ---: |
| train | 4 | 47 | 59,08 | 660 |
| validation | 4 | 45 | 56,36 | 718 |
| test | 4 | 46 | 58,84 | 411 |

Độ dài tính trên raw text theo Unicode code point, không phải byte. Không cắt văn bản.

So sánh trùng sau NFC/lowercase/gộp whitespace: train có 11.425 câu duy nhất trong 11.426 dòng (một nhóm gồm hai dòng). Validation/test không có trùng nội bộ. Giao nhau train–validation, train–test, validation–test đều 0 câu duy nhất. Giữ nguyên dữ liệu theo chính sách report-only; leader cần ghi nhận trước training. Chưa kết luận về near-duplicate hoặc mọi nguồn rò rỉ khác.

## Code và kiểm chứng

- `ml/data.py`: `load_split(data_dir, split)`, `load_dataset(data_dir)`; DataFrame `id,text,sentiment,topic,split`, giữ raw text và thứ tự. Fail fast khi thiếu file, lệch dòng, split rỗng, text blank hoặc nhãn lạ. Không làm mất ký tự Unicode phân cách trong nội dung câu.
- `ml/labels.py`: bảng nhãn/mapping hai nhiệm vụ đã đối chiếu dataset card và loader nguồn.
- `ml/preprocessing.py`: NFC, lower, whitespace; giữ dấu, phủ định, dấu câu, emoji và chữ số. Chỉ dùng trong TF-IDF pipeline, không áp dụng vào raw loader.
- Notebook dùng loader chung; không fit vectorizer/model; xuất CSV schema chuẩn, thống kê và ba biểu đồ. Bốn code cell đã chạy, không có error output.
- Full pytest: **25 passed** với `TV2_RUN_REAL_DATA=1`: 22 tests tự tạo và 3 tests dữ liệu thật (checksum nguồn, schema/raw text so với export, manifest tái lập).
- `pip check`: không có dependency lỗi. Phiên bản đầy đủ được lưu trong `reports/evidence/data/requirements-local.txt` và `environment.json`.

Môi trường local Data: Python 3.13.3; pytest 8.4.2; pandas 2.3.3. Không thay bộ lock ML/server chung. Khi không có dataset, chạy tests mặc định sẽ skip 3 tests thật; không coi skip là nghiệm thu dữ liệu.

Log/kết quả: `reports/evidence/data/pytest-local.txt`, `pip-check.txt`, `notebook-execution.json`, `validation-local.json`. Lệnh chạy lại ở [dataset.md](dataset.md).

## Đầu ra bàn giao local

- Dataset gốc: `data/raw/{train,dev,test}/`, 9 file, không track Git.
- Export schema chuẩn/raw text: `data/processed/{train,validation,test}.csv`, không track Git.
- `reports/data/manifest.json`, `source.json`, `summary.csv`, `sentiment_counts.csv`, `topic_counts.csv`.
- Biểu đồ: `reports/data/sentiment_distribution.png`, `topic_distribution.png`, `text_length_distribution.png`.
- Notebook EDA có output: `notebooks/01_eda.ipynb`.
- Hướng dẫn: `docs/data/dataset.md`, `preprocessing.md`; công cụ tải/chạy EDA: `acquire_dataset.py`, `run_eda.py`.

Ảnh và manifest sentiment-only cũ chỉ là bằng chứng lịch sử; không dùng để chứng minh bản này chạy. Đầu ra cũ thuộc thư mục Sentiment được giữ nguyên cho chủ sở hữu.

## Checklist TV2

- [x] Có nguồn/revision/bằng chứng đối chiếu mapping, file gốc local và checksum.
- [x] Loader/labels/chuẩn hóa đúng hợp đồng, có pytest trên fixture và dữ liệu thật.
- [x] EDA hai nhiệm vụ, độ dài, trùng nội bộ/giao split; không đổi dữ liệu nguồn.
- [x] Manifest, notebook output, biểu đồ, CSV thống kê và hướng dẫn tái lập.
- [x] Ghi rõ mất cân bằng lớp, mẫu trùng và giới hạn dữ liệu.
- [ ] Nguồn xác nhận quyền sử dụng; leader duyệt bằng chứng và quyết định mẫu trùng trước training.
- [ ] Review/merge/bàn giao qua develop: chưa thực hiện theo yêu cầu chỉ làm local.

## Cập nhật xác minh Phase 2 — 2026-10-30

Bản tích hợp đã chạy 63 tests Data/ML với dữ liệu thật, không skip; xem
`reports/evidence/phase-2/README.md` và `pytest-locked.txt`. Checksum 9 file,
schema/export và manifest khớp; split 11426/1583/3166 giữ nguyên. Một cặp trùng
trong train, không có text chuẩn hóa giao split. Chưa kiểm near-duplicates.
Nguồn vẫn license unknown. Kế hoạch mới cho phép demo kỹ thuật local, không
đồng nghĩa được phân phối; các mục chờ quyền nguồn phía trên là lịch sử M1.
