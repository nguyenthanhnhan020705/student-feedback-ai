# Phase 3 — Huấn luyện và đánh giá mô hình

**Trạng thái:** Chưa bắt đầu.  
**Thời gian:** Ngày 6–10.  
**Phụ trách:** TV3 sở hữu Sentiment; TV4 sở hữu Topic; mỗi người sửa code/tests/metadata của nhiệm vụ mình, dùng Data đã được TV2 bàn giao.  
**Phụ thuộc:** Phase 2 đạt, bảng mã và split đã xác minh.  
**Quay lại:** [Lộ trình](README.md).

## Mục tiêu

So sánh Multinomial Naive Bayes, Logistic Regression và Linear SVM cho từng nhiệm vụ; chọn và bàn giao hai pipeline thực. Đáp ứng BR-02, FR-05, RULE-02–06, NFR-01/02/05 và AC-02.

## Công việc

- [ ] P3.1: Định nghĩa cấu hình thí nghiệm dùng chung, seed nếu có và cách lưu kết quả; viết kiểm thử ranh giới train/validation/test.
- [ ] P3.2: Tạo pipeline TF-IDF + classifier cho ba thuật toán; mỗi nhiệm vụ có pipeline độc lập, dùng lại tiền xử lý Phase 2.
- [ ] P3.3: Huấn luyện sentiment và topic trên train; ghi chỉ số validation cho từng thuật toán và cấu hình.
- [ ] P3.4: Chọn một pipeline cho mỗi nhiệm vụ bằng Macro F1 validation; ghi quy tắc xử lý khi kết quả gần nhau và lý do lựa chọn.
- [ ] P3.5: Chốt cấu hình trước khi đánh giá test; báo cáo Accuracy, Macro Precision/Recall/F1, chỉ số từng lớp và Confusion Matrix. Không điều chỉnh lại mô hình dựa trên điểm test.
- [ ] P3.6: Phân tích lỗi ở lớp ít mẫu, các cặp nhãn dễ nhầm và câu nhiều cảm xúc/chủ đề; phân biệt ví dụ minh họa với kết quả chạy thật.
- [ ] P3.7: Xuất toàn bộ hai pipeline và metadata; tải lại trong tiến trình mới, đối chiếu dự đoán với trước khi lưu.

## Sản phẩm dự kiến

| File | Trách nhiệm |
| --- | --- |
| `ml/train_sentiment.py`, `ml/evaluate_sentiment.py`, `ml/predict_sentiment.py` | TV3: huấn luyện, đánh giá, suy luận sentiment |
| `ml/train_topic.py`, `ml/evaluate_topic.py`, `ml/predict_topic.py` | TV4: huấn luyện, đánh giá, suy luận topic |
| `notebooks/02_sentiment.ipynb`, `notebooks/03_topic.ipynb` | Tái hiện thí nghiệm cho từng nhiệm vụ |
| `models/sentiment_pipeline.joblib`, `models/topic_pipeline.joblib` | Hai pipeline đã chọn; chỉ phân phối theo quyền phù hợp |
| `models/sentiment_metadata.json`, `models/topic_metadata.json` | Metadata riêng từng nhiệm vụ, do chủ mô hình tương ứng quản lý |
| `reports/metrics/`, `reports/figures/` | Bảng chỉ số và biểu đồ được sinh từ mã |
| `tests/test_sentiment_training.py`, `tests/test_sentiment_artifacts.py` | TV3: ranh giới fit và lưu/tải sentiment |
| `tests/test_topic_training.py`, `tests/test_topic_artifacts.py` | TV4: ranh giới fit và lưu/tải topic |

## Điều kiện hoàn thành và kiểm chứng

- Có hai bảng so sánh, mỗi bảng đủ ba thuật toán; metadata nối được kết quả với dữ liệu/cấu hình cụ thể.
- Mỗi người chạy tests nhiệm vụ mình; lệnh dự kiến khi đã có tests là `python -m pytest tests/test_sentiment_training.py tests/test_sentiment_artifacts.py -q` hoặc `python -m pytest tests/test_topic_training.py tests/test_topic_artifacts.py -q`. Kiểm thử nhanh bằng dữ liệu nhỏ không thay thế thí nghiệm trên dataset thực.
- Hai pipeline tải được trên môi trường phục vụ API và giữ nguyên nhãn dự đoán cho tập đối chiếu cố định.
- Có chỉ số thực tế và phân tích lỗi; không đặt thêm ngưỡng Accuracy/F1 nghiệm thu khi BRD chưa quy định.

Bàn giao artifact, bảng nhãn, metadata và hướng dẫn tải cho Phase 4; bảng kết quả và giới hạn mô hình chuyển sang báo cáo Phase 6.
