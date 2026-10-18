# Công việc để Leader phân công

Đây là đề xuất theo README, chưa gán tên sinh viên hoặc tạo GitHub Issues.
Leader điền người phụ trách và ngày bắt đầu thực tế.

| Vai trò | Nhánh dự kiến | Việc tiếp tục | Nghiệm thu |
|---|---|---|---|
| TV1 Leader | Nhánh riêng khi code | Review hợp đồng, tích hợp, theo dõi mốc, báo cáo | Demo và bộ minh chứng chạy lại được |
| TV2 Data & EDA | feature/data-preprocessing | Nguồn/quyền dữ liệu, kiểm chứng mapping, giữ split, hoàn thiện preprocess + notebook 01/02 | CSV train/validation/test ba cột; số lượng/lỗi/EDA có nguồn |
| TV3 Sentiment | feature/sentiment-model | Hoàn thiện train_sentiment, notebook 03; NB/LR/LinearSVC; chọn bằng validation | Pipeline thật + báo cáo test + cấu hình/phiên bản |
| TV4 Topic | feature/topic-model | Hoàn thiện train_topic, notebook 04; NB/LR/LinearSVC; phối hợp evaluate | Pipeline thật + báo cáo test + confusion matrix |
| TV5 Backend | feature/backend-api | Tích hợp hai pipeline thực, kiểm thử nhãn/hiệu năng/lỗi, hoàn thiện validation | API trả hai nhãn thực, không có đường chạy giả |
| TV6 Frontend | feature/frontend-dashboard | Kiểm thử browser, hoàn thiện biểu đồ/bảng so sánh, UX và export | Bốn tab, CSV/Dashboard từ kết quả API thật |

## Mốc 21 ngày

- Ngày 1–3: Leader duyệt khung/API; TV2 chốt dữ liệu/mapping; TV5/TV6 chạy khung.
- Ngày 4–7: dữ liệu chuẩn và baseline sentiment thật; kiểm thử kết nối ban đầu.
- Ngày 8–11: TV3/TV4 so sánh ba thuật toán cho từng task bằng validation.
- Ngày 12–14: chốt model, đánh giá test; TV5/TV6 tích hợp hai pipeline thật.
- Ngày 15–18: CSV, Dashboard, báo cáo ML và kiểm thử toàn luồng.
- Ngày 19–21: sửa lỗi, chốt tài liệu/slide, diễn tập offline và hỏi đáp.

## Điểm giao tiếp bắt buộc

1. TV2 → TV3/TV4: dữ liệu có nguồn và giấy phép, split, label mapping đã xác minh.
2. TV3/TV4 → TV5: hai pipeline tin cậy, phiên bản thư viện, preprocessing,
   báo cáo theo API_CONTRACT và cách tái lập từ dữ liệu thật.
3. TV5 → TV6: giữ hợp đồng hoặc cùng cập nhật trước khi đổi response.
4. Leader review PR trước merge. Thành viên chỉ sửa phạm vi được giao;
   `ml/evaluate.py`, `ml/labels.py` và requirements cần phối hợp khi sửa chung.

Ưu tiên P0: hai model thật, phân tích đơn câu, báo cáo ML. CSV/Dashboard là P1;
cloud/Deep Learning/UI nâng cao chỉ làm khi P0 ổn định.
