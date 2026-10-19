# Quyền sở hữu file và đầu ra của 5 chức năng

**Nguyên tắc:** một chủ sở hữu cho mỗi file. Cần thay đổi phần khác thì gửi yêu cầu cho người phụ trách và leader, không tự sửa file của nhau. Đây là phân công công việc; nhánh Git không tự khóa quyền sửa file của một tài khoản.

## 1. Phạm vi file

| Chủ sở hữu | File / thư mục được sửa |
| --- | --- |
| Leader | `README.md`, `CONTRIBUTING.md`, `.github/`, `.gitignore`, `pytest.ini`, root `requirements*.txt`, `ml/__init__.py`, `docs/specs/`, `docs/decisions.md`, roadmap, phân công, `docs/development.md`, `docs/acceptance.md`, `tests/integration/`, báo cáo/slide tổng hợp |
| Data | `ml/data.py`, `ml/preprocessing.py`, `ml/labels.py`, `notebooks/01_eda.ipynb`, `docs/data/`, `reports/data/`, `tests/test_data.py`, `tests/test_preprocessing.py`, `tests/test_labels.py`, `requirements/data.txt` |
| Sentiment | `ml/train_sentiment.py`, `ml/evaluate_sentiment.py`, `ml/predict_sentiment.py`, `notebooks/02_sentiment.ipynb`, `docs/sentiment/`, `tests/test_sentiment*.py`, `reports/metrics/sentiment*.json`, `reports/figures/sentiment/`, `reports/evidence/sentiment/`, `models/sentiment_pipeline.joblib`, `models/sentiment_metadata.json`, `requirements/sentiment.txt` |
| Topic | `ml/train_topic.py`, `ml/evaluate_topic.py`, `ml/predict_topic.py`, `notebooks/03_topic.ipynb`, `docs/topic/`, `tests/test_topic*.py`, `reports/metrics/topic*.json`, `reports/figures/topic/`, `reports/evidence/topic/`, `models/topic_pipeline.joblib`, `models/topic_metadata.json`, `requirements/topic.txt` |
| Backend | `backend/`, `docs/backend/`, `tests/test_health.py`, `tests/test_model_service.py`, `tests/test_predict.py`, `tests/test_batch.py`, `tests/test_dashboard_data.py`, `reports/evidence/backend/`, `requirements/backend.txt` |
| Frontend | `frontend/`, `docs/frontend/`, `tests/frontend/`, `reports/evidence/frontend/` |

Các đường dẫn sản phẩm là dự kiến, chưa phải file đã triển khai. Dataset và artifact phải tuân thủ quyền sử dụng và `.gitignore`; không tự công bố trên repo public.

Data sở hữu code dùng chung về loader, chuẩn hóa và bảng nhãn. Sentiment/Topic sử dụng các giao diện đó và tự làm phần mô hình trong file riêng; Backend tải pipeline thay vì viết lại tiền xử lý. Không có hai người cùng sửa một file training/evaluation hoặc một file metadata.

## 2. Đầu ra nghiệm thu theo chức năng

### Data — TV2

- Xác minh nguồn/quyền sử dụng, phiên bản, mã nhãn và split UIT-VSFC.
- Kiểm tra rỗng, lệch dòng, nhãn lạ, trùng lặp trong/giữa split; EDA và biểu đồ.
- Loader, chuẩn hóa Unicode/khoảng trắng giữ phủ định/sắc thái; tests và manifest.
- Bàn giao giao diện Data cho Sentiment/Topic và phần báo cáo dữ liệu cho leader. Đáp ứng AC-01, [Phase 2](roadmap/phase-2-data.md).

### Sentiment — TV3

- NB/LR/SVM cho cảm xúc; chỉ fit trên train, chọn bằng Macro F1 validation.
- Chốt cấu hình trước test cuối, báo cáo đầy đủ chỉ số, Confusion Matrix và phân tích lỗi.
- Pipeline, metadata, tests tải lại và hướng dẫn riêng; bàn giao cho Backend.
- Đáp ứng phần sentiment của AC-02, [Phase 3](roadmap/phase-3-models.md); không sửa Data/Topic.

### Topic — TV4

- NB/LR/SVM cho chủ đề theo bảng nhãn Data đã xác minh; cùng quy tắc train/validation/test.
- Metrics, Confusion Matrix, phân tích nhầm lẫn, pipeline, metadata và tests tải lại riêng.
- Bàn giao artifact đúng quyền cho Backend và phần báo cáo topic cho leader.
- Đáp ứng phần topic của AC-02, [Phase 3](roadmap/phase-3-models.md); không sửa Data/Sentiment.

### Backend — TV5

- FastAPI, health, cấu hình, kiểm tra/nạp hai pipeline và `/api/predict` theo hợp đồng leader chốt.
- Kiểm tra input, lỗi model/mạng, tests API và hướng dẫn chạy cho Frontend.
- P1 nếu được leader cho phép: batch CSV/export và dữ liệu thống kê, không làm giao diện.
- Đáp ứng AC-04/07, phần API của AC-03 và AC-05 nếu có; xem [Phase 4](roadmap/phase-4-mvp.md).

### Frontend — TV6

- Toàn bộ HTML/CSS/JavaScript, nhập câu, trạng thái chờ, kết quả và lỗi theo JSON API.
- P1 nếu được leader cho phép: UI tải/xuất CSV và biểu đồ Dashboard từ dữ liệu thật.
- Kiểm tra trình duyệt, ảnh/video thực tế, hướng dẫn UI và phần báo cáo frontend.
- Đáp ứng phần UI của AC-03 và AC-06 nếu có; xem [Phase 4](roadmap/phase-4-mvp.md). Không sửa API/ML.

## 3. Phối hợp bằng bàn giao

1. Leader tự chốt Phase 0. Data có thể khảo sát nguồn; Backend/Frontend có thể chuẩn bị bố cục theo đặc tả khi đã chốt.
2. Data được review và merge vào `develop`; Sentiment/Topic cập nhật `develop` rồi dùng Data đã duyệt.
3. Hai phần mô hình được duyệt; Backend cập nhật `develop`, nhận artifact đúng quyền và tích hợp.
4. Frontend cập nhật API thật; leader chạy nghiệm thu tích hợp và tổng hợp báo cáo.
5. Bản tích hợp ổn định được đưa qua PR `develop` → `main`, cần leader duyệt.

Mỗi người nên mở nhiều PR nhỏ trên nhánh của mình, không đợi xong cả dự án. Không merge trực tiếp nhánh người khác; dùng `develop` làm nơi nhận phần đã được leader duyệt. Không dùng nhãn/metrics giả để đánh dấu nghiệm thu.
