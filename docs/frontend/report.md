# Báo cáo TV6 — Frontend, Phase 4

Ngày thực hiện: 2026-10-31. Kế thừa giao diện của TV6 trên bản tích hợp
`feature/integration-p0`; trợ lý bổ sung sửa lỗi và kiểm thử theo yêu cầu leader.
Không gán phần hỗ trợ tích hợp thành toàn bộ đóng góp của TV6.

## Thay đổi

- Nhãn dự đoán phải là chuỗi và có trong bảng nhãn chuẩn; từ chối thuộc tính
  prototype (`constructor`, `toString`, `__proto__`), mảng và nhãn lạ.
- Timeout 10 giây bao gồm nhận headers và đọc JSON body. AbortError được báo
  timeout; lỗi truyền dữ liệu được báo lỗi mạng. JSON sai không làm mất phân loại
  HTTP 422/503/500. Không dùng dữ liệu mẫu làm fallback.
- Giữ luồng UI có sẵn: khóa nút khi đang xử lý, giữ input, xóa kết quả cũ,
  mở lại nút sau lỗi và kiểm tra lại health khi model chưa sẵn sàng.
- Giữ HTML/CSS/app.js hiện có sau kiểm tra bố cục desktop và mobile 390 px;
  không thêm framework, confidence, CSV hoặc dashboard.

## Kiểm chứng

Regression gốc tái hiện 4 thất bại trên Chrome/Edge. Bộ mở rộng trước sửa có
6 thất bại và 5 ca kiểm soát đạt trên Chrome. Kiểm thử mới bao gồm nhãn sai
kiểu, timeout body qua UI và retry với model thật, JSON sai, health reconnect,
banner MOCK và bố cục mobile. Lệnh, log cuối và kết quả review được lưu ở
[bằng chứng Phase 4](../../reports/evidence/phase-4/README.md).

Ảnh và JSON suy luận thật: `reports/evidence/frontend/`; ảnh mobile MOCK được
ghi rõ riêng trong `reports/evidence/phase-4/`. API/model dùng local, không train
lại hoặc sửa số liệu thực nghiệm. Nghiệm thu tổng thể và đóng gói demo thuộc
Phase 5; Word/PowerPoint thuộc Phase 6.
