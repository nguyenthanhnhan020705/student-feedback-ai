# Quyền sở hữu file

Một file có một người chịu trách nhiệm. Các nhánh đều chứa cả repository để tích hợp được, nhưng mỗi người chỉ sửa phần được giao. [Manifest khung file](scaffold-manifest.json) liệt kê chính xác file trống đã tạo, chủ sở hữu và phạm vi P0/P1.

| Chủ sở hữu | Phạm vi |
| --- | --- |
| Leader | README/CONTRIBUTING, `.github/`, `.gitignore`, `.env.example`, root `requirements*.txt`, `pytest.ini`, `ml/__init__.py`, roadmap/phân công/manifest, `docs/specs/`, `docs/decisions.md`, `docs/development.md`, `docs/acceptance.md`, `tests/integration/`, báo cáo tổng hợp |
| Data | `ml/data.py`, `ml/preprocessing.py`, `ml/labels.py`, `notebooks/01_eda.ipynb`, `docs/data/`, `reports/data/`, `reports/evidence/data/`, `tests/test_data.py`, `tests/test_preprocessing.py`, `tests/test_labels.py`, `requirements/data.txt`, dữ liệu local `data/raw/` và `data/processed/` |
| Sentiment | `ml/train_sentiment.py`, `ml/evaluate_sentiment.py`, `ml/predict_sentiment.py`, `notebooks/02_sentiment.ipynb`, `docs/sentiment/`, `tests/test_sentiment*.py`, `reports/metrics/sentiment/`, `reports/figures/sentiment/`, `reports/evidence/sentiment/`, `requirements/sentiment.txt`; artifact sinh ra `models/sentiment_pipeline.joblib` và `models/sentiment_metadata.json` |
| Topic | `ml/train_topic.py`, `ml/evaluate_topic.py`, `ml/predict_topic.py`, `notebooks/03_topic.ipynb`, `docs/topic/`, `tests/test_topic*.py`, `reports/metrics/topic/`, `reports/figures/topic/`, `reports/evidence/topic/`, `requirements/topic.txt`; artifact sinh ra `models/topic_pipeline.joblib` và `models/topic_metadata.json` |
| Backend | `backend/`, `docs/backend/`, tests health/model_service/predict/batch/dashboard_data, `reports/evidence/backend/`, `requirements/backend.txt` |
| Frontend | `frontend/`, `docs/frontend/`, `tests/frontend/`, `reports/evidence/frontend/` |

## Quy tắc phối hợp

- Data sở hữu loader/chuẩn hóa/bảng nhãn; các phần khác dùng giao diện leader chốt. Cần sửa thì yêu cầu Data thực hiện.
- Sentiment và Topic có code huấn luyện, đánh giá, suy luận, metadata, tests và báo cáo riêng; không tạo file training/evaluation chung để hai người cùng sửa.
- Mỗi người khai báo dependencies trong file riêng. Leader thống nhất phiên bản và tổng hợp vào requirements/config gốc.
- Backend sở hữu JSON/lỗi khi thực thi theo đặc tả; Frontend không tự sửa API, Backend không sửa UI.
- Mỗi người viết phần báo cáo trong `docs/<vai-tro>/report.md`; leader tổng hợp vào báo cáo cuối.
- File P1 đã được dành chỗ nhưng chỉ triển khai khi leader cho phép. Dataset/model/metrics thật được sinh sau, không tạo artifact giả hoặc JSON metrics trống để làm bằng chứng.
- File mới ngoài phạm vi cần leader xác định chủ sở hữu trước khi thêm. Các file khung đã tạo và chủ sở hữu được kiểm tra bằng manifest, không bằng quyền GitHub riêng cho từng thư mục.

Xem [phân công và mốc bàn giao](team-assignments.md), [hướng dẫn bắt đầu](team-start.md).
