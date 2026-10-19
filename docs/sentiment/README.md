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
