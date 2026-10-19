# Phase 0 — Chốt phạm vi và đặc tả

**Trạng thái:** Đã soạn đủ đặc tả v1.0 và tự rà soát; chờ leader duyệt bằng văn bản.  
**Thời gian:** Ngày 1.  
**Phụ trách:** TV1 — leader tự chốt và sửa đặc tả; TV2–TV6 cung cấp thông tin/góp ý theo chức năng.  
**Nguồn:** [BRD](../../README.md), mục 4–9 và 12.  
**Quay lại:** [Lộ trình](README.md).

## Mục tiêu và điều kiện bắt đầu

Chuyển BRD thành đặc tả đủ rõ để triển khai từng thành phần. Đầu vào là BRD hiện tại; thông tin chưa xác nhận phải được ghi thành quyết định còn mở, kèm người xử lý và mốc cần chốt.

Leader dùng [checklist chốt Phase 0](../phase-0-leader-checklist.md). Việc tạo nhánh/phân công không đồng nghĩa Phase 0 đã hoàn thành; chỉ đổi trạng thái sau khi có bộ đặc tả cụ thể được leader xác nhận.

Các quyết định cụ thể đã nằm trong [bộ đặc tả v1.0](../specs/README.md). Đầu ra M0 phải giúp cả 5 người bắt đầu phần độc lập cùng lúc, theo [phân công song song](../team-assignments.md).

## Công việc

Các dấu [x] dưới đây ghi nhận công việc soạn đặc tả đã xong, không phải leader đã duyệt hoặc ứng dụng đã chạy. Bước P0.9 vẫn cần xác nhận của leader trên bộ tài liệu cụ thể.

- [x] P0.1: Soạn phạm vi P0/P1, đối tượng demo và kiến trúc phục vụ UI/API cùng origin, chờ duyệt trong MVP v1.0.
- [x] P0.2: Phân loại TBD-01–TBD-08 thành nội dung chặn triển khai và nội dung có thể hoàn thiện sau; xác định đầu mối và hạn xử lý.
- [x] P0.3: Đặc tả `GET /api/health` và `POST /api/predict`: cấu trúc JSON, lỗi đầu vào, thiếu mô hình, giới hạn văn bản và trạng thái sẵn sàng.
- [x] P0.4: Định nghĩa hợp đồng dữ liệu: trường văn bản, nhãn sentiment/topic, cách ghi nhận split; bảng mã số chỉ chốt sau đối chiếu dataset ở Phase 2.
- [x] P0.5: Định nghĩa cách bàn giao pipeline: tên artifact, metadata, phiên bản môi trường, thông tin nhãn và cách kiểm tra trước khi nạp.
- [x] P0.6: Ghi thiết kế luồng nhập câu → API → hai pipeline → hiển thị nhãn; mô tả trạng thái đang xử lý, lỗi và thành công của giao diện.
- [x] P0.7: Liên kết các quyết định với AC-01–AC-08; soạn quy tắc chọn mô hình bằng validation, giữ test cho đánh giá cuối.

- [x] P0.8: Soạn runtime/constraints/lệnh mục tiêu và giao Phase 1 kiểm chứng lock/môi trường thật.
- [ ] P0.9: Leader duyệt phiên bản 1.0, ghi ngày duyệt và công bố M0. Không tự đánh dấu bước này đã hoàn thành.

## Sản phẩm đã soạn

| File | Nội dung |
| --- | --- |
| `docs/specs/mvp.md` | Phạm vi, kiến trúc, luồng người dùng, xử lý lỗi và tiêu chí nghiệm thu |
| `docs/specs/api-contract.md` | Hợp đồng API, ví dụ request/response và lỗi |
| `docs/specs/data-contract.md` | Trường dữ liệu, split, nhãn và hợp đồng artifact |
| `docs/specs/environment.md` | Runtime/constraints, lock, cấu hình và lệnh mục tiêu |
| `docs/decisions.md` | Quyết định đề xuất v1.0, phân loại việc còn phải kiểm chứng và đầu mối |

## Điều kiện hoàn thành

- Người làm ML, backend và frontend sử dụng cùng hợp đồng; không còn quyết định chặn khung ứng dụng bị bỏ ngỏ.
- Những nội dung phụ thuộc xác minh dataset được giao rõ cho Phase 2; nội dung P1 được giao cho Phase 5 trước khi triển khai.
- Đặc tả được rà soát với BRD; không gán số liệu mô hình hay ngày phê duyệt chưa có thật.

## Kiểm chứng và bàn giao

Rà soát thủ công một request hợp lệ, một request rỗng và trường hợp chưa có model xuyên suốt đặc tả API/UI. Ghi kết quả rà soát vào cuối tài liệu này khi thực hiện. Đầu ra chuyển sang Phase 1 và Phase 2.
