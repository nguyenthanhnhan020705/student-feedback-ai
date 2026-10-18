# Phase 0 — Chốt phạm vi và đặc tả

**Trạng thái:** Chưa bắt đầu.  
**Thời gian:** Ngày 1.  
**Phụ trách:** TV1 điều phối; TV2–TV6 cùng rà soát.  
**Nguồn:** [BRD](../../README.md), mục 4–9 và 12.  
**Quay lại:** [Lộ trình](README.md).

## Mục tiêu và điều kiện bắt đầu

Chuyển BRD thành đặc tả đủ rõ để triển khai từng thành phần. Đầu vào là BRD hiện tại; thông tin chưa xác nhận phải được ghi thành quyết định còn mở, kèm người xử lý và mốc cần chốt.

## Công việc

- [ ] P0.1: Xác nhận phạm vi P0, giữ CSV/Dashboard ở P1; ghi đối tượng dùng demo và cách chạy demo dự kiến.
- [ ] P0.2: Phân loại TBD-01–TBD-08 thành nội dung chặn triển khai và nội dung có thể hoàn thiện sau; xác định đầu mối và hạn xử lý.
- [ ] P0.3: Đặc tả `GET /api/health` và `POST /api/predict`: cấu trúc JSON, lỗi đầu vào, thiếu mô hình, giới hạn văn bản và trạng thái sẵn sàng.
- [ ] P0.4: Định nghĩa hợp đồng dữ liệu: trường văn bản, nhãn sentiment/topic, cách ghi nhận split; bảng mã số chỉ chốt sau đối chiếu dataset ở Phase 2.
- [ ] P0.5: Định nghĩa cách bàn giao pipeline: tên artifact, metadata, phiên bản môi trường, thông tin nhãn và cách kiểm tra trước khi nạp.
- [ ] P0.6: Ghi thiết kế luồng nhập câu → API → hai pipeline → hiển thị nhãn; mô tả trạng thái đang xử lý, lỗi và thành công của giao diện.
- [ ] P0.7: Liên kết các quyết định với AC-01–AC-08; chốt cách đánh giá mô hình bằng validation, giữ test cho đánh giá cuối.

## Sản phẩm dự kiến

| File | Nội dung |
| --- | --- |
| `docs/specs/mvp.md` | Phạm vi, kiến trúc, luồng người dùng, xử lý lỗi và tiêu chí nghiệm thu |
| `docs/specs/api-contract.md` | Hợp đồng API, ví dụ request/response và lỗi |
| `docs/specs/data-contract.md` | Trường dữ liệu, split, nhãn và hợp đồng artifact |
| `docs/decisions.md` | Quyết định đã thống nhất, vấn đề còn mở và đầu mối |

## Điều kiện hoàn thành

- Người làm ML, backend và frontend sử dụng cùng hợp đồng; không còn quyết định chặn khung ứng dụng bị bỏ ngỏ.
- Những nội dung phụ thuộc xác minh dataset được giao rõ cho Phase 2; nội dung P1 được giao cho Phase 5 trước khi triển khai.
- Đặc tả được rà soát với BRD; không gán số liệu mô hình hay ngày phê duyệt chưa có thật.

## Kiểm chứng và bàn giao

Rà soát thủ công một request hợp lệ, một request rỗng và trường hợp chưa có model xuyên suốt đặc tả API/UI. Ghi kết quả rà soát vào cuối tài liệu này khi thực hiện. Đầu ra chuyển sang Phase 1 và Phase 2.
