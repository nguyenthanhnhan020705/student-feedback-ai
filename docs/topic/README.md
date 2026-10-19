# TV4 — Topic

**Nhánh:** `feature/topic-model`. **Issue đề xuất:** TEAM-03. **PR đích:** `develop`.

## File bắt đầu

- Code trống: `ml/train_topic.py`, `evaluate_topic.py`, `predict_topic.py`.
- Tests trống: `tests/test_topic_training.py`, `test_topic_artifacts.py`.
- Notebook rỗng: `notebooks/03_topic.ipynb`.
- Bạn điền: `docs/topic/experiment.md`, `report.md`, `requirements/topic.txt`.
- Kết quả thật: `reports/metrics/topic/`, `reports/figures/topic/`, `reports/evidence/topic/`.

## Làm song song ngay sau M0

1. Viết thiết kế thí nghiệm riêng theo hợp đồng Data/model; khai báo dependencies riêng.
2. Viết pipeline TF-IDF + NB/LR/SVM, mã đánh giá/lưu-tải và tests bằng fixture nhỏ, nhận diện rõ đây là dữ liệu kiểm thử.
3. Không chờ Sentiment, không sửa file Sentiment/Data; chuẩn bị phân tích nhầm lẫn và lớp ít mẫu cho chủ đề.

## Khi nhận M1 từ Data

Đồng bộ `origin/develop`, dùng đúng loader, bảng mã và chuẩn hóa được bàn giao. Train trên train, chọn bằng Macro F1 validation; chốt cấu hình/quy tắc hòa trước đánh giá cuối trên test.

## Bàn giao M2-T và nghiệm thu

- [ ] Bảng so sánh 3 thuật toán, Accuracy/Macro Precision/Recall/F1, chỉ số từng lớp và Confusion Matrix.
- [ ] Phân tích lỗi, câu nhiều chủ đề và các cặp nhãn dễ nhầm bằng kết quả thật.
- [ ] Sinh `models/topic_pipeline.joblib`, `models/topic_metadata.json`; tests tải lại trong tiến trình mới và đối chiếu dự đoán.
- [ ] Giao Backend artifact/metadata/hướng dẫn tải; giao leader phần báo cáo. Đáp ứng phần topic của AC-02, [Phase 3](../roadmap/phase-3-models.md).

Không suy đoán mã nhãn, fit trên validation/test hoặc điều chỉnh theo điểm test cuối. Không tạo file huấn luyện/metadata dùng chung với Sentiment.
