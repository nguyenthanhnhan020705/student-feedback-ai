# Artifact mô hình

Hiện chưa có model hoặc metadata thật. Hai người làm mô hình sinh ra các file sau khi huấn luyện và kiểm tra tải lại:

- Sentiment: `sentiment_pipeline.joblib`, `sentiment_metadata.json`.
- Topic: `topic_pipeline.joblib`, `topic_metadata.json`.

Không tạo `.joblib` rỗng hoặc metadata giả. Kiểm tra quyền phân phối và kích thước trước khi đưa artifact lên GitHub; `.joblib`/`.pkl` được ignore mặc định. Nếu không phân phối qua Git, ghi cách nhận đúng phiên bản artifact trong tài liệu bàn giao. Backend tải đúng hai artifact được leader duyệt theo [hợp đồng](../docs/specs/data-contract.md).
