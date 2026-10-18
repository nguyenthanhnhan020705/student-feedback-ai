# Bắt đầu làm việc trong nhóm

## Leader chuẩn bị

1. Xác nhận bảo vệ `main` và `develop` đã được bật trên GitHub trước khi cấp quyền ghi cho thành viên. Tài liệu và CODEOWNERS không thay thế bước này.
2. Điền tên/tài khoản vào [bảng phân công](team-assignments.md), thống nhất thời gian bắt đầu và hạn giao từng đầu việc.
3. Tạo Issue cho TEAM-01–TEAM-05 bằng mẫu Công việc phát triển, gán đúng người và tiêu chí nghiệm thu. Việc gửi lời mời/giao Issue do leader thực hiện sau khi nhóm đã sẵn sàng.
4. Cùng nhóm hoàn thiện [Phase 0](roadmap/phase-0-specification.md), rồi thực hiện các phase theo phụ thuộc.

## Thành viên bắt đầu

Đọc theo thứ tự:

1. [README BRD](../README.md) — hiểu phạm vi P0 và P1.
2. [Phân công](team-assignments.md) — tìm vai trò và đầu việc đầu tiên của mình.
3. [Quy trình GitHub](../CONTRIBUTING.md) — cách đặt nhánh, mở PR, gửi minh chứng.
4. [Roadmap](roadmap/README.md) — đọc phase liên quan và điều kiện bắt đầu.

Sau khi được leader thông báo quyền truy cập và `develop` đã sẵn sàng:

```bash
git clone --branch develop https://github.com/nguyenthanhnhan020705/student-feedback-ai.git
cd student-feedback-ai
git switch -c feature/data-source-audit
```

Lệnh cuối là ví dụ cho TEAM-01. Mỗi thành viên chọn nhánh riêng:

| Vai trò | Nhánh cho đầu việc đầu tiên |
| --- | --- |
| TV2 — Data | `feature/data-source-audit` |
| TV3 — Sentiment | `docs/sentiment-experiment-design` |
| TV4 — Topic | `docs/topic-experiment-design` |
| TV5 — Backend | `docs/api-contract` |
| TV6 — Frontend | `docs/frontend-flow` |

Các tên nhánh này là hướng dẫn để thành viên tự tạo từ `develop`, chưa phải các nhánh đã được tạo sẵn. Không chạy lệnh cài đặt/khởi động mẫu trong BRD trước khi Phase 1 cung cấp môi trường thực tế.

## Trước khi yêu cầu leader review

- Đối chiếu tiêu chí của Issue và đánh dấu việc đã hoàn thành thực tế.
- Xem `git diff`, chỉ commit các file thuộc đầu việc; kiểm tra không có bí mật hoặc dữ liệu riêng tư.
- Push nhánh riêng, mở PR với base `develop`, điền đầy đủ mẫu PR và liên kết Issue.
- Nếu chưa có mô hình, dữ liệu hoặc API thật để kiểm tra, ghi rõ giới hạn, không dùng kết quả giả để đánh dấu đạt.
- Tiếp tục cập nhật cùng PR khi nhận góp ý; chờ leader duyệt và merge.
