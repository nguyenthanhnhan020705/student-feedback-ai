# Ghi chú giao diện Frontend (P0)

**Phụ trách:** TV6 – Frontend. **Nguồn:** `docs/specs/mvp.md` mục 3, `docs/specs/api-contract.md` mục 1–5.
**Trạng thái:** khung giao diện, mới chạy với dữ liệu MOCK; chưa kiểm chứng với API và mô hình thật.

## File
`frontend/index.html`, `styles.css`, `api.js` (gọi API), `app.js` (giao diện). P1 (`batch.js`, `dashboard.js`) chưa làm vì chưa được leader cho phép.

## Luồng
1. Mở trang: gọi `GET /api/health` một lần. Nút "Kiểm tra lại kết nối" gọi lại; không polling.
2. Nhập câu: hiển thị bộ đếm Unicode code point (`[...text].length`) trên 5000, không dùng `maxlength`.
3. Nút **Phân tích** chỉ bật khi input hợp lệ, không đang gửi và `ready = true`.
4. Gửi `POST /api/predict` với `{"text": ...}` nguyên văn. Một request tại một thời điểm, timeout 10 giây, không tự gửi lại.
5. Thành công: hiện nhãn tiếng Việt theo bảng ánh xạ. Không có confidence.
6. Lỗi: giữ nguyên nội dung đã nhập, xóa kết quả cũ.
7. Hiển thị bằng `textContent`, không dùng `innerHTML`.

## Bảng trạng thái
| Trạng thái | Khi nào | Hiển thị |
|---|---|---|
| Input rỗng/chỉ khoảng trắng | Chưa nhập hoặc toàn khoảng trắng | Gợi ý nhập nội dung, nút khóa, không gọi API |
| Quá 5000 ký tự | Đếm code point > 5000 | Thông báo vượt giới hạn, nút khóa |
| Đang phân tích | Đã gửi request | Nút khóa, "Đang phân tích…" |
| Thành công | HTTP 200 | Hai ô Cảm xúc, Chủ đề |
| 422 | INVALID_INPUT | Thông báo nội dung không hợp lệ |
| 503 | MODEL_NOT_READY | Thông báo chưa sẵn sàng, cập nhật trạng thái model |
| 500 | INFERENCE_ERROR / INTERNAL_ERROR | Thông báo lỗi hệ thống |
| Lỗi mạng / timeout | Không kết nối được hoặc quá 10 giây | Thông báo, cho thử lại |
| Health `ready=false` | Thiếu hoặc hỏng một model | "Mô hình chưa sẵn sàng" kèm trạng thái từng model, nút Phân tích khóa |

UI dựa vào HTTP status, không so khớp nguyên văn `error.message`. Nhãn ngoài bảng ánh xạ được coi là lỗi hệ thống.

## Dữ liệu MOCK
Chỉ dùng khi phát triển, bật bằng `?mock=ok|notready|invalid|error`. Khi bật có banner và hậu tố "(MOCK)" trên kết quả. Không có tham số `mock` thì gọi API thật; mock không phải fallback.

## Cần kiểm chứng sau khi Backend và model xong (M3/M4)
- [ ] Câu mới đi qua UI, API và hai pipeline thật (AC-03)
- [ ] 422 và 503 hiển thị đúng (AC-04), health phân biệt live và ready (AC-07)
- [ ] Ảnh chụp bản chạy thật (Chrome, Edge) lưu trong `reports/evidence/frontend/`
