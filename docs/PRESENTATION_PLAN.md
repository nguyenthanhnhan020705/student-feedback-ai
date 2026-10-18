# Kế hoạch bảo vệ: 25 phút + 10 phút hỏi đáp

| Phút | Thành viên | Nội dung và minh chứng cần chuẩn bị |
|---|---|---|
| 0–3 | TV1 | Bài toán, giới hạn 1 sentiment + 1 topic, sơ đồ kiến trúc |
| 3–7 | TV2 | Nguồn UIT-VSFC, mapping đã xác minh, EDA và split độc lập |
| 7–12 | TV3 | TF-IDF, NB/LR/LinearSVC cho sentiment, chọn theo validation |
| 12–16 | TV4 | Ba thuật toán topic, test report và confusion matrix thật |
| 16–22 | TV5 + TV6 | Một câu mới → CSV → Dashboard; minh họa lỗi đầu vào |
| 22–25 | TV1 | Kết quả thực nghiệm, giới hạn, hướng mở rộng |
| 25–35 | Cả nhóm | Hỏi đáp theo phạm vi phụ trách |

Chuẩn bị notebook/script chạy lại được, dữ liệu được phép dùng, hai pipeline,
requirements/phiên bản, báo cáo test, slide và demo offline. Khi chưa có model,
chỉ trình bày trạng thái bộ khung; không dùng output của mock test làm demo AI.

Câu hỏi diễn tập: tránh data leakage thế nào? Vì sao Macro F1? Chọn model trên
validation hay test? Vì sao SVM không có confidence? Câu nhiều khía cạnh được
xử lý ra sao? Mô hình và preprocessing lúc train/predict có khớp nhau không?

Chưa tạo báo cáo Word/PDF, slide PPT hoặc số liệu nghiên cứu trong Giai đoạn A.
