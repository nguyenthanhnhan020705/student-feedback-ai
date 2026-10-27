# TV3 — Sentiment

**Nhánh:** `feature/sentiment-model`. **Issue đề xuất:** TEAM-02. **PR đích:** `develop`.

## File bắt đầu

- Code trống: `ml/train_sentiment.py`, `evaluate_sentiment.py`, `predict_sentiment.py`.
- Tests trống: `tests/test_sentiment_training.py`, `test_sentiment_artifacts.py`.
- Notebook rỗng: `notebooks/02_sentiment.ipynb`.
- Bạn điền: `docs/sentiment/experiment.md`, `report.md`, `requirements/sentiment.txt`.
- Kết quả thật: `reports/metrics/sentiment/`, `reports/figures/sentiment/`, `reports/evidence/sentiment/`.

## Làm song song ngay sau M0

1. Viết thiết kế thí nghiệm riêng theo hợp đồng Data/model đã chốt; khai báo dependencies riêng.
2. Viết pipeline TF-IDF + NB/LR/SVM, mã đánh giá/lưu-tải và tests với fixture nhỏ. Fixture chỉ là dữ liệu kiểm thử, không đưa vào báo cáo như thí nghiệm thật.
3. Giữ code/tests riêng; không chờ Topic và không sửa file Data/Topic.

## Khi nhận M1 từ Data

Đồng bộ `origin/develop`, dùng loader/chuẩn hóa/bảng nhãn đã duyệt. Train trên train, so sánh bằng Macro F1 validation. Chốt cấu hình và quy tắc hòa điểm trước khi đánh giá cuối trên test.

## Bàn giao M2-S và nghiệm thu

- [ ] Bảng so sánh 3 thuật toán, Accuracy/Macro Precision/Recall/F1, chỉ số từng lớp, Confusion Matrix và phân tích lỗi.
- [ ] Sinh `models/sentiment_pipeline.joblib` và `models/sentiment_metadata.json` từ pipeline thật; tuân thủ quyền phân phối và hướng dẫn artifact.
- [ ] Tải lại trong tiến trình mới, đối chiếu dự đoán trước/sau lưu, ghi tests/log.
- [ ] Giao Backend artifact + metadata + hướng dẫn tải và câu đối chiếu; giao leader phần báo cáo. Đáp ứng phần sentiment của AC-02, [Phase 3](../roadmap/phase-3-models.md).

Không fit trên validation/test; không điều chỉnh mô hình lặp lại theo điểm test cuối. Không tự viết lại tiền xử lý ngoài pipeline hoặc tạo metrics/điểm tin cậy giả.
## Quy trình thực hiện bắt buộc

Phase 0 v1.0 đã được leader duyệt. Đọc [đặc tả chung](../specs/README.md), [môi trường](../specs/environment.md), [quyền sở hữu file](../function-ownership.md) và [quy trình đóng góp](../../CONTRIBUTING.md) trước khi code. Những mục nghiệm thu ở trên là yêu cầu cho phần việc của bạn, không phải kết quả đã hoàn thành.

### Nhận việc và vào đúng nhánh

- Leader giao tên người và hạn trong Issue; mã TEAM là mã đề xuất, không phải Issue GitHub đã được tạo. Chưa có Issue thì báo leader để xác định đầu việc, không tự suy đoán thời hạn.
- Khi đã được mời vào repo, clone bằng lệnh dưới. Nếu đã clone thì lưu công việc, fetch, chuyển đúng nhánh rồi `git pull --ff-only`; không clone lại và không reset để bỏ công việc.

```bash
git clone --branch feature/sentiment-model https://github.com/nguyenthanhnhan020705/student-feedback-ai.git
cd student-feedback-ai
git status
```

- Chỉ sửa file thuộc vai trò của mình. File chung, thay đổi hợp đồng, dependencies gốc và công cụ mới cần thống nhất với leader trước khi thay đổi.
- Khai báo dependencies cần thiết cùng phiên bản đề xuất, báo leader để thống nhất môi trường. Requirements/config hiện là khung trống; không giả định đã cài đủ thư viện hoặc ứng dụng đã chạy được.
- Mốc gửi PR: PR đầu: pipeline và tests fixture; M2-S: thí nghiệm thật, artifact/metadata và báo cáo sau khi nhận M1.

### Trước mỗi lần bàn giao

1. Viết code và tests kiểm tra hành vi đúng/sai/biên liên quan; chỉ chạy trên fixture khi chưa có đầu ra thật từ phần phụ thuộc và ghi rõ giới hạn này.
2. Chạy kiểm tra phù hợp, ghi chính xác lệnh, môi trường, kết quả đạt/lỗi/skip. Không ghi “tests pass” nếu chưa có tests được chạy; không dùng mock làm bằng chứng tích hợp thật.
3. Cập nhật tài liệu vai trò và `report.md`: đã làm, cách chạy lại, đầu vào/đầu ra, kết quả, hạn chế và phần còn thiếu. Dữ liệu/model lớn hoặc chưa có quyền phân phối không đưa lên repo public; ghi cách nhận/tái tạo được leader duyệt.
4. Kiểm tra `git status`, `git diff`, chỉ stage các đường dẫn đã kiểm tra thuộc phần mình; xem `git diff --cached` trước khi commit. Không đưa `.env`, token, cache hay môi trường ảo vào commit.
5. Commit và push đúng nhánh:

```bash
git commit -m "feat: mô tả đầu việc đã hoàn thành"
git push origin feature/sentiment-model
```

### Nội dung PR gửi leader

Mở PR từ `feature/sentiment-model` vào **`develop`**, yêu cầu review từ `@nguyenthanhnhan020705`, gửi link PR cho leader. Mỗi PR ghi đủ:

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
