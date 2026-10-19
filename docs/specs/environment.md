# Môi trường và cách vận hành v1.0

**Trạng thái:** Leader đã duyệt cùng Phase 0 v1.0 ngày 2026-10-19. Chỉ runtime máy hiện tại đã được đọc: Python 3.13.3, 64-bit; chưa cài/chạy bộ dependencies hoặc ứng dụng cho bản triển khai này.

## 1. Quyết định môi trường

- CPython 3.13.x 64-bit, bản thường có GIL; Windows PowerShell là môi trường hướng dẫn chính. Không dùng Python 2.7/ArcGIS hoặc Python Anaconda cũ cho project.
- Mỗi thành viên dùng `.venv` riêng từ cùng Python minor và cùng bộ lock của leader, không cài đè môi trường Python hệ thống.
- P0: pandas/NumPy/scikit-learn/joblib cho ML, FastAPI/Pydantic/Uvicorn cho web, HTML/CSS/JavaScript thuần. Không cần Node/npm, database, GPU hoặc dịch vụ cloud.
- Artifact train và server dùng cùng bộ phiên bản ML đã khóa. Một người không tự nâng thư viện riêng rồi bàn giao model cho môi trường khác.

## 2. Giới hạn dependencies để leader khóa ở Phase 1

| Gói | Constraint đầu vào của bộ lock |
| --- | --- |
| numpy | >=2.1,<3 |
| scipy | >=1.14.1,<2 |
| pandas | >=2.2.3,<3 |
| scikit-learn | ==1.6.1 |
| joblib | >=1.4.2,<2 |
| matplotlib | >=3.10,<4 |
| fastapi | >=0.115.12,<1 |
| pydantic | >=2.11,<3 |
| uvicorn | >=0.34,<1 |
| python-multipart | >=0.0.20,<1, chỉ cần khi làm P1 |
| pytest | >=8.3.5,<9 |
| httpx | >=0.28,<0.29 |
| nbformat | >=5.10.4,<6 |
| playwright | >=1.52,<2, bộ kiểm tra trình duyệt |
| pytest-playwright | >=0.7,<1, bộ kiểm tra trình duyệt |

Đây là constraints cụ thể để resolver tạo bộ lock, không phải khẳng định mọi tổ hợp trong khoảng đã được kiểm thử. Leader resolve/cài trên CPython 3.13 tại Phase 1, kiểm tra import/chạy tests nền tảng rồi công bố `requirements-lock.txt` đầy đủ dependencies trực tiếp/gián tiếp với phiên bản exact, cùng `requirements-browser-lock.txt` cho browser tooling. Cả nhóm dùng cùng bộ lock trước train; cập nhật lock phải có review. Nếu resolver không giải được, leader sửa constraint và ghi quyết định v1.x trước khi tiếp tục.

`pandas 2.2.3` có hỗ trợ Python 3.13 trong [release notes](https://pandas.pydata.org/pandas-docs/version/2.2/whatsnew/v2.2.3.html); scikit-learn 1.6 hỗ trợ Python 3.9–3.13 theo [tài liệu cài đặt](https://scikit-learn.org/stable/install.html). [FastAPI 0.115.12](https://pypi.org/project/fastapi/0.115.12/) khai báo Python 3.13. Đây là kiểm tra nguồn, chưa thay thế chạy môi trường thật.

## 3. File cấu hình do leader quản lý

- Root requirements/config hiện tiếp tục để trống trong Phase 0. Phase 1 đưa constraints vào root requirements phù hợp, resolve và thêm lock mới; cập nhật manifest khi file không còn là placeholder.
- `requirements/<vai-tro>.txt` chứa đề xuất dependencies riêng; không tự cài phiên bản lệch lock nhóm hoặc sửa root requirements từ nhánh phần việc khác.
- `pytest.ini`: đặt testpaths=tests, marker integration/browser; unit tests không yêu cầu dataset/model thật, integration/browser nghiệm thu cần môi trường/artifact thật. Thiếu artifact được báo/skip khi dev nhưng không được tính là đạt nghiệm thu.
- `.env.example`: chỉ tài liệu biến môi trường, không có bí mật. V1.0 không yêu cầu thư viện đọc .env; Backend đọc biến môi trường hệ điều hành bằng os.environ. Không ngầm giả định tạo .env là server đã nạp được biến.
- Biến v1.0 cho vị trí model là `SFAI_MODEL_DIR`, mặc định `<repo>/models`; resolve từ vị trí mã nguồn, không phụ thuộc shell đang đứng thư mục nào. Không có biến đổi ngầm sang model giả.

## 4. Lệnh mục tiêu sau khi Phase 1 triển khai

Chạy từ repository root với `python` đã kiểm tra là CPython 3.13 64-bit. Không dùng `py` không chỉ phiên bản vì launcher hiện tại còn thấy môi trường ArcGIS cũ.

```powershell
python --version
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

Mở `http://127.0.0.1:8000/`, `/api/health` và `/docs`. Server phục vụ frontend cùng origin; không cần bật CORS cho demo v1.0. Backend load model một lần khi startup; thay artifact thì restart.

```powershell
.\.venv\Scripts\python.exe -m pytest -q -m "not integration and not browser"
.\.venv\Scripts\python.exe -m pip install -r requirements-browser-lock.txt
.\.venv\Scripts\python.exe -m playwright install chromium
.\.venv\Scripts\python.exe -m pytest -q -m "integration or browser"
```

Browser/integration chỉ là lệnh mục tiêu sau khi tests đã được viết và có artifact thật; không chạy file trống rồi ghi là pass. Notebook có thể mở trong VS Code/Jupyter phù hợp; việc chọn kernel phải trỏ đúng `.venv`. Backend/UI tests cần log và phiên bản trình duyệt thực tế, không chỉ chụp mockup.

## 5. Những việc kiểm chứng chuyển cho phase sau

Phase 1 chịu trách nhiệm lock/import/server/static/tests nền tảng. Data chịu trách nhiệm nguồn/quyền dùng, số dòng, mapping và manifest ở M1. Hai người ML chịu trách nhiệm thí nghiệm/artifact thật ở M2. Đây là đầu ra triển khai đã được giao người/mốc, không phải chỗ trống của schema Phase 0.
