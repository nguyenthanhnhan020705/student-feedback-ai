# Ghi chú giao diện Frontend (P0)

**Phụ trách:** TV6 – Frontend. **Nguồn:** `docs/specs/mvp.md` mục 3, `docs/specs/api-contract.md` mục 1–5.
**Trạng thái 2026-10-31:** Phase 4 đã kiểm chứng với API và hai model thật trên Chrome/Edge; bộ Frontend đạt 42 tests. Bằng chứng ở `reports/evidence/phase-4/` và `reports/evidence/frontend/`. Nghiệm thu toàn sản phẩm thuộc Phase 5.

## File
`frontend/index.html`, `styles.css`, `api.js` (gọi API), `app.js` (giao diện). P1 (`batch.js`, `dashboard.js`) chưa làm vì chưa được leader cho phép.

## Luồng
1. Mở trang: gọi `GET /api/health` một lần. Nút "Kiểm tra lại kết nối" gọi lại; không polling.
2. Nhập câu: hiển thị bộ đếm Unicode code point (`[...text].length`) trên 5000, không dùng `maxlength`.
3. Nút **Phân tích** chỉ bật khi input hợp lệ, không đang gửi và `ready = true`.
4. Gửi `POST /api/predict` với `{"text": ...}` nguyên văn. Một request dự đoán tại một thời điểm, timeout 10 giây bao gồm cả đọc JSON body, không tự gửi lại.
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

UI dựa vào HTTP status, không so khớp nguyên văn `error.message`. Nhãn phải là chuỗi và own-property trong bảng ánh xạ; nhãn lạ, thuộc tính prototype và mảng đều là lỗi hệ thống. AbortError báo timeout, lỗi truyền dữ liệu báo lỗi mạng; JSON sai giữ phân loại HTTP lỗi hoặc bị từ chối khi response thành công.

## Dữ liệu MOCK
Chỉ dùng khi phát triển, bật bằng `?mock=ok|notready|invalid|error`. Khi bật có banner và hậu tố "(MOCK)" trên kết quả. Không có tham số `mock` thì gọi API thật; mock không phải fallback.

## Kiểm chứng Frontend (không thay nghiệm thu tổng thể)
- [x] Câu mới đi qua UI, API và hai pipeline thật (minh chứng cho AC-03)
- [x] 422 và 503 hiển thị đúng; reconnect sau lỗi health (minh chứng cho AC-04/07)
- [x] Ảnh chụp bản chạy thật (Chrome, Edge) lưu trong `reports/evidence/frontend/`
- [x] Timeout headers/body, nhãn không hợp lệ, input Unicode 5000/5001, giữ input và retry.
- [x] Bố cục mobile 390 px không tràn ngang; MOCK luôn có banner và hậu tố.
