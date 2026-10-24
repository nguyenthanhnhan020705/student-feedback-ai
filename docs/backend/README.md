# TV5 — Backend

**Nhánh:** `feature/backend-api`. **Issue đề xuất:** TEAM-04. **PR đích:** `develop`.

## File bắt đầu

- Toàn bộ `backend/`: main/config/schemas/model_service, routes health/predict; file batch/dashboard dành cho P1.
- Tests: `tests/test_health.py`, `test_model_service.py`, `test_predict.py`; `test_batch.py`, `test_dashboard_data.py` dành cho P1.
- Bạn điền: `docs/backend/api-notes.md`, `report.md`, `requirements/backend.txt`; minh chứng thật trong `reports/evidence/backend/`.

## Làm song song ngay sau M0

1. Theo JSON/lỗi leader chốt, viết schema, FastAPI, cấu hình và health; ứng dụng khởi động được khi thiếu model và báo đúng mức sẵn sàng.
2. Viết validation cho input rỗng/sai kiểu/vượt giới hạn, xử lý lỗi artifact thiếu/hỏng/không tương thích.
3. Viết service suy luận tách biệt để unit tests có thể dùng test double; không trả nhãn mẫu từ API thật thay cho model chưa có.
4. Giao Frontend hợp đồng đã triển khai và lệnh chạy API; khung health/lỗi có thể bàn giao trước khi có model.

## Khi nhận M2-S và M2-T

Tải hai pipeline thật theo metadata; không tự train hoặc viết lại Data. Đối chiếu dự đoán API với gọi trực tiếp cùng artifact, xác nhận M3 với Frontend. Leader phụ trách kiểm thử tích hợp chung.

## Nghiệm thu

- [ ] Health, predict, input/lỗi/model có tests và log thực tế; đáp ứng AC-04/07 và phần API của AC-03.
- [ ] `api-notes.md` ghi cách chạy và ví dụ request/response, không tự đổi đặc tả leader chốt.
- [ ] P1 nếu được duyệt: CSV/batch/export, dữ liệu thống kê và tests; chưa được duyệt thì giữ file P1 trống.
- [ ] Hoàn thành phần báo cáo và bàn giao Frontend API dùng model thật. Xem [Phase 4](../roadmap/phase-4-mvp.md), [Phase 5](../roadmap/phase-5-batch-dashboard.md).

Không sửa UI/ML hoặc dependencies gốc. Đề xuất thay đổi giao diện chung qua leader.
## Quy trình thực hiện bắt buộc

Phase 0 v1.0 đã được leader duyệt. Đọc [đặc tả chung](../specs/README.md), [môi trường](../specs/environment.md), [quyền sở hữu file](../function-ownership.md) và [quy trình đóng góp](../../CONTRIBUTING.md) trước khi code. Những mục nghiệm thu ở trên là yêu cầu cho phần việc của bạn, không phải kết quả đã hoàn thành.

### Nhận việc và vào đúng nhánh

- Leader giao tên người và hạn trong Issue; mã TEAM là mã đề xuất, không phải Issue GitHub đã được tạo. Chưa có Issue thì báo leader để xác định đầu việc, không tự suy đoán thời hạn.
- Khi đã được mời vào repo, clone bằng lệnh dưới. Nếu đã clone thì lưu công việc, fetch, chuyển đúng nhánh rồi `git pull --ff-only`; không clone lại và không reset để bỏ công việc.

```bash
git clone --branch feature/backend-api https://github.com/nguyenthanhnhan020705/student-feedback-ai.git
cd student-feedback-ai
git status
```

- Chỉ sửa file thuộc vai trò của mình. File chung, thay đổi hợp đồng, dependencies gốc và công cụ mới cần thống nhất với leader trước khi thay đổi.
- Khai báo dependencies cần thiết cùng phiên bản đề xuất, báo leader để thống nhất môi trường. Requirements/config hiện là khung trống; không giả định đã cài đủ thư viện hoặc ứng dụng đã chạy được.
- Mốc gửi PR: PR đầu: health, schema, validation và tests khi chưa có model; M3: API dùng hai model thật sau M2-S/M2-T.

### Trước mỗi lần bàn giao

1. Viết code và tests kiểm tra hành vi đúng/sai/biên liên quan; chỉ chạy trên fixture khi chưa có đầu ra thật từ phần phụ thuộc và ghi rõ giới hạn này.
2. Chạy kiểm tra phù hợp, ghi chính xác lệnh, môi trường, kết quả đạt/lỗi/skip. Không ghi “tests pass” nếu chưa có tests được chạy; không dùng mock làm bằng chứng tích hợp thật.
3. Cập nhật tài liệu vai trò và `report.md`: đã làm, cách chạy lại, đầu vào/đầu ra, kết quả, hạn chế và phần còn thiếu. Dữ liệu/model lớn hoặc chưa có quyền phân phối không đưa lên repo public; ghi cách nhận/tái tạo được leader duyệt.
4. Kiểm tra `git status`, `git diff`, chỉ stage các đường dẫn đã kiểm tra thuộc phần mình; xem `git diff --cached` trước khi commit. Không đưa `.env`, token, cache hay môi trường ảo vào commit.
5. Commit và push đúng nhánh:

```bash
git commit -m "feat: mô tả đầu việc đã hoàn thành"
git push origin feature/backend-api
```

### Nội dung PR gửi leader

Mở PR từ `feature/backend-api` vào **`develop`**, yêu cầu review từ `@nguyenthanhnhan020705`, gửi link PR cho leader. Mỗi PR ghi đủ:

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
