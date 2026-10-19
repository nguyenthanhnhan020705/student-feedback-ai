# Checklist Phase 0 — Leader tự chốt đặc tả

**Người quyết định:** TV1 / leader `@nguyenthanhnhan020705`.  
**Trạng thái:** Chờ leader chốt nội dung; chưa ghi nhận Phase 0 hoàn thành.

Leader có thể tự quyết định yêu cầu trong phạm vi BRD. Quyết định làm thay đổi cam kết học phần cần đối chiếu yêu cầu giảng viên. Các thành viên cung cấp dữ kiện/góp ý kỹ thuật; leader là người duy nhất cập nhật và phê duyệt bộ đặc tả chung.

## 1. Các quyết định cần chốt

- [ ] Phạm vi P0 và việc CSV/Dashboard giữ ở P1 hay được cam kết thêm.
- [ ] Đối tượng dùng demo, đầu vào tiếng Việt và đầu ra một nhãn cảm xúc/một nhãn chủ đề.
- [ ] Hợp đồng loader, trường dữ liệu, nhãn và split. Giao Data xác minh nguồn/quyền sử dụng/mã số thực tế trước training.
- [ ] Giao diện pipeline/metadata, vị trí artifact riêng, quy tắc chuẩn hóa và cách bàn giao cho Backend.
- [ ] Thí nghiệm: ba thuật toán/nhiệm vụ, chỉ fit trên train, chọn Macro F1 validation, cách xử lý kết quả ngang nhau và giữ test cho cuối.
- [ ] API health/predict: JSON request/response, giới hạn input, lỗi rỗng/sai kiểu/vượt giới hạn/thiếu model. Batch chốt trước khi làm P1.
- [ ] UI: form nhập, trạng thái chờ, kết quả, lỗi; địa chỉ API và cách phục vụ frontend khi demo.
- [ ] Phiên bản Python/dependencies chung, lệnh cài/chạy/test, đường dẫn artifact; kiểm chứng cài thật ở Phase 1.
- [ ] Nghiệm thu AC-01–AC-08 theo phạm vi; không tự ghi ngưỡng Accuracy/F1 chưa được thống nhất.
- [ ] Tên/tài khoản từng người, ngày bắt đầu, hạn giao việc và quyền sở hữu file theo [phân công](team-assignments.md).

## 2. Tài liệu leader hoàn thiện

| File đầu ra | Nội dung cần có |
| --- | --- |
| `docs/specs/mvp.md` | Phạm vi chốt, kiến trúc, luồng demo, UI và nghiệm thu |
| `docs/specs/api-contract.md` | JSON request/response, lỗi, giới hạn và health |
| `docs/specs/data-contract.md` | Giao diện dữ liệu, nhãn, split và pipeline/metadata |
| `docs/decisions.md` | Quyết định, người chốt, ngày chốt và đầu mối xử lý việc chưa chặn triển khai |

Các file đầu ra đã có mẫu trong [bộ đặc tả](specs/README.md), chờ leader điền và phê duyệt. Checklist không thay thế đặc tả và chưa tự chốt giá trị kỹ thuật thay leader.

## 3. Điều kiện hoàn thành

- Đặc tả có quyết định cụ thể cho các giao diện chặn P0; ví dụ API hợp lệ/lỗi khớp luồng UI.
- Phần xác minh dữ liệu/môi trường được giao rõ cho Phase 1–2; P1 chưa chốt không chặn P0.
- Leader ghi phiên bản/ngày chốt, thông báo thành viên và cập nhật trạng thái trong roadmap.
- Đưa đặc tả vào các nhánh làm việc để dùng cùng phiên bản. Khi đưa vào `develop`, tiếp tục dùng PR cần leader review; với leader là code owner duy nhất, nhờ thành viên mở PR từ commit đặc tả leader chuẩn bị để bạn duyệt.

Xem [Phase 0](roadmap/phase-0-specification.md) và [quy trình PR](../CONTRIBUTING.md).
