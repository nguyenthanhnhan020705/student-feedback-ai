# UIT-VSFC — bàn giao TV2 Data v1.0 (local)

## Nguồn đã đối chiếu

- Tác giả/bài báo: [kietnv/uit-vsfc](https://github.com/kietnv/uit-vsfc), Nguyen et al., KSE 2018, DOI `10.1109/KSE.2018.8573337`.
- Nguồn tải: [UIT-NLP trên Hugging Face](https://huggingface.co/datasets/uitnlp/vietnamese_students_feedback), revision `7b56c6cb1c9c8523249f407044c838660df3811a`.
- Đã đọc dataset card và script loader ở revision trên; mapping sentiment/topic khớp hợp đồng Phase 0 v1.0.
- Tải đúng byte của 9 file Google Drive được script nguồn trỏ tới; không thực thi code nguồn tải về. URL `train/sentiments` có lỗi `export=down load`; công cụ tải sửa query thành `export=download` và lưu cả URL gốc/thực dùng.
- Google Drive không được version hóa bằng revision Hugging Face. Vì vậy SHA-256 của từng file trong `reports/data/source.json` và manifest là dấu nhận diện bắt buộc khi tái lập.
- Dataset card nguồn vẫn ghi license **unknown**. Bằng chứng local: `reports/evidence/data/uitnlp-dataset-card.md` và `uitnlp-loader-source.py.txt`. Không suy diễn Apache-2.0 của script thành giấy phép dataset. Chỉ kiểm tra kỹ thuật local, chưa training hoặc phân phối công khai. Xác nhận quyền sử dụng/leader duyệt còn chờ.

## File dữ liệu đã có trên local

```text
data/raw/
  train/{sents.txt,sentiments.txt,topics.txt}
  dev/{sents.txt,sentiments.txt,topics.txt}
  test/{sents.txt,sentiments.txt,topics.txt}
data/processed/
  train.csv
  validation.csv
  test.csv
```

`raw` giữ nguyên byte nguồn. `processed` là export schema chuẩn nhưng vẫn giữ raw text; không phải văn bản đã lower/chuẩn hóa. Cả hai thư mục được Git ignore.

Adapter đọc UTF-8, chấp nhận BOM và CRLF; ba file trong mỗi split phải cùng số dòng, không rỗng. Mỗi file một giá trị mỗi dòng. Có thể dùng thư mục `validation` thay `dev`; nếu cùng tồn tại, ưu tiên `validation`. API công khai chỉ nhận `train`, `validation`, `test`.

| Task | Mã nguồn đã đối chiếu | Nhãn chuẩn dự án |
| --- | --- | --- |
| sentiment | 0 / 1 / 2 | negative / neutral / positive |
| topic | 0 / 1 / 2 / 3 | lecturer / curriculum / facility / other |

`load_split(data_dir, split)` trả đúng `id,text,sentiment,topic,split`, mọi cell là string. ID theo vị trí nguồn, ví dụ `train:000001`. Loader giữ thứ tự/raw text, chỉ bỏ phân cách dòng vật lý; không shuffle, fit, deduplicate, lower hoặc đổi split.

Thiếu file → `FileNotFoundError`; split sai/rỗng, lệch dòng, text blank, nhãn sai → `ValueError`. Lỗi từng mẫu ghi ID/task. Không âm thầm bỏ/sửa dòng. CSV sentiment-only cũ không phải đầu vào của adapter hai nhiệm vụ.

## Cách tái lập từ repository root (PowerShell)

```powershell
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r reports/evidence/data/requirements-local.txt
# Chỉ tải để kiểm tra local; xác nhận quyền sử dụng trước training/phân phối.
.venv/Scripts/python.exe docs/data/acquire_dataset.py
.venv/Scripts/python.exe -m ml.data --data-dir data/raw --source-metadata reports/data/source.json --output reports/data/manifest.json
.venv/Scripts/python.exe -m ipykernel install --prefix .venv --name tv2-local --display-name 'TV2 local Python 3.13'
.venv/Scripts/python.exe docs/data/run_eda.py
$env:TV2_RUN_REAL_DATA='1'
.venv/Scripts/python.exe -m pytest -q
.venv/Scripts/python.exe -m pip check
```

`requirements-local.txt` là snapshot môi trường Data đã chạy thực tế, không thay bộ lock train/server chung do leader sở hữu. File đề xuất dependencies là `requirements/data.txt`. Không tự nâng dependency ML rồi bàn giao artifact sang server khác môi trường.

Công cụ acquisition sẽ tải lại nguồn và cập nhật metadata thời điểm tải; đối chiếu SHA-256 với bản manifest bàn giao trước khi dùng kết quả mới. Các nguồn mạng có thể thay đổi hoặc không truy cập được. Giữ byte và checksum local của lần đo này để tái lập chính xác.

`run_eda.py` chạy notebook bằng kernel `.venv`, đặt cache/history trong `.local-tools/`, lưu notebook có output và `notebook-execution.json`. Notebook xuất thống kê/biểu đồ trong `reports/data/`, CSV schema chuẩn trong `data/processed/` và manifest có metadata nguồn. Không tự chuyển trạng thái quyền sử dụng thành approved.

## Manifest và chính sách

Manifest ghi schema 1.0, URL/revision/bằng chứng nguồn, đường dẫn tương đối/SHA-256 từng file, số dòng/nhãn hai task, số rỗng/nhãn lạ và trùng trong/giữa split. Không chứa toàn bộ câu gốc. Dữ liệu lỗi khiến lệnh thất bại trước khi ghi manifest.

Mặc định giữ mẫu trùng và split chính thức theo hợp đồng. Có một câu xuất hiện hai lần trong train, không có giao nhau giữa split sau chuẩn hóa; xem [báo cáo](report.md). Leader ghi nhận giới hạn/quyết định trước training. Không coi đếm trùng là đã loại mọi nguy cơ rò rỉ.

`source.approval_status` còn `pending_leader_review`, `license_status` là `unknown`. Không dùng phần kiểm tra kỹ thuật để tuyên bố đã được phép phân phối hoặc M1 đã được leader nghiệm thu.

Manifest cũ từ CSV sentiment-only được giữ ở `reports/data/legacy_sentiment_manifest.json`, không dùng cho thí nghiệm hai task.
