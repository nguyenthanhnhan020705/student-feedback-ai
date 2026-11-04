# Kịch bản demo P0 — Phase 5

Chạy từ bản tích hợp `.local-tools/integration-p0` của checkout gốc, nhánh
`feature/integration-p0`. Không chạy từ checkout Data hoặc thư mục lồng cùng tên.

## Chuẩn bị

- Windows, Python 3.13.x 64-bit; môi trường theo `requirements-lock.txt`.
- Hai pipeline và hai metadata trong `models/`. Không chạy notebook train để mở demo.
- Tắt server cũ nếu cổng 8000 đang dùng; kiểm biến `SFAI_MODEL_DIR` không trỏ nhầm nơi.
- Mở PowerShell tại bản tích hợp:

```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

Mở `http://127.0.0.1:8000/` bằng Chrome hoặc Edge, không thêm `?mock=...`.
Health phải báo “Mô hình sẵn sàng”. Không cần API key, GPU, database hoặc mạng ngoài
khi đã cài đủ dependencies và có artifact local. Cài dependencies ban đầu có thể cần mạng.

## Diễn tập khoảng 3–5 phút

1. Giới thiệu: một câu tiếng Việt → một nhãn cảm xúc và một nhãn chủ đề.
2. Nhập “Giảng viên giải thích bài tập rõ ràng và tận tình.” rồi Phân tích.
   Đọc hai nhãn thực tế; không hứa mọi câu sẽ đúng hoặc hiển thị confidence.
3. Nhập “Phòng học nóng và máy chiếu không hoạt động.” rồi Phân tích.
4. Nhập khoảng trắng: nút Phân tích bị khóa. Quá 5000 Unicode code point cũng bị khóa.
   API gọi trực tiếp với input không hợp lệ trả 422.
5. Nhập một câu hợp lệ. Dừng server bằng Ctrl+C, bấm Phân tích trên trang còn mở:
   có thông báo kết nối, giữ câu nhập và xóa kết quả cũ.
6. Chạy lại lệnh server, bấm Kiểm tra lại kết nối, rồi Phân tích để chứng minh phục hồi.
7. Trình bày giới hạn: neutral/other yếu, một nhãn mỗi nhiệm vụ, không hỗ trợ đầy đủ
   câu nhiều chủ đề hoặc mỉa mai. Không train lại theo các câu demo.

## Nhánh thiếu model (tùy thời gian trình bày)

Dừng server. Dùng một đường dẫn tuyệt đối đến thư mục không có artifact bằng biến
`SFAI_MODEL_DIR`, chạy lại server rồi kiểm tra trang: UI vẫn mở, health chưa sẵn sàng,
Phân tích bị khóa; API input hợp lệ trả 503. Không xóa/đổi tên model thật để diễn tập.
Sau đó Ctrl+C, bỏ biến bằng lệnh sau và chạy lại server:

```powershell
Remove-Item Env:SFAI_MODEL_DIR -ErrorAction SilentlyContinue
```

Bấm Kiểm tra lại kết nối, nhập câu mới và Phân tích.

## Bằng chứng và phạm vi

`reports/evidence/phase-5/` chứa suite, diễn tập hai browser, ảnh, thời gian thật
và kiểm chứng gói local. Thời gian là số đo trên máy này, không phải SLA.
Guard chặn mạng ngoài trong server Python và request của trang browser; không
thay firewall, không chứng nhận mọi tiến trình nền của hệ điều hành đã offline.
CSV/Dashboard không thuộc P0; Word/PPTX cuối thuộc Phase 6. Dataset/model chỉ dùng
trong bản local; quyền phân phối nguồn vẫn unknown.
