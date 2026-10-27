# Kiểm thử — file hiện còn trống

Đã dành chỗ cho tests Data/chuẩn hóa/nhãn, Sentiment, Topic, Backend, Frontend và tích hợp. Người viết code sở hữu tests phần đó; leader sở hữu `integration/test_prediction_flow.py` và cấu hình chung.

File test trống không chứa bài kiểm tra, nên chưa có kết quả pass/fail của chức năng. Khi triển khai, viết test theo hợp đồng đã chốt rồi chạy kiểm chứng. Fixture/test double chỉ dùng trong tests; không thay mô hình thật trong nghiệm thu.

- Data: `test_data.py`, `test_preprocessing.py`, `test_labels.py`.
- Sentiment: `test_sentiment_training.py`, `test_sentiment_artifacts.py`.
- Topic: `test_topic_training.py`, `test_topic_artifacts.py`.
- Backend: `test_health.py`, `test_model_service.py`, `test_predict.py`; P1 có `test_batch.py`, `test_dashboard_data.py`.
- Frontend: `frontend/test_ui.py`, leader chốt công cụ trước khi thực hiện.
- Leader: `integration/test_prediction_flow.py`, cần artifact thật để nghiệm thu toàn luồng.

Không coi pytest báo không thu thập bài nào hoặc skip do thiếu artifact là đã đạt. Ghi lệnh và kết quả thực tế trong PR/tài liệu vai trò.
