# Bắt đầu làm việc — đọc trước khi sửa file

## 1. Trạng thái của repository

Đã có khung file trống cho cả năm chức năng. File code và tests chưa có nội dung; notebook không có cell/output; chưa có dataset, model hay metrics thực nghiệm. Các phase triển khai chưa được nghiệm thu. Leader đã duyệt [hợp đồng Phase 0 v1.0](specs/README.md) ngày 2026-10-19; các thành viên có thể bắt đầu theo cùng hợp đồng.

## 2. Vào đúng nhánh

| Thành viên | Nhánh | Hướng dẫn cần đọc |
| --- | --- | --- |
| Data | `feature/data-preprocessing` | [Data](data/README.md) |
| Sentiment | `feature/sentiment-model` | [Sentiment](sentiment/README.md) |
| Topic | `feature/topic-model` | [Topic](topic/README.md) |
| Backend | `feature/backend-api` | [Backend](backend/README.md) |
| Frontend | `feature/frontend-dashboard` | [Frontend](frontend/README.md) |

Ví dụ cho Data; người khác thay đúng tên nhánh của mình:

```bash
git clone --branch feature/data-preprocessing https://github.com/nguyenthanhnhan020705/student-feedback-ai.git
cd student-feedback-ai
```

Nếu đã clone và chưa có nhánh ở máy:

```bash
git fetch origin
git switch --track origin/feature/data-preprocessing
```

Nếu đã có nhánh ở máy, lưu công việc trước, rồi:

```bash
git switch feature/data-preprocessing
git pull --ff-only
```

Không reset/force push để đồng bộ. Nếu nhánh đã có commit riêng và không fast-forward được, trao đổi với leader để merge giữ lại công việc.

## 3. Thứ tự đọc và bắt đầu

1. [BRD](../README.md): mục tiêu và phạm vi P0/P1.
2. [Phân công làm song song](team-assignments.md): việc làm ngay và các mốc bàn giao.
3. Hướng dẫn vai trò của mình trong bảng trên: file nào sửa, việc nào làm trước, đầu ra nào bàn giao.
4. [Quyền sở hữu file](function-ownership.md) và [quy trình PR](../CONTRIBUTING.md).
5. Bộ [đặc tả Phase 0](specs/README.md) đã được leader chốt; hiện phiên bản 1.0 đã có hiệu lực, không còn là mẫu hoặc bản chờ duyệt.

Đọc [hướng dẫn môi trường](development.md) trước khi chạy lệnh. Requirements/config đang trống, chưa có dependencies hay lệnh khởi động ứng dụng được kiểm chứng. Tạo đủ file không đồng nghĩa có ứng dụng chạy được.

## 4. Làm việc và gửi PR

- Chỉ sửa file thuộc phạm vi của mình. Code/tests bắt đầu từ file trống; tài liệu và notebook bắt đầu theo mẫu riêng.
- Làm phần có thể độc lập trước, dùng fixture rõ ràng trong tests; chỉ chờ đầu ra thật tại bước đã chỉ ra trong phân công.
- Khi hoàn thành một đầu việc nhỏ, kiểm tra diff, tests liên quan và cập nhật tài liệu vai trò.
- Commit/push đúng nhánh, mở PR với base `develop`, ghi rõ task, cách kiểm tra, kết quả thật và phần còn thiếu.
- Chờ leader duyệt; sau khi PR được merge, fetch và merge `origin/develop` về nhánh chức năng trước đầu việc tiếp theo.
- Không đánh dấu tests/phase hoàn thành nếu file còn trống, bài kiểm tra chưa chạy hoặc chưa có dữ liệu/artifact cần thiết.

## 5. Leader giao việc

Phase 0 đã chốt. Mời 5 tài khoản, điền tên và hạn vào Issue, rồi giao mỗi người một nhánh/chức năng. Các tài liệu chỉ phân vai; không tự gửi lời mời hoặc gán một tài khoản vào nhánh. Nhánh Git không tạo giới hạn quyền sửa file; nhóm tuân thủ phân công và leader kiểm tra PR.
