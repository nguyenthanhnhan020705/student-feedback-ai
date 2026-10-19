# Đặc tả MVP — mẫu chờ leader chốt

**Trạng thái:** Chưa phê duyệt. Leader điền phiên bản/ngày chốt và nội dung dưới đây.

## Phạm vi

Đối chiếu BRD: P0 là Data + hai nhiệm vụ sentiment/topic + API/web một câu + kiểm thử/báo cáo. P1 CSV/Dashboard chỉ triển khai khi được leader cho phép. Ghi quyết định phạm vi và đối tượng dùng demo tại đây.

## Luồng và giao diện

Chốt luồng nhập câu → API → hai pipeline → hai nhãn; trạng thái chờ, lỗi và model chưa sẵn sàng. Ghi giới hạn một nhãn chính mỗi nhiệm vụ, cách phục vụ UI và địa chỉ API.

## Nghiệm thu

Liên kết AC-01–AC-08 theo phạm vi, cách cung cấp minh chứng và trách nhiệm mỗi phần. Không điền số liệu mô hình hoặc ngưỡng chất lượng chưa thống nhất.
