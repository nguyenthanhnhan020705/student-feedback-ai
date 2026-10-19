# Quy trình đóng góp

Đọc [hướng dẫn bắt đầu](docs/team-start.md), [phân công song song](docs/team-assignments.md), [quyền sở hữu file](docs/function-ownership.md) và hướng dẫn vai trò trước khi sửa file.

## 1. Nhánh và quyền duyệt

Luồng cố định: nhánh chức năng → PR vào `develop` → leader duyệt; bản tích hợp ổn định → PR vào `main` → leader duyệt.

| Vai trò | Nhánh |
| --- | --- |
| Data | `feature/data-preprocessing` |
| Sentiment | `feature/sentiment-model` |
| Topic | `feature/topic-model` |
| Backend | `feature/backend-api` |
| Frontend | `feature/frontend-dashboard` |

Leader/code owner là `@nguyenthanhnhan020705`. Không push trực tiếp vào `main`/`develop`, không tự merge hoặc force push. Quy tắc phân công không tự khóa quyền sửa file theo thư mục; leader kiểm tra phạm vi trên mỗi PR. Cấu hình bảo vệ và hướng dẫn ban đầu nằm trong [quản trị GitHub](docs/github-admin.md).

## 2. Làm việc trên nhánh đã có

Ví dụ Sentiment:

```bash
git clone --branch feature/sentiment-model https://github.com/nguyenthanhnhan020705/student-feedback-ai.git
cd student-feedback-ai
git status
# Viết code/tests/tài liệu phần mình, chạy kiểm tra liên quan rồi:
git diff
git add ml/train_sentiment.py tests/test_sentiment_training.py docs/sentiment/experiment.md
git diff --cached
git commit -m "feat: add sentiment baseline"
git push origin feature/sentiment-model
```

Mở PR với base `develop`, điền mẫu và yêu cầu leader review. PR có thể nhỏ theo mốc bàn giao, không cần đợi xong cả chức năng. Khi được yêu cầu sửa, tiếp tục commit/push cùng nhánh, không mở PR trùng cho cùng đầu việc.

## 3. Đồng bộ phần đã duyệt

Lưu công việc trước khi đồng bộ:

```bash
git fetch origin
git merge origin/develop
# Xử lý conflict nếu có, chạy lại kiểm tra liên quan rồi push nhánh mình.
```

Không merge trực tiếp nhánh người khác. Nhóm ưu tiên merge commit cho PR từ 5 nhánh dùng qua nhiều đầu việc; nếu dùng squash/rebase, leader cần thống nhất nhánh tiếp theo để tránh đưa lại commit cũ vào PR. Không tự đổi chiến lược hoặc force push để sửa lịch sử.

## 4. Điều kiện gửi review

- Gắn task/Issue, đúng phạm vi file của một vai trò, có mô tả và tiêu chí nghiệm thu.
- Có lệnh/cách kiểm tra và kết quả thật. File test trống, bài không được thu thập hoặc skip do thiếu artifact không được ghi là đạt.
- Fixture/mock dành tests/UI development phải được phân biệt rõ; không thay model thật trong API/nghiệm thu.
- Cập nhật tài liệu/báo cáo riêng và dependencies riêng; đề xuất leader khi cần thay đổi hợp đồng/config gốc.
- Không đưa bí mật, dữ liệu riêng tư hoặc dataset/model chưa được phép lên repo public.
- Báo tiến độ và vướng mắc trong Issue; hoàn thành được ghi nhận sau review và merge.

## 5. PR của leader

GitHub không cho tác giả tự approve PR của mình. Khi leader là code owner duy nhất, nhờ thành viên mở PR từ commit/nhánh chứa tài liệu leader đã chuẩn bị, rồi leader review. Không tắt bảo vệ để tự hợp nhất. Bản mới của khung/hướng dẫn đang ở 5 nhánh chức năng và đi vào `develop` bằng PR, trước khi được đưa lên `main` cùng bản ổn định.
