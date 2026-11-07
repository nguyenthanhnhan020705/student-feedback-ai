# Dữ liệu

**Nguồn:** UIT-VSFC (Vietnamese Students' Feedback Corpus, `uitnlp/vietnamese_students_feedback`), giữ ba split chính thức.
Không có dữ liệu trong Git (`data/**` bị ignore). Người dùng chịu trách nhiệm quyền sử dụng dữ liệu.

| Split | Số dòng (đã kiểm tra) |
| --- | --- |
| train | 11 426 |
| validation | 1 583 |
| test | 3 166 |

Mỗi split gồm `sents.txt`, `sentiments.txt`, `topics.txt` (song song theo dòng). `validation` có thể tên `dev` ở nguồn cũ; `data import` chuẩn hóa thành `validation`.

## Nhãn baseline

- Sentiment: `negative`, `neutral`, `positive` (mã nguồn 0/1/2). Topic: `lecturer`, `curriculum`, `facility`, `other` (mã 0–3).
- Ánh xạ chỉ thực hiện một lần ở loader (`common/labels.py`). Loader không loại dòng, không fit gì.

## Lệnh

| Lệnh | Việc |
| --- | --- |
| `data acquire` | Tải phiên bản nguồn đã ghim khi **bạn chủ động chạy**; từ chối nội dung HTML; không thực thi mã từ xa |
| `data import --source <dir>` | Sao chép + kiểm tra từ thư mục có sẵn vào `data/raw` |
| `data validate` | Kiểm tra số dòng/nhãn/độ dài, ghi `data/manifest.json` (train dùng manifest này để xác minh dữ liệu) |
| `data eda --output <dir>` | Phân bố nhãn và độ dài từng split (CSV + PNG + `summary.json`) |

Quan sát EDA thực tế (train): độ dài trung bình ≈ 59 ký tự, trung vị 47, tối đa 660.
Chuẩn hóa văn bản (`data/preprocessing.normalize_text`) được áp dụng trong pipeline, đúng một lần; UI/API gửi văn bản thô.

## Provenance (tùy chọn)

Nếu có `data/source.json` (nguồn đã ghim, SHA-256 từng file; nguồn gốc gọi split này là `dev`, project lưu là `validation`),
`data validate` ghi nó vào `data/manifest.json`, và test dữ liệu thật (`TV2_RUN_REAL_DATA=1`) kiểm tra byte file khớp bản ghi nguồn.
Không có `source.json` thì manifest chỉ ghi số dòng/nhãn, trường `source` để trống.
