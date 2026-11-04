# Backend API Notes

## Cập nhật TV5 — 2026-10-28

P0 đã được bổ sung kiểm thử độc lập với TV2–TV4. Dùng Python 3.13.x và môi trường riêng; bộ phiên bản thực tế ở `reports/evidence/backend/requirements-local.txt` chỉ là bằng chứng local, chưa thay bộ lock chính thức của leader.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements/backend.txt
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

API phục vụ `frontend/index.html` tại `/`, các asset P0 `/app.js`, `/api.js`, `/styles.css` cùng origin. File Frontend trên nhánh Backend vẫn là placeholder; cần leader tích hợp UI của TV6 để hiển thị giao diện thật. `/docs`, `/api/health` và `/api/predict` hoạt động độc lập. Không bật CORS hoặc endpoint P1.

Lỗi không dự kiến được trả bằng JSON `INTERNAL_ERROR`, không lộ stack trace/đường dẫn. Kết quả suy luận sai kiểu/nhãn trả `INFERENCE_ERROR`, không trả kết quả một phần.

Tests loader dùng pipeline sklearn huấn luyện trên dữ liệu tổng hợp trong thư mục tạm; kiểm tra load/reload, checksum, metadata, class, phiên bản và lỗi artifact. Tests API dùng test double để xác nhận hợp đồng. Không có artifact giả trong `models/`, không có fallback nhãn mẫu trên API chạy thật.

Khi nhận artifact thật: đặt đủ hai `.joblib` và hai metadata v1.0 vào `models/` (hoặc `SFAI_MODEL_DIR`), cài đúng phiên bản ML được nhóm khóa, rồi restart server. Kiểm tra health ready và đối chiếu API với gọi trực tiếp hai pipeline. Tích hợp này cùng nghiệm thu trình duyệt đang chờ M2-S/M2-T.

## 1. Tổng quan

Backend sử dụng FastAPI để cung cấp API phân tích phản hồi sinh viên theo hợp đồng dữ liệu v1.0.

- `GET /api/health`: kiểm tra trạng thái API và mức độ sẵn sàng của hai mô hình.
- `POST /api/predict`: nhận một phản hồi và trả về nhãn cảm xúc, nhãn chủ đề.
- Phiên bản hợp đồng: `1.0`.

Backend không tự tạo nhãn dự đoán giả khi mô hình chưa sẵn sàng.

## 2. Môi trường

- Python: 3.13.x (môi trường hiện tại đã kiểm tra: Python 3.13.11).
- FastAPI, Pydantic, Uvicorn, scikit-learn và joblib được sử dụng trong Backend.
- Môi trường phát triển: virtual environment `.venv`.

## 3. Cách chạy

Tại thư mục gốc của repository, kích hoạt môi trường ảo trong PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Chạy API:

```powershell
python -m uvicorn backend.main:app --reload
```

Mặc định, API chạy tại `http://127.0.0.1:8000`.

Mở tài liệu API tương tác tại `http://127.0.0.1:8000/docs`.

Có thể cấu hình thư mục chứa model bằng biến môi trường `SFAI_MODEL_DIR`. Nếu không cấu hình, Backend sử dụng thư mục `models` ở thư mục gốc repository.

## 4. Health API

### Request

```http
GET /api/health
```

### Response mẫu khi chưa có model

```json
{
  "status": "ok",
  "ready": false,
  "models": {
    "sentiment": "missing",
    "topic": "missing"
  },
  "contract_version": "1.0"
}
```

`status` vẫn là `ok` khi API hoạt động nhưng model chưa sẵn sàng. `ready` chỉ là `true` khi cả hai model đã sẵn sàng. Trạng thái từng model có thể là `ready`, `missing` hoặc `invalid`.

## 5. Predict API

### Request

```http
POST /api/predict
Content-Type: application/json
```

Ví dụ body:

```json
{
  "text": "Giảng viên giải thích bài học rất dễ hiểu."
}
```

`text` phải là chuỗi có từ 1 đến 5000 ký tự Unicode và không được chỉ chứa khoảng trắng. Backend giữ nguyên chuỗi đầu vào khi chuyển cho service dự đoán.

### Response thành công

```json
{
  "sentiment": "positive",
  "topic": "lecturer",
  "contract_version": "1.0"
}
```

Các nhãn sentiment được chấp nhận: `negative`, `neutral`, `positive`.

Các nhãn topic được chấp nhận: `lecturer`, `curriculum`, `facility`, `other`.

Đây là ví dụ về định dạng phản hồi, không phải kết quả dự đoán thật đã được xác nhận.

## 6. Lỗi API

Các lỗi dùng chung cấu trúc:

```json
{
  "error": {
    "code": "INVALID_INPUT",
    "message": "Dữ liệu đầu vào không hợp lệ.",
    "details": [
      {
        "field": "text",
        "reason": "blank"
      }
    ]
  },
  "contract_version": "1.0"
}
```

| HTTP status | Error code | Ý nghĩa |
|---|---|---|
| 422 | `INVALID_INPUT` | JSON hoặc dữ liệu đầu vào không hợp lệ |
| 503 | `MODEL_NOT_READY` | Một hoặc cả hai model chưa sẵn sàng |
| 500 | `INFERENCE_ERROR` | Lỗi dự đoán hoặc kết quả model không hợp lệ |
| 500 | `INTERNAL_ERROR` | Lỗi nội bộ khác, theo hợp đồng |

Các `reason` đầu vào có thể gồm `required`, `type`, `too_long`, `blank`, `extra_field`, `invalid_json`. `field` có thể là `text`, tên trường thừa hoặc `$body`.

## 7. Kiểm thử

Lệnh chạy toàn bộ test hiện có:

```powershell
python -m pytest -q
```

Kết quả kiểm thử ban đầu trước đợt bổ sung TV5: **9 passed, 1 warning**. Kết quả mới và danh sách phiên bản được lưu tại `reports/evidence/backend/pytest-local.txt` và `requirements-local.txt`.

Các test hiện có bao gồm health khi thiếu model, model chưa sẵn sàng, input rỗng, vượt giới hạn, thiếu trường, sai kiểu, trường thừa, JSON không hợp lệ và lỗi suy luận.

## 8. Giới hạn và việc còn lại

- Chưa xác nhận dự đoán bằng hai artifact model thật.
- Cần kiểm thử thêm các trường hợp artifact hỏng hoặc không tương thích.
- Chưa nghiệm thu luồng tích hợp đầy đủ giữa website, API và hai pipeline.
- API batch/CSV thuộc P1, chỉ triển khai khi được leader phê duyệt.

## Trạng thái tích hợp Phase 3 — 2026-10-30

Các giới hạn lịch sử ở mục 8 phía trên đã được kiểm lại: hai model thật đã được
đối chiếu API/pipeline; thiếu/hỏng từng model và cwd ngoài repo có kiểm thử.
119 tests Backend/tích hợp đạt. JSON UTF-8 sai trả 422 theo envelope; metadata
kiểm toàn bộ metrics lồng nhau, Python version đầy đủ và thứ tự nhãn chuẩn.
Xem reports/evidence/phase-3/README.md để chạy lại bằng môi trường khóa Phase 1.
Còn minor: khóa JSON lone surrogate bị từ chối 422 nhưng field body chưa là $body.
UI và nghiệm thu toàn dự án vẫn chờ Phase 4–5; không coi toàn suite hiện tại xanh.
