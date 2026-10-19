# Phase 0 — Checklist của leader

**Người phê duyệt:** `@nguyenthanhnhan020705`. **Bộ đề xuất:** v1.0, soạn 2026-10-19.  
**Trạng thái:** Đã soạn và tự rà soát, chờ leader duyệt; chưa công bố M0 hoàn thành.

## 1. Nội dung đã chuẩn bị để duyệt

- [x] Phạm vi P0 và CSV/Dashboard giữ ở P1 chưa giao triển khai.
- [x] Người dùng demo, kiến trúc FastAPI phục vụ cả UI/API và luồng lỗi/kết quả.
- [x] Hợp đồng loader/nhãn/split/chuẩn hóa, mốc M1 và xử lý rỗng/trùng.
- [x] Baseline NB/LR/SVM, tham số, chọn validation/tie-break và cách đánh giá test cuối.
- [x] Pipeline/metadata riêng, checksum/môi trường/tập nhãn và quy tắc readiness.
- [x] API JSON, giới hạn 5000 code point, error envelope và P1 dự phòng 2 MiB/1000 record.
- [x] Python 3.13.x 64-bit, constraints, quy trình khóa môi trường và lệnh mục tiêu Phase 1.
- [x] Tiêu chí AC-01–AC-08 và cách bàn giao M0/M1/M2-S/M2-T/M3/M4 để làm song song.
- [x] Phân loại thông tin nguồn cần xác minh, giao rõ người/mốc; không tự điền số liệu hoặc phê duyệt thay nhóm.
- [ ] Leader duyệt toàn bộ [bộ đặc tả v1.0](specs/README.md), hoặc ghi chỉnh sửa cần có.

Các dấu [x] chỉ xác nhận đã soạn quyết định trong tài liệu, không xác nhận đã chạy ứng dụng/test/dataset/model hoặc được leader phê duyệt.

## 2. Đọc theo thứ tự

1. [MVP](specs/mvp.md): phạm vi, luồng, kiến trúc và nghiệm thu.
2. [API](specs/api-contract.md): nhãn chuỗi, JSON, giới hạn và lỗi.
3. [Data/model](specs/data-contract.md): chữ ký hàm, baseline, split, artifact/metadata.
4. [Môi trường](specs/environment.md): runtime, constraints và lock ở Phase 1.
5. [Nhật ký quyết định](decisions.md): các quyết định và việc chuyển giao cho phase sau.

## 3. Sau khi leader duyệt

Ghi ngày/phiên bản duyệt, cập nhật M0 và phân phối cùng bản hợp đồng đến 5 nhánh chức năng. Điền tên/tài khoản và hạn thực tế vào Issue trước khi giao người. Giữ PR/review khi đưa vào develop/main; không tắt bảo vệ để tự hợp nhất.

Data xác minh quyền dùng/source/mapping và manifest trước M1; leader kiểm chứng/công bố bộ lock ở Phase 1 trước train. Đây là đầu ra triển khai tiếp theo, không phải yêu cầu phải tự tạo dữ liệu hoặc cài dependencies trong Phase 0.
