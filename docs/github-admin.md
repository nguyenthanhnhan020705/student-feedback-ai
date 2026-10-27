# Quản trị GitHub — dành cho leader

Repo đã được chuyển public theo lựa chọn của leader, có `main`, `develop` và 5 nhánh chức năng. Hai nhánh chính đã bật PR/review của code owner là leader; phần dưới giữ hướng dẫn quản trị để đối chiếu khi cần. Thành viên đọc CONTRIBUTING và tài liệu vai trò, không tự thay đổi cấu hình bảo vệ.

Lời mời, tên tài khoản và hạn giao việc do leader thực hiện. Không tắt bảo vệ hoặc cấp bypass để đưa khung file mới vào nhánh chính; dùng PR do thành viên mở và leader review.

## 1. Checklist quản trị trước khi mời thành viên

Leader thực hiện lần thiết lập ban đầu:

1. Đưa BRD, roadmap, phân công và quy trình này lên nhánh chuẩn bị để rà soát.
2. Rà soát lịch sử/diff với `main` hiện có, đặc biệt vì repository có lịch sử xóa bộ khung cũ. Không merge toàn bộ nhánh chuẩn bị chỉ vì tài liệu mới đã đúng.
3. Tạo `develop` từ nền dự án đã chọn; đưa các tài liệu và `.github/CODEOWNERS` vào nhánh này.
4. Đưa riêng quy tắc quản trị, nhất là `.github/CODEOWNERS`, vào `main` trong lần thiết lập. `main` có thể chứa tài liệu quản trị trước khi có bản ứng dụng ổn định.
5. Bật bảo vệ cho cả `main` và `develop`, sau đó kiểm chứng trước khi cấp quyền làm việc cho thành viên.
6. Mời đúng 5 tài khoản làm cộng tác viên; không cấp quyền Admin hoặc quyền bỏ qua quy tắc cho thành viên.

CODEOWNERS được đọc từ **nhánh đích của PR**. File chỉ nằm trên nhánh chuẩn bị sẽ chưa bảo đảm yêu cầu review cho `main`/`develop`.

## 2. Cấu hình GitHub bắt buộc

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
