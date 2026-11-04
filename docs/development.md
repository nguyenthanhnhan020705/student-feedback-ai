# Môi trường demo local — Phase 1

Bản tích hợp: `D:\N.ThanhNhan\Project_AI\student-feedback-ai\.local-tools\integration-p0`, nhánh `feature/integration-p0`. Bản gốc thành viên được giữ nguyên. Môi trường: Windows, CPython 3.13.3 64-bit.

## Cài và chạy

Trong thư mục bản tích hợp, dùng Python 3.13. Không tạo đè venv đã có; có thể đổi tên môi trường mới.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

Mở `http://127.0.0.1:8000/`; health `/api/health`, tài liệu API `/docs`. Ctrl+C để dừng; restart sau khi thay model. Không cần API key, Node, GPU hay database. Suy luận dùng model local, không gọi dịch vụ ngoài.

Chạy từ thư mục bất kỳ:

```powershell
$project = 'D:\N.ThanhNhan\Project_AI\student-feedback-ai\.local-tools\integration-p0'
& "$project\.venv\Scripts\python.exe" -m uvicorn backend.main:app --app-dir $project --host 127.0.0.1 --port 8000
```

Model mặc định lấy từ `<bản tích hợp>/models`, độc lập cwd. Nếu thay vị trí, đặt biến môi trường bằng đường dẫn tuyệt đối:

```powershell
$env:SFAI_MODEL_DIR = 'D:\duong-dan\models'
```

Bỏ override bằng `Remove-Item Env:SFAI_MODEL_DIR -ErrorAction SilentlyContinue`. `.env.example` chỉ là tài liệu; không tự nạp `.env`.

Cần `sentiment_pipeline.joblib`, `topic_pipeline.joblib` và hai file metadata. Thiếu model vẫn mở UI/API được: health `ready: false`, predict 503. Bản tích hợp đã có dữ liệu/model local; clone Git không tự có các file bị ignore. Quyền nguồn vẫn `unknown`, chưa có bước công bố/phân phối dataset/model.

## Các bộ dependencies

- `requirements.txt`: constraints runtime/ML và nbformat.
- `requirements-test.txt`: pytest/httpx; `requirements-lock.txt` khóa chung runtime/ML/unit/integration tests và nbformat.
- `requirements-browser-lock.txt`: bộ đầy đủ kèm Playwright/pytest-playwright; cài thêm để chạy browser tests. Suite dùng Chrome và Edge đã cài, channel `chrome`/`msedge`.
- `requirements-docs-lock.txt`: công cụ Word/PowerPoint, cài vào `.venv-tools` riêng; không cần để chạy API.

Năm gói khớp metadata cả hai model: NumPy 2.5.4, SciPy 1.18.1, pandas 2.3.3, scikit-learn 1.6.1, joblib 1.6.0. Không tự nâng phiên bản. Lock được kiểm trên Windows Python 3.13, chưa xác minh hệ điều hành khác. Kernel notebook tương tác (`ipykernel`, `nbclient`) chưa nằm trong runtime lock; được kiểm riêng trong Phase 2.

## Kiểm chứng

```powershell
.\.venv\Scripts\python.exe reports/verify_phase1.py
.\.venv\Scripts\python.exe -m pytest tests/test_health.py tests/integration/test_prediction_flow.py -q
```

Script ghi nguồn và hash, kiểm import/phiên bản, chạy HTTP server với model thật và model rỗng từ cwd ngoài repo, dừng tiến trình sau kiểm tra. Bằng chứng: `reports/evidence/phase-1/`; inventory ở `reports/evidence/phase-6/source-inventory.json` theo đường dẫn kế hoạch.

Phase 3: 119 tests Backend/tích hợp đạt; JSON UTF-8 sai đã trả 422 đúng envelope. Kiểm chứng HTTP thật từ cwd ngoài repo và hướng dẫn kiểm lại ở `reports/evidence/phase-3/README.md`. Review ghi nhận một lỗi nhỏ sẵn có: khóa JSON chứa lone surrogate bị từ chối 422 nhưng detail field là `body` thay vì `$body`.

Phase 4 (2026-10-31) đã sửa lỗi chấp nhận nhãn prototype/sai kiểu và timeout chưa bao gồm đọc body. Kiểm thử Frontend đạt 42 tests trên Chrome/Edge; toàn suite với dữ liệu thật đạt 224 tests, không skip, 12 cảnh báo thư viện đã biết. Xem `reports/evidence/phase-4/README.md`. Kết quả regression này chưa thay nghiệm thu tổng thể và đóng gói demo ở Phase 5.

Để chạy toàn suite sau khi cài browser tooling: đặt `$env:TV2_RUN_REAL_DATA='1'`, dùng Python venv chạy `-m pytest -q`. Nghiệm thu toàn bộ thuộc Phase 5.

## Bàn giao và diễn tập Phase 5

Bắt đầu ở DEMO.md; kịch bản ở reports/demo-script.md; nghiệm thu ở docs/acceptance.md.
Suite Phase 5 đạt 224 tests, không skip, 12 warnings; Chrome/Edge đã diễn tập
startup/restart/thiếu model/phục hồi từ cwd ngoài repo dưới network guard.
Log/ảnh/thời gian: reports/evidence/phase-5/.

```powershell
./.venv/Scripts/python.exe reports/verify_phase5.py
./.venv/Scripts/python.exe reports/package_demo.py
```

Gói mặc định ở .local-tools/phase5-delivery/. Nếu đã tồn tại, chọn
--destination .local-tools/phase5-delivery-new, không xóa đè.
ZIP kèm dataset/model nội bộ, không kèm venv/Python/browser/wheel cache.
Cài dependencies lần đầu có thể cần mạng. Phase 6 Word/PPTX chưa làm.
