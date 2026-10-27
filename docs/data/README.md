# TV2 — Data

**Nhánh:** `feature/data-preprocessing`. **Issue đề xuất:** TEAM-01. **PR đích:** `develop`.

## File bắt đầu

- Code trống: `ml/data.py`, `ml/preprocessing.py`, `ml/labels.py`.
- Tests trống: `tests/test_data.py`, `test_preprocessing.py`, `test_labels.py`.
- Notebook rỗng: `notebooks/01_eda.ipynb`.
- Bạn điền: `docs/data/dataset.md`, `preprocessing.md`, `report.md`, `requirements/data.txt`.
- Nơi lưu kết quả thật: `reports/data/`, `reports/evidence/data/`; dataset local trong `data/raw/` và `data/processed/`.

## Làm ngay

1. Xác minh nguồn UIT-VSFC, quyền sử dụng, phiên bản, bảng nhãn và split; ghi nguồn trong `dataset.md`.
2. Theo hợp đồng leader chốt, viết loader, chuẩn hóa Unicode/khoảng trắng và bảng nhãn; tests cho rỗng, lệch dòng, nhãn lạ và giữ phủ định.
3. Kiểm tra số dòng, trùng lặp trong/giữa split và các nguy cơ rò rỉ dữ liệu; ghi chính sách xử lý.

## Bàn giao M1 sớm

Mở PR nhỏ với nguồn đã xác minh, schema, bảng nhãn, loader/chuẩn hóa có tests và manifest split. Sau khi leader duyệt, Sentiment/Topic nhận Data từ `develop` và có thể train thật. Bạn tiếp tục EDA, biểu đồ và báo cáo; không cần đợi toàn bộ EDA xong mới bàn giao M1.

## Hoàn thiện và nghiệm thu

- [ ] Dataset được kiểm đếm và đối chiếu nguồn thực tế, không chép số tham khảo thành số đo.
- [ ] EDA và biểu đồ phân bố nhãn/độ dài, phát hiện rỗng/trùng/mất cân bằng.
- [ ] Tests Data/chuẩn hóa/nhãn thực sự chạy đạt; ghi lệnh và log.
- [ ] Viết hướng dẫn tái lập và phần báo cáo Data. Đáp ứng AC-01, [Phase 2](../roadmap/phase-2-data.md).

Không sửa code mô hình/API/UI. Không công bố dataset chưa rõ quyền sử dụng. Thay đổi giao diện loader/nhãn/chuẩn hóa phải được leader duyệt và báo các phần dùng Data.
## Quy trình thực hiện bắt buộc

Phase 0 v1.0 đã được leader duyệt. Đọc [đặc tả chung](../specs/README.md), [môi trường](../specs/environment.md), [quyền sở hữu file](../function-ownership.md) và [quy trình đóng góp](../../CONTRIBUTING.md) trước khi code. Những mục nghiệm thu ở trên là yêu cầu cho phần việc của bạn, không phải kết quả đã hoàn thành.

### Nhận việc và vào đúng nhánh

- Leader giao tên người và hạn trong Issue; mã TEAM là mã đề xuất, không phải Issue GitHub đã được tạo. Chưa có Issue thì báo leader để xác định đầu việc, không tự suy đoán thời hạn.
- Khi đã được mời vào repo, clone bằng lệnh dưới. Nếu đã clone thì lưu công việc, fetch, chuyển đúng nhánh rồi `git pull --ff-only`; không clone lại và không reset để bỏ công việc.

```bash
git clone --branch feature/data-preprocessing https://github.com/nguyenthanhnhan020705/student-feedback-ai.git
cd student-feedback-ai
git status
```

- Chỉ sửa file thuộc vai trò của mình. File chung, thay đổi hợp đồng, dependencies gốc và công cụ mới cần thống nhất với leader trước khi thay đổi.
- Khai báo dependencies cần thiết cùng phiên bản đề xuất, báo leader để thống nhất môi trường. Requirements/config hiện là khung trống; không giả định đã cài đủ thư viện hoặc ứng dụng đã chạy được.
- Mốc gửi PR: M1: nguồn/quyền sử dụng, loader, nhãn, split và tests; EDA/báo cáo gửi PR tiếp theo.

### Trước mỗi lần bàn giao

1. Viết code và tests kiểm tra hành vi đúng/sai/biên liên quan; chỉ chạy trên fixture khi chưa có đầu ra thật từ phần phụ thuộc và ghi rõ giới hạn này.
2. Chạy kiểm tra phù hợp, ghi chính xác lệnh, môi trường, kết quả đạt/lỗi/skip. Không ghi “tests pass” nếu chưa có tests được chạy; không dùng mock làm bằng chứng tích hợp thật.
3. Cập nhật tài liệu vai trò và `report.md`: đã làm, cách chạy lại, đầu vào/đầu ra, kết quả, hạn chế và phần còn thiếu. Dữ liệu/model lớn hoặc chưa có quyền phân phối không đưa lên repo public; ghi cách nhận/tái tạo được leader duyệt.
4. Kiểm tra `git status`, `git diff`, chỉ stage các đường dẫn đã kiểm tra thuộc phần mình; xem `git diff --cached` trước khi commit. Không đưa `.env`, token, cache hay môi trường ảo vào commit.
5. Commit và push đúng nhánh:

```bash
git commit -m "feat: mô tả đầu việc đã hoàn thành"
git push origin feature/data-preprocessing
```

### Nội dung PR gửi leader

Mở PR từ `feature/data-preprocessing` vào **`develop`**, yêu cầu review từ `@nguyenthanhnhan020705`, gửi link PR cho leader. Mỗi PR ghi đủ:

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
