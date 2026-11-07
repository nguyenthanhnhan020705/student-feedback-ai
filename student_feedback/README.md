# student_feedback — dự án độc lập phân tích phản hồi sinh viên

Một project root riêng, **không phụ thuộc mã nguồn cũ** (`demo_v2`, `demo_v3`, `backend`, `ml`, `reports` ở repo cha).
Gồm: web 3 tab + API 3.0 (FastAPI), quy trình dữ liệu → huấn luyện → đánh giá → thí nghiệm, notebook, kiểm thử và tài liệu.
Có thể sao chép nguyên thư mục này ra ngoài repo.

## Cài đặt (Python 3.13, Windows/macOS/Linux)

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements/lock.txt
.\.venv\Scripts\python.exe -m pip install -e . --no-deps
# Tùy chọn: .\.venv\Scripts\python.exe -m pip install playwright pytest httpx   # test và browser test
```

Mọi lệnh dùng `feedback-ai --project-root <thư mục này> ...` (hoặc `python -m feedback_ai`). Đường dẫn tương đối được
tính từ `--project-root`, không phụ thuộc thư mục làm việc. `.env.example` chỉ là tài liệu, `.env` **không** tự được nạp.

## Dữ liệu và model đã có trong Git

Checkout này bao gồm `data/raw`, `data/visualize/simple_data_visualization.ipynb`
và bundle `artifacts/serving`. Thành viên không cần import từ checkout cũ
hoặc huấn luyện lại để chạy ứng dụng.

Xem [hướng dẫn clone và chạy local](docs/local-setup.md) cho Windows/macOS/Linux
và cách xem/chạy notebook. Bundle được kiểm tra checksum từng file khi nạp.

## Chạy ứng dụng

```powershell
feedback-ai --project-root . serve            # http://127.0.0.1:8003 (đổi bằng --port / --host)
```

Thiếu hoặc hỏng bundle: giao diện và `/api/health` vẫn chạy (`ready=false`), dự đoán trả `503 MODEL_NOT_READY`.
API: `GET /api/health`, `POST /api/v3/predict`, `/api/v3/import`, `/api/v3/analyze-row`, `/api/v3/export`, `GET /mau-phan-hoi.xlsx`.

## Quy trình dữ liệu, huấn luyện, đánh giá

```powershell
feedback-ai --project-root . data validate                      # kiểm tra 3 split, ghi data/manifest.json
feedback-ai --project-root . data eda --output outputs/eda      # thống kê + biểu đồ nhãn/độ dài
feedback-ai --project-root . train --task sentiment --output outputs/run1/sentiment
feedback-ai --project-root . train --task topic --output outputs/run1/topic
feedback-ai --project-root . evaluate --task topic --artifact outputs/run1/topic/topic_pipeline.joblib --output outputs/run1/eval-topic
feedback-ai --project-root . experiment baseline --config configs/baseline.json --output outputs/exp/baseline
```

`train`/`experiment`/`evaluate` luôn ghi vào thư mục **mới**; từ chối thư mục đã có hoặc nằm trong `serving`. Model vừa huấn luyện
**không bao giờ tự thay model phục vụ**. Chọn thuật toán chỉ dùng validation; test chỉ dùng để báo cáo. Xem [docs/training.md](docs/training.md).

Thí nghiệm có sẵn: `baseline`, `class_weights`, `word_char`, `augmentation`, `selective` (cấu hình mẫu trong `configs/`).
`word_char` và `augmentation` cần model kiểm soát CT2/CT3 do thí nghiệm trước tạo ra — dùng `tools/fill_checksums.py` để điền checksum.

## Kiểm thử

```powershell
python -m pytest tests/unit -q --basetemp=outputs/tmp-pytest                  # không cần artifact/dữ liệu riêng tư
python -m pytest tests -q --basetemp=outputs/tmp-pytest                       # toàn bộ (cần dữ liệu, bundle, Chrome và Edge)
python -m pytest tests -m "not browser" -q --basetemp=outputs/tmp-pytest      # bỏ browser test
$env:TV2_RUN_REAL_DATA='1'                                                    # bật 3 test dữ liệu thật trong tests/unit/test_data.py
```

Test `integration`, `parity`, `browser` **fail rõ ràng** nếu thiếu bundle/trình duyệt (không âm thầm skip). Chi tiết ở [docs/operations.md](docs/operations.md).

## Giới hạn cần biết

- Hai bộ nhãn khác nhau: **baseline** (3 nhãn cảm xúc, 4 nhãn chủ đề UIT-VSFC) và **serving v3** (nhãn hỗn hợp/chưa xác định, nhiều chủ đề, theo luật + bundle đóng băng). Điểm baseline **không** chứng minh độ chính xác của nhãn v3.
- 5000 ký tự Unicode/phản hồi, 500 phản hồi/đợt, 5 MiB/file; không có tài khoản, lịch sử hay database.
- CT1–CT5 chưa được chạy lại toàn bộ; xem trạng thái ở [docs/evaluation.md](docs/evaluation.md).

Tài liệu: [kiến trúc](docs/architecture.md) · [dữ liệu](docs/data.md) · [huấn luyện](docs/training.md) · [đánh giá](docs/evaluation.md) · [vận hành](docs/operations.md).
