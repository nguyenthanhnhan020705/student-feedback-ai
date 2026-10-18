# Quy trình làm việc của nhóm

Xem [phân công 5 thành viên](docs/team-assignments.md), [BRD](README.md) và [lộ trình](docs/roadmap/README.md).

## 1. Nhánh và quyền duyệt

Luồng công việc: `feature/*` → Pull Request vào `develop` → Pull Request vào `main`.

| Nhánh | Mục đích | Quy tắc |
| --- | --- | --- |
| `main` | Bản tích hợp ổn định để demo/bàn giao | Chỉ cập nhật qua PR đã được leader duyệt và đạt kiểm tra |
| `develop` | Tích hợp công việc trong quá trình phát triển | PR từ nhánh công việc, leader review trước khi merge |
| `feature/<vai-tro>-<task>` | Công việc của từng thành viên | Thành viên commit/push vào nhánh của mình |
| `chore/*`, `docs/*`, `fix/*` | Thiết lập, tài liệu hoặc sửa lỗi | Cùng quy trình PR như nhánh feature |

Không push trực tiếp lên `main` hoặc `develop`, kể cả sau khi được duyệt. Dùng chức năng merge PR để cập nhật nhánh đích. Theo quy trình nhóm, leader thực hiện merge; khả năng chỉ cho leader bấm merge còn phụ thuộc cấu hình quyền trên GitHub.

Leader dự kiến là `@nguyenthanhnhan020705`, theo chủ repository. File `.github/CODEOWNERS` chỉ có một người duyệt toàn bộ mã nguồn. Nếu leader dùng tài khoản khác, sửa file trước khi bật yêu cầu review của code owner.

## 2. Trước khi mời thành viên bắt đầu

Leader thực hiện lần thiết lập ban đầu:

1. Đưa BRD, roadmap, phân công và quy trình này lên nhánh chuẩn bị để rà soát.
2. Rà soát lịch sử/diff với `main` hiện có, đặc biệt vì repository có lịch sử xóa bộ khung cũ. Không merge toàn bộ nhánh chuẩn bị chỉ vì tài liệu mới đã đúng.
3. Tạo `develop` từ nền dự án đã chọn; đưa các tài liệu và `.github/CODEOWNERS` vào nhánh này.
4. Đưa riêng quy tắc quản trị, nhất là `.github/CODEOWNERS`, vào `main` trong lần thiết lập. `main` có thể chứa tài liệu quản trị trước khi có bản ứng dụng ổn định.
5. Bật bảo vệ cho cả `main` và `develop`, sau đó kiểm chứng trước khi cấp quyền làm việc cho thành viên.
6. Mời đúng 5 tài khoản làm cộng tác viên; không cấp quyền Admin hoặc quyền bỏ qua quy tắc cho thành viên.

CODEOWNERS được đọc từ **nhánh đích của PR**. File chỉ nằm trên nhánh chuẩn bị sẽ chưa bảo đảm yêu cầu review cho `main`/`develop`.

## 3. Cấu hình GitHub bắt buộc

Vào repository → Settings → Branches → Add branch protection rule. Tạo một rule cho `main` và một rule cho `develop`:

- Bật **Require a pull request before merging**.
- Bật **Require approvals**, đặt ít nhất **1**.
- Bật **Require review from Code Owners** để approval phải đến từ leader; một approval bất kỳ không đủ đáp ứng yêu cầu này.
- Bật **Dismiss stale pull request approvals when new commits are pushed** để thay đổi sau review phải được duyệt lại.
- Bật **Require conversation resolution before merging**.
- Không cho phép force push hoặc xóa nhánh được bảo vệ.
- Không cấp bypass cho thành viên. Nếu bật **Do not allow bypassing the above settings**, quy tắc áp dụng cả với admin.
- Khi Phase 1 có CI chạy thực tế, thêm đúng tên check vào **Require status checks to pass before merging**. Không yêu cầu tên check chưa tồn tại.

