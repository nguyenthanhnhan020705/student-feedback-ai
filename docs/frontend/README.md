# TV6 — Frontend

**Nhánh:** `feature/frontend-dashboard`. **Issue đề xuất:** TEAM-05. **PR đích:** `develop`.

## File bắt đầu

- `frontend/index.html`, `styles.css`, `app.js`, `api.js`.
- `frontend/batch.js`, `dashboard.js` dành cho P1; chưa được duyệt thì giữ trống.
- `tests/frontend/test_ui.py` là chỗ viết kiểm thử trình duyệt sau khi leader chốt công cụ.
- Bạn điền: `docs/frontend/ui-notes.md`, `report.md`; ảnh/video thật trong `reports/evidence/frontend/`.

## Làm song song ngay sau M0

1. Xây bố cục, form nhập, nút phân tích và trạng thái loading/error/result theo luồng leader chốt.
2. Viết lớp gọi API theo JSON đã thống nhất; xử lý lỗi input, mất kết nối và model chưa sẵn sàng.
3. Khi API chưa có, có thể dùng fixture/mock riêng để thiết kế và kiểm thử UI. Hiển thị rõ dữ liệu mẫu, không dùng làm minh chứng dự đoán thật hoặc làm fallback kết quả trên bản nghiệm thu.
4. Kiểm tra giao diện/trạng thái và ghi hướng dẫn chạy frontend khi đã triển khai.

## Khi Backend bàn giao API

Kết nối health/predict; xác nhận lỗi và dữ liệu đúng hợp đồng. M4 cần chạy câu mới qua trình duyệt → API → hai model thật, có log/ảnh đối chiếu. Không cần đợi model để bắt đầu dựng giao diện.

## Nghiệm thu

- [ ] Trạng thái nhập/chờ/kết quả/lỗi hoạt động đúng và có kiểm tra trình duyệt.
- [ ] Hai nhãn đến từ API thật; ảnh/video demo tương ứng lần chạy thực tế.
- [ ] P1 nếu được duyệt: UI CSV/export/Dashboard khớp dữ liệu thực tế; không sửa logic API/ML.
- [ ] Hoàn thành hướng dẫn UI và phần báo cáo. Đáp ứng phần UI của AC-03, AC-06 nếu có; [Phase 4](../roadmap/phase-4-mvp.md), [Phase 5](../roadmap/phase-5-batch-dashboard.md).
## Quy trình thực hiện bắt buộc

Phase 0 v1.0 đã được leader duyệt. Đọc [đặc tả chung](../specs/README.md), [môi trường](../specs/environment.md), [quyền sở hữu file](../function-ownership.md) và [quy trình đóng góp](../../CONTRIBUTING.md) trước khi code. Những mục nghiệm thu ở trên là yêu cầu cho phần việc của bạn, không phải kết quả đã hoàn thành.

### Nhận việc và vào đúng nhánh

- Leader giao tên người và hạn trong Issue; mã TEAM là mã đề xuất, không phải Issue GitHub đã được tạo. Chưa có Issue thì báo leader để xác định đầu việc, không tự suy đoán thời hạn.
- Khi đã được mời vào repo, clone bằng lệnh dưới. Nếu đã clone thì lưu công việc, fetch, chuyển đúng nhánh rồi `git pull --ff-only`; không clone lại và không reset để bỏ công việc.

```bash
git clone --branch feature/frontend-dashboard https://github.com/nguyenthanhnhan020705/student-feedback-ai.git
cd student-feedback-ai
git status
```

- Chỉ sửa file thuộc vai trò của mình. File chung, thay đổi hợp đồng, dependencies gốc và công cụ mới cần thống nhất với leader trước khi thay đổi.
- Khai báo dependencies cần thiết cùng phiên bản đề xuất, báo leader để thống nhất môi trường. Requirements/config hiện là khung trống; không giả định đã cài đủ thư viện hoặc ứng dụng đã chạy được.
- Mốc gửi PR: PR đầu: form/trạng thái và gọi API theo hợp đồng, mock được nhận diện rõ; M4: kiểm tra toàn luồng với API/model thật.

### Trước mỗi lần bàn giao

1. Viết code và tests kiểm tra hành vi đúng/sai/biên liên quan; chỉ chạy trên fixture khi chưa có đầu ra thật từ phần phụ thuộc và ghi rõ giới hạn này.
2. Chạy kiểm tra phù hợp, ghi chính xác lệnh, môi trường, kết quả đạt/lỗi/skip. Không ghi “tests pass” nếu chưa có tests được chạy; không dùng mock làm bằng chứng tích hợp thật.
3. Cập nhật tài liệu vai trò và `report.md`: đã làm, cách chạy lại, đầu vào/đầu ra, kết quả, hạn chế và phần còn thiếu. Dữ liệu/model lớn hoặc chưa có quyền phân phối không đưa lên repo public; ghi cách nhận/tái tạo được leader duyệt.
4. Kiểm tra `git status`, `git diff`, chỉ stage các đường dẫn đã kiểm tra thuộc phần mình; xem `git diff --cached` trước khi commit. Không đưa `.env`, token, cache hay môi trường ảo vào commit.
5. Commit và push đúng nhánh:

```bash
git commit -m "feat: mô tả đầu việc đã hoàn thành"
git push origin feature/frontend-dashboard
```

### Nội dung PR gửi leader

Mở PR từ `feature/frontend-dashboard` vào **`develop`**, yêu cầu review từ `@nguyenthanhnhan020705`, gửi link PR cho leader. Mỗi PR ghi đủ:

- Issue/task và mốc bàn giao; thay đổi đã làm và file chính.
- Đối chiếu checklist nghiệm thu của vai trò; mục chưa làm ghi rõ.
- Lệnh tái lập/kiểm thử, phiên bản môi trường, kết quả thật và nơi lưu log/ảnh/metrics thích hợp.
- Đầu ra phụ thuộc còn thiếu; phân biệt phần đã kiểm bằng fixture với phần đã kiểm bằng dữ liệu/model/API thật.
- Hướng dẫn nhận artifact nếu có, thay đổi dependencies đề xuất và vấn đề cần leader quyết định.

Không đợi xong toàn bộ chức năng mới gửi PR. Khi vướng mắc, báo trong Issue/PR: bước đang làm, lệnh tái hiện, lỗi đã bỏ thông tin nhạy cảm và phần cần hỗ trợ.

### Khi review phát hiện lỗi

- Leader có thể lấy nhánh/PR về máy để kiểm tra trước khi merge; thành viên phải cung cấp cách chạy tái lập được.
- Sửa theo từng nhận xét, bổ sung kiểm thử cho lỗi khi phù hợp, chạy lại kiểm tra liên quan; commit/push tiếp **cùng nhánh, cùng PR**.
- Trả lời nhận xét bằng thay đổi/kết quả kiểm tra; chưa đồng ý thì giải thích để thống nhất. Không tự đánh dấu yêu cầu review đã được leader chấp thuận.
- Không tự merge, push trực tiếp `main`/`develop`, force push hay sửa code của vai trò khác để vượt lỗi. Nếu có conflict không chắc cách xử lý thì báo leader, giữ lại công việc.
- Sau khi leader duyệt và merge, lưu công việc rồi đồng bộ nhánh của mình:

```bash
git fetch origin
git merge origin/develop
```

Chạy lại kiểm tra liên quan rồi push nhánh mình. Chỉ lấy phần của người khác qua `develop` sau khi được duyệt. Đầu việc chỉ hoàn thành khi đã review/merge và có đủ minh chứng nghiệm thu; phần P1 chỉ làm khi leader cho phép.
