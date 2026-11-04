# Bàn giao demo local — Student Feedback AI

Điểm bắt đầu cho người chạy demo. Bản làm việc: `.local-tools/integration-p0`
của checkout gốc, nhánh `feature/integration-p0`. Dùng chính thư mục chứa file này.

## Chạy

Nếu đã có `.venv` của bản tích hợp:

```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

Mở `http://127.0.0.1:8000/`. Dừng bằng Ctrl+C.
Nếu dùng gói ZIP local giải nén mới, tạo venv từ CPython 3.13.x 64-bit rồi cài lock:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
.\.venv\Scripts\python.exe -m pip check
```

Không chép `.venv` giữa máy. Việc cài mới cần nguồn package phù hợp; ZIP không
kèm Python, browser hoặc wheel cache. Windows là môi trường đã kiểm chứng.
Nếu PowerShell đang ở nơi khác, dùng đường dẫn tuyệt đối tới Python và
`--app-dir <thư-mục-giải-nén>` theo `docs/development.md`.

## Thành phần bàn giao

| Thành phần | Đường dẫn |
| --- | --- |
| API, giao diện, Data/ML | `backend/`, `frontend/`, `ml/` |
| Runtime/test/browser lock | `requirements*-lock.txt` |
| Hai model thật + metadata | `models/*_pipeline.joblib`, `models/*_metadata.json` |
| Dữ liệu local, notebook và metrics | `data/`, `notebooks/`, `reports/data/`, `reports/metrics/` |
| Cách chạy, kịch bản, nghiệm thu | `docs/development.md`, `reports/demo-script.md`, `docs/acceptance.md` |
| Bằng chứng Phase 5 | `reports/evidence/phase-5/` |

Gói local được tạo bởi `reports/package_demo.py` tại
`.local-tools/phase5-delivery/student-feedback-ai-local.zip`; manifest SHA-256
bên cạnh gói và trong gói. `package-verification.json` bên cạnh ZIP là biên bản
kiểm chứng chính gói đó; không nhúng hash/biên bản gói cũ vào ZIP mới.
Công cụ từ chối ghi đè gói cũ; chọn `--destination`
mới nếu cần tạo lại. Chỉ đóng gói file được liệt kê, không kèm Git, venv hoặc bí mật.

Đây là gói nội bộ local, có dataset/model không track Git. Không tự upload/phân phối.
Nguồn vẫn license unknown; không coi gói là giấy phép phát hành. Demo chạy local
không gọi dịch vụ ML ngoài; mock chỉ bật khi dùng tham số URL rõ ràng.

## Trạng thái bàn giao

Xem `docs/acceptance.md` và `reports/evidence/phase-5/README.md` để biết kết quả
thực tế, hạn chế và việc còn chờ leader. Phase 6 Word/PPTX chưa hoàn thành;
không có commit/push/merge hoặc nộp bài trong Phase 5.
