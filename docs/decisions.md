# Quyết định của leader

**Trạng thái Phase 0:** Chờ leader chốt. File này ghi quyết định thực tế, không tự ghi ngày phê duyệt thay leader.

## Đã thống nhất về tổ chức

- Một người phụ trách một phần: Data, Sentiment, Topic, Backend, Frontend; file chung thuộc leader.
- Làm song song theo hợp đồng, bàn giao theo M0/M1/M2-S/M2-T/M3/M4.
- Nhánh chức năng → PR vào develop → leader review; bản tích hợp ổn định → PR vào main → leader review.
- File khung trống không phải code hoặc kiểm thử đã hoàn thành; dataset/model/metrics thật chỉ sinh sau.

## Leader cần điền để chốt M0

Ghi phiên bản/ngày chốt, Python/dependencies, phạm vi P1, giới hạn input/file, schema API/Data/artifact, công cụ test/UI, cách chạy demo và các quyết định xử lý dữ liệu/đánh giá. Dùng [checklist Phase 0](phase-0-leader-checklist.md), đối chiếu [bộ đặc tả](specs/README.md).

## Thông tin giao việc cần hoàn thiện

Tên/tài khoản TV2–TV6, ngày bắt đầu, hạn từng Issue, thông tin nộp bài và lịch giảng viên cần leader xác nhận. Chưa tự tạo lời mời/giao Issue hoặc cam kết deadline thay nhóm.
