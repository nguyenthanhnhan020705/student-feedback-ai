# Kiểm thử Giai đoạn A — 18/10/2026

## Môi trường và kết quả

Windows, CPython 3.13.3, môi trường ảo `.venv`. Máy chưa có Python 3.11/3.12
trong những vị trí đã kiểm tra; chưa tuyên bố tương thích đã kiểm chứng với
hai phiên bản khuyến nghị đó. Danh sách dependency trực tiếp đã cài tại
`requirements-tested.txt`. Playwright 1.64.0 dùng riêng để kiểm tra trình duyệt,
không bắt buộc khi chạy app hoặc pytest.

| Kiểm tra | Kết quả thực tế |
|---|---|
| Cài `requirements.txt` vào `.venv` | Thành công |
| `python -m pip check` | No broken requirements found |
| `python -m pytest -q` | 43 passed, 1 warning |
| `python -m compileall -q backend ml tests` | Thành công |
| CLI train_sentiment/train_topic/evaluate | --help thành công, lệnh mặc định trả mã 2 và báo chưa triển khai |
| Bốn notebook | JSON đọc được, chưa chạy thí nghiệm, không có output |
| Uvicorn `--reload` | Khởi động thành công tại 127.0.0.1:8765 |
| HTTP smoke | Frontend/static/docs/OpenAPI 200, health đúng, metrics chưa có, suy luận 503, input sai 422 |
| Edge headless desktop/mobile | Bốn tab, bàn phím, lỗi thiếu model, CSV sai, trạng thái rỗng đúng; không tràn ngang hoặc có JS exception |

Cổng 8000 đang có tiến trình khác lắng nghe: lệnh Uvicorn mặc định gặp
WinError 10013 cả trong và ngoài sandbox. Không dừng tiến trình đó; dùng
`--port 8765` để kiểm chứng. Đây là giới hạn cổng trên máy, ứng dụng vẫn phục
vụ cùng các route ở cổng thay thế.

Cảnh báo duy nhất: Starlette 1.8.0 TestClient thông báo dùng httpx đang bị
deprecated và khuyến nghị httpx2. Test hiện vẫn chạy thành công với httpx
0.28.1. Không tắt/ẩn cảnh báo bằng pytest filter. Nhóm có thể chốt lại bộ
phiên bản hoặc đổi HTTP test client trong bước duy trì tiếp theo.

## Chạy lại

Từ gốc repository:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m compileall -q backend ml tests
.\.venv\Scripts\python.exe -m ml.train_sentiment --help
.\.venv\Scripts\python.exe -m ml.train_topic --help
.\.venv\Scripts\python.exe -m ml.evaluate --help
```

Khởi động app ở terminal thứ nhất, HTTP smoke ở terminal thứ hai:

```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --reload --port 8765
```

```powershell
.\.venv\Scripts\python.exe tests/http_smoke.py --url http://127.0.0.1:8765
```

Smoke này dành cho trạng thái chưa có model. Nếu đã thêm model thật, kiểm
thử theo checklist tích hợp bên dưới thay vì mong đợi health setup_required.

Browser smoke tùy chọn, dùng Edge cài sẵn trên Windows:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-browser.txt
.\.venv\Scripts\python.exe tests/browser_smoke.py --url http://127.0.0.1:8765 --executable "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"
```

Có thể truyền executable Chrome khác, hoặc bỏ --executable nếu đã cài
Chromium của Playwright. Script không tự tải browser. Screenshot thật lưu
tại `.local-tests/phase-a/desktop.png` và `mobile.png`, bị loại khỏi Git.
Các script smoke không được pytest tự động thu thập; cần server đang chạy.

## Phạm vi pytest

- Văn bản thiếu/sai kiểu/rỗng/khoảng trắng/vượt 5.000 ký tự.
- Health thiếu cả hai model, thiếu một model, model hỏng hoặc không có predict.
- Predict lỗi trả 503; nhãn ngoài mapping, sai kiểu hoặc sai số lượng bị từ chối.
- CSV thiếu cột, trùng header, ô trống, UTF-8 lỗi, quote lỗi, sai số cột,
  quá 1.000 dòng, quá 2 MB, sai đuôi file, thiếu multipart field.
- BOM, dấu phẩy/xuống dòng trong ô có quote, đúng 1.000 dòng và đúng 5.000 ký tự.
- Hợp đồng kết quả một câu và batch/summary bằng pipeline substitute trong test.
- Metrics thiếu, marker chưa đánh giá, JSON hỏng, thiếu schema, số overflow
  trong trường phụ đều không trở thành chỉ số khả dụng.
- Unicode/khoảng trắng và CLI khung trung thực.

Các số và nhãn trong fixture chỉ xác minh phần mềm. Không có pipeline được
huấn luyện, dataset mẫu hoặc báo cáo fixture được đưa vào model/report của app.

## Rà soát độc lập và sửa lỗi

Một lượt review độc lập phát hiện số JSON dạng `1e999` trong trường tùy chọn
của báo cáo có thể thành giá trị vô hạn nhưng vẫn được đánh dấu available.
Đã thêm test hồi quy, quan sát test thất bại, sửa parser để từ chối overflow
ở mọi độ sâu, rồi chạy toàn bộ suite: 43 test đạt. Không còn phát hiện
Critical/Important chưa xử lý từ lượt review đó.

## Checklist khi có dataset/model thật (chưa kiểm chứng)

- [ ] TV2 xác minh nguồn, quyền phân phối, split và mapping của đúng bản dataset.
- [ ] TV3/TV4 fit vectorizer trên train; chọn thuật toán/siêu tham số bằng validation.
- [ ] Giữ tiền xử lý bên trong pipeline tương thích lúc train và predict.
- [ ] Xuất hai joblib tin cậy cùng cấu hình, seed và phiên bản thư viện.
- [ ] Đánh giá test độc lập và xuất reports theo API_CONTRACT.md; kiểm tra thứ tự nhãn ma trận.
- [ ] Khởi động lại backend, health ready, suy luận thật đơn câu và batch.
- [ ] Browser hiển thị đúng nhãn thật, count/dashboard khớp results, xuất CSV đọc lại được.
- [ ] Kiểm tra bảng báo cáo, bảng so sánh và hình Confusion Matrix bằng số liệu thật.
- [ ] Kiểm tra cùng bộ phiên bản trên Python 3.11/3.12 nếu nhóm chọn hai phiên bản này.

Chưa đo Accuracy/F1, hiệu năng AI hoặc độ ổn định production. Chưa kiểm thử
toàn luồng thành công với model thật; đó là phần việc tích hợp tiếp theo.
