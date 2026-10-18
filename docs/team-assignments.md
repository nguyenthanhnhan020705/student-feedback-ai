# Phân công leader và 5 thành viên

**Trạng thái:** Phân công theo vai trò; leader điền tên và tài khoản thực tế khi giao việc.  
**Tài liệu chung:** [BRD](../README.md), [roadmap](roadmap/README.md), [quy trình GitHub](../CONTRIBUTING.md).

## 1. Phân công chính

| Thành viên | Phần việc | Phase chính | Kết quả bắt buộc | Tiêu chí leader kiểm tra |
| --- | --- | --- | --- | --- |
| TV1 — Bạn, leader | Chốt phạm vi, hợp đồng, giao Issue, review, tích hợp, tổng hợp báo cáo/slide | 0, 4, 6; theo dõi toàn bộ | Đặc tả thống nhất, bảng tiến độ, biên bản kiểm tra và bản bàn giao | AC-01–AC-08 theo phạm vi; minh chứng từng người |
| TV2 — Data | Nguồn UIT-VSFC, loader, kiểm tra nhãn/split, EDA, chuẩn hóa văn bản | 2; tham gia 0, 3, 6 | Nguồn/quyền sử dụng, bảng mã, notebook EDA, hàm xử lý và tests | AC-01; số dòng/nhãn đúng; phát hiện rỗng/trùng; giữ phủ định |
| TV3 — Sentiment | So sánh NB/LR/SVM cho cảm xúc, chọn bằng validation | 3; tham gia 0, 4, 6 | Sentiment pipeline, metrics, Confusion Matrix, phân tích lỗi, hướng dẫn tái lập | AC-02; fit trên train; pipeline tải lại cho kết quả nhất quán |
| TV4 — Topic | So sánh NB/LR/SVM cho chủ đề, chọn bằng validation | 3; tham gia 0, 4, 6 | Topic pipeline, metrics, Confusion Matrix, phân tích lỗi, hướng dẫn tái lập | AC-02; cùng split so sánh; bảng mã đúng và kết quả thật |
| TV5 — Backend | Khung FastAPI, health, nạp mô hình, predict, tests và batch nếu kịp | 1, 4; 5 tùy chọn | API theo hợp đồng, kiểm thử đầu vào/lỗi/model, tài liệu chạy | AC-04/07, phần API của AC-03; AC-05 nếu triển khai |
| TV6 — Frontend | Form nhập câu, trạng thái chờ/lỗi, hiển thị nhãn, kết nối API; CSV/Dashboard nếu kịp | 1, 4; 5 tùy chọn | Website hoạt động với API thật, ảnh demo và hướng dẫn chạy | AC-03; lỗi rõ ràng; AC-06 nếu triển khai |

Mỗi người viết phần báo cáo và cung cấp minh chứng cho phần việc của mình. Leader tổng hợp và kiểm tra tính thống nhất, không phải tự viết lại toàn bộ báo cáo thay nhóm.

## 2. Đợt giao việc đầu tiên

Trước khi viết code, cả nhóm đọc Phase 0 và cùng chốt giao diện dữ liệu/API. Leader có thể tạo các Issue sau trên GitHub; danh sách này chưa được tự động đăng hoặc gửi cho thành viên.

| Mã giao việc | Người nhận | Đầu việc khởi đầu | Sản phẩm đưa vào PR | Điều kiện trước khi làm |
| --- | --- | --- | --- | --- |
| TEAM-01 | TV2 | Xác minh nguồn, quyền sử dụng, split và bảng mã UIT-VSFC | `docs/data/dataset.md`, đề xuất hợp đồng dữ liệu | Có thể khảo sát ngay, chưa huấn luyện khi nguồn chưa rõ |
| TEAM-02 | TV3 | Lập thiết kế thí nghiệm sentiment: 3 thuật toán, metrics, cấu hình và artifact | Phần sentiment của đặc tả/thí nghiệm; kế hoạch kiểm thử tải lại | Dùng nhãn dự kiến có ghi chú; chờ TV2 xác minh trước training |
| TEAM-03 | TV4 | Lập thiết kế thí nghiệm topic và thống nhất khung dùng chung với TV3 | Phần topic; đề xuất trách nhiệm module chung | Chốt cách chia file với TV3 trước khi cùng sửa module |
| TEAM-04 | TV5 | Đề xuất API health/predict, lỗi, cách tải artifact và môi trường | `docs/specs/api-contract.md`, sau khi chốt mới triển khai Phase 1 | Hợp đồng được leader và TV3/TV4/TV6 rà soát |
| TEAM-05 | TV6 | Đề xuất luồng nhập câu, chờ, lỗi, kết quả và kết nối backend | Mô tả UI trong đặc tả; khung frontend sau khi chốt | Phối hợp TV5 về request/response và cách phục vụ UI |

Leader gắn người nhận, hạn thực tế, phase, mã BRD và điều kiện nghiệm thu vào từng Issue. Mốc ngày 1–21 trong roadmap là dự kiến, không thay thế hạn giao việc đã thống nhất với thành viên.

## 3. Các điểm cần phối hợp

- TV2 bàn giao bảng mã và split cho TV3/TV4 trước huấn luyện; thay đổi tiền xử lý phải báo nhóm ML/backend.
- TV3/TV4 dùng chung giao diện nhưng mỗi người sở hữu pipeline riêng. Chỉ định một người thực hiện mỗi thay đổi ở `ml/training.py` hoặc `ml/evaluation.py`, người còn lại review; không cùng viết hai phiên bản cạnh tranh.
- TV3/TV4 bàn giao artifact + metadata + lệnh tải cho TV5; chỉ gửi notebook chưa đủ để tích hợp.
- TV5/TV6 làm theo cùng hợp đồng. Khi chưa có model, ứng dụng báo chưa sẵn sàng; dữ liệu mock phục vụ phát triển phải được nhận diện rõ.
- TV1 rà soát thay đổi ở dependencies, cấu hình, hợp đồng chung và phạm vi; không tự động tăng P1 thành bắt buộc.
- Phase 5 chỉ bắt đầu sau khi Phase 4 ổn định; mọi thành viên tiếp tục bổ sung báo cáo và minh chứng cho Phase 6.

## 4. Nội dung có thể gửi cho nhóm

> Mỗi bạn đọc README BRD, roadmap và CONTRIBUTING trước khi làm. Nhận Issue đúng vai trò, cập nhật tiến độ mỗi ngày và báo sớm khi bị chặn. Tạo nhánh mới từ develop, chỉ push nhánh của mình, mở PR vào develop và yêu cầu leader review. PR phải có mô tả, hướng dẫn chạy, kết quả kiểm tra và minh chứng phần việc. Không push trực tiếp main/develop, không tự merge, không sửa hợp đồng chung khi chưa thống nhất. Mỗi bạn nộp cả code, tài liệu và phần báo cáo tương ứng; hoàn thành được ghi nhận sau khi PR đã được duyệt và merge.
