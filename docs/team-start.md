# Bắt đầu làm việc trong nhóm

## Leader chuẩn bị

1. Xác nhận bảo vệ `main` và `develop` đã được bật trên GitHub trước khi cấp quyền ghi cho thành viên. Tài liệu và CODEOWNERS không thay thế bước này.
2. Điền tên/tài khoản vào [bảng phân công](team-assignments.md), thống nhất thời gian bắt đầu và hạn giao từng đầu việc.
3. Tạo Issue cho TEAM-01–TEAM-05 bằng mẫu Công việc phát triển, gán đúng người và tiêu chí nghiệm thu. Việc gửi lời mời/giao Issue do leader thực hiện sau khi nhóm đã sẵn sàng.
4. Leader tự chốt [Phase 0](phase-0-leader-checklist.md), cung cấp cùng phiên bản đặc tả cho 5 thành viên; sau đó thực hiện các phase theo phụ thuộc.

## Thành viên bắt đầu

Đọc theo thứ tự:

1. [README BRD](../README.md) — hiểu phạm vi P0 và P1.
2. [Phân công](team-assignments.md) — tìm vai trò và đầu việc đầu tiên của mình.
3. [Quy trình GitHub](../CONTRIBUTING.md) — cách đặt nhánh, mở PR, gửi minh chứng.
4. [Roadmap](roadmap/README.md) — đọc phase liên quan và điều kiện bắt đầu.

Sau khi được leader thông báo quyền truy cập và `develop` đã sẵn sàng:

```bash
git clone --branch feature/data-preprocessing https://github.com/nguyenthanhnhan020705/student-feedback-ai.git
cd student-feedback-ai
```

Ví dụ trên dành cho Data. Mỗi thành viên thay tên nhánh theo đúng chức năng:

| Vai trò | Nhánh cho đầu việc đầu tiên |
| --- | --- |
| TV2 — Data | `feature/data-preprocessing` |
| TV3 — Sentiment | `feature/sentiment-model` |
| TV4 — Topic | `feature/topic-model` |
| TV5 — Backend | `feature/backend-api` |
| TV6 — Frontend | `feature/frontend-dashboard` |

Leader khởi tạo 5 nhánh từ cùng nền `develop`, kèm cùng commit hướng dẫn phân công. Thành viên checkout nhánh đã có, không cần tạo nhánh trùng tên. Nếu đã clone repository:

```bash
git fetch origin
git switch --track origin/feature/data-preprocessing
```

Nếu nhánh đã có ở máy, dùng `git switch feature/data-preprocessing`. Đọc [quyền sở hữu file](function-ownership.md); không chạy lệnh cài/khởi động mẫu trong BRD trước khi Phase 1 cung cấp môi trường thực tế. Hướng dẫn mới được tích hợp vào `develop` qua PR, không push trực tiếp vào nhánh được bảo vệ.

## Trước khi yêu cầu leader review

- Đối chiếu tiêu chí của Issue và đánh dấu việc đã hoàn thành thực tế.
- Xem `git diff`, chỉ commit các file thuộc đầu việc; kiểm tra không có bí mật hoặc dữ liệu riêng tư.
- Push nhánh chức năng của mình, mở PR với base `develop`, điền mẫu PR và liên kết Issue. Sau khi PR nhỏ được merge, đồng bộ `origin/develop` về nhánh chức năng trước đầu việc tiếp theo.
- Nếu chưa có mô hình, dữ liệu hoặc API thật để kiểm tra, ghi rõ giới hạn, không dùng kết quả giả để đánh dấu đạt.
- Tiếp tục cập nhật cùng PR khi nhận góp ý; chờ leader duyệt và merge.