Nếu repository thuộc organization và có tùy chọn **Restrict who can push to matching branches**, có thể giới hạn leader để kiểm soát người thực hiện merge. Với repository cá nhân, yêu cầu approval của leader không đồng nghĩa chỉ leader có nút merge: người có quyền ghi vẫn có thể merge khi mọi điều kiện đã đạt. Quy tắc nhóm là để leader thực hiện thao tác đó.

GitHub Free hỗ trợ bảo vệ nhánh trên repository public; repository private cần gói hỗ trợ tương ứng. Nếu gói hiện tại không hỗ trợ, không coi README/CODEOWNERS là biện pháp chặn kỹ thuật. Cần chọn gói phù hợp hoặc cách cấp quyền đóng góp không cho thành viên ghi trực tiếp vào repository gốc; không tự đổi repository private thành public.

**PR do leader mở:** GitHub không cho tác giả tự approve PR của mình. Với leader là code owner duy nhất và không có bypass, nhờ thành viên mở PR tích hợp `develop` → `main` để leader review. Nếu muốn leader trực tiếp mở PR, phải thống nhất cơ chế reviewer/bypass riêng trước; không tự tắt bảo vệ để giải quyết.

**Kiểm chứng cấu hình:** dùng một PR thử do thành viên mở và kiểm tra GitHub chặn merge khi chưa được leader approve; sau approval, thêm một thay đổi và xác nhận cần review lại. Kiểm tra giao diện rules/protection và quyền thành viên; không cần thử push phá quy tắc lên `main`.

Nguồn: [Protected branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches), [Code owners](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners).

## 4. Các bước của thành viên

Chỉ thực hiện sau khi leader thông báo `develop` đã sẵn sàng. Ví dụ cho TV3:

```bash
git clone https://github.com/nguyenthanhnhan020705/student-feedback-ai.git
cd student-feedback-ai
git fetch origin
git switch -c feature/sentiment-baseline origin/develop
```

Nếu đã clone, dùng repository đang có và tạo nhánh mới từ `origin/develop` sau khi fetch. Repo từng có các nhánh feature cũ; không dùng lại hoặc merge nhánh cũ vào nền dự án mới khi chưa được rà soát.

```bash
git status
git diff
# Chỉ thêm đúng file của đầu việc; ví dụ khi các file sau đã được tạo:
git add ml/training.py notebooks/02_sentiment.ipynb
git diff --cached
git commit -m "feat: add sentiment baseline"
git push -u origin feature/sentiment-baseline
```

Trên GitHub, mở PR với **base: develop**, chọn nhánh vừa push làm compare và yêu cầu leader review. Dùng Draft PR nếu chưa sẵn sàng. Khi được yêu cầu sửa, tiếp tục commit/push vào chính nhánh đó, không mở PR mới cho cùng đầu việc.

Đồng bộ thay đổi mới khi cần, sau khi đã lưu công việc:

```bash
git fetch origin
git merge origin/develop
# Nếu có conflict: xử lý, kiểm tra lại, rồi commit và push nhánh công việc.
```

Không force push nhánh dùng chung, không tự sửa hợp đồng dữ liệu/API hoặc file thành viên khác đang phụ trách mà chưa trao đổi trong Issue/PR.

## 5. Điều kiện gửi review

- Mỗi PR gắn với một đầu việc có mã task và tiêu chí nghiệm thu; tránh dồn toàn bộ phase vào một PR lớn.
- Có hướng dẫn chạy, lệnh kiểm tra và kết quả thật. Nếu chưa chạy được, ghi rõ lý do và giữ Draft.
- Cung cấp phần báo cáo tương ứng: nguồn dữ liệu/EDA cho TV2, metrics và phân tích lỗi cho TV3/TV4, log API cho TV5, ảnh hoặc video thao tác thật cho TV6.
- Không commit `.env`, môi trường ảo, dữ liệu cá nhân hoặc dataset/model chưa được phép phân phối; không sử dụng số liệu hay dự đoán giả làm bằng chứng.
- Mỗi ngày cập nhật ngắn trong Issue: đã làm, sẽ làm, đang vướng; báo sớm khi phụ thuộc bị chặn.
- Hoàn thành khi leader đã duyệt, kiểm tra đạt và PR được merge; push code lên nhánh riêng chưa phải nghiệm thu.
