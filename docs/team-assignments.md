# Phân công theo chức năng — một người phụ trách một phần

**Cập nhật 2026-10-19:** Leader tự chốt Phase 0; mỗi thành viên phụ trách trọn một chức năng và sửa các file thuộc phạm vi của mình. Leader điền tên/tài khoản thực tế khi giao việc.  
**Tài liệu chung:** [BRD](../README.md), [roadmap](roadmap/README.md), [quy trình GitHub](../CONTRIBUTING.md).

## Nhánh và phạm vi độc lập

| Thành viên | Nhánh riêng | Công việc trọn phần |
| --- | --- | --- |
| TV2 | `feature/data-preprocessing` | Toàn bộ Data: nguồn, EDA, loader, chuẩn hóa, bảng nhãn và kiểm thử Data |
| TV3 | `feature/sentiment-model` | Toàn bộ Sentiment: huấn luyện, đánh giá, artifact, tests và báo cáo cảm xúc |
| TV4 | `feature/topic-model` | Toàn bộ Topic: huấn luyện, đánh giá, artifact, tests và báo cáo chủ đề |
| TV5 | `feature/backend-api` | Toàn bộ Backend: API, model service, lỗi, kiểm thử API, batch nếu có P1 |
| TV6 | `feature/frontend-dashboard` | Toàn bộ Frontend: giao diện, gọi API, kiểm tra UI, CSV/Dashboard nếu có P1 |

Xem [quyền sở hữu file và bàn giao](function-ownership.md), [hướng dẫn bắt đầu](team-start.md) và [checklist leader chốt Phase 0](phase-0-leader-checklist.md). Các nhánh có cùng nền `develop` và cùng commit hướng dẫn này; hướng dẫn được đưa vào `develop` qua PR được leader duyệt.

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

Trước khi viết code, leader tự chốt đặc tả Phase 0 và giao mỗi chức năng cho một người. Thành viên có thể góp ý hoặc cung cấp dữ kiện, leader là người duy nhất sửa bộ đặc tả chung. Leader có thể tạo các Issue sau; danh sách này chưa được tự động đăng hoặc gửi cho thành viên.

| Mã giao việc | Người nhận | Đầu việc khởi đầu | Sản phẩm đưa vào PR | Điều kiện trước khi làm |
| --- | --- | --- | --- | --- |
| TEAM-01 | TV2 | Xác minh nguồn, quyền sử dụng, split và bảng mã UIT-VSFC | `docs/data/dataset.md`, đề xuất hợp đồng dữ liệu | Có thể khảo sát ngay, chưa huấn luyện khi nguồn chưa rõ |
| TEAM-02 | TV3 | Chuẩn bị thí nghiệm sentiment: 3 thuật toán, metrics và artifact theo hợp đồng leader chốt | Tài liệu sentiment riêng và kế hoạch kiểm thử tải lại | Chờ Data được duyệt trước training thực tế |
| TEAM-03 | TV4 | Chuẩn bị thí nghiệm topic với code/tests/metadata riêng | Tài liệu topic riêng và kế hoạch kiểm thử tải lại | Chờ Data được duyệt trước training thực tế; không sửa module Sentiment |
| TEAM-04 | TV5 | Xây khung health/predict và model service theo hợp đồng leader chốt | `backend/`, tests API và `docs/backend/` | Leader chốt API/môi trường trước; tích hợp thật khi có hai artifact |
| TEAM-05 | TV6 | Xây giao diện theo luồng UI và JSON leader chốt | `frontend/`, kiểm tra UI và `docs/frontend/` | Khung UI có thể làm theo hợp đồng; nghiệm thu cần API thật |

Leader gắn người nhận, hạn thực tế, phase, mã BRD và điều kiện nghiệm thu vào từng Issue. Mốc ngày 1–21 trong roadmap là dự kiến, không thay thế hạn giao việc đã thống nhất với thành viên.

## 3. Các điểm cần phối hợp

- TV2 bàn giao bảng mã và split cho TV3/TV4 trước huấn luyện; thay đổi tiền xử lý phải báo nhóm ML/backend.
- TV3/TV4 có code huấn luyện, đánh giá, suy luận, metadata và tests riêng theo bảng quyền sở hữu. Không dùng chung `ml/training.py`, `ml/evaluation.py` hoặc `models/metadata.json`.
- TV3/TV4 bàn giao artifact + metadata + lệnh tải cho TV5; chỉ gửi notebook chưa đủ để tích hợp.
- TV5/TV6 làm theo cùng hợp đồng. Khi chưa có model, ứng dụng báo chưa sẵn sàng; dữ liệu mock phục vụ phát triển phải được nhận diện rõ.
- TV1 là chủ sở hữu duy nhất của dependencies/cấu hình gốc, hợp đồng chung và tài liệu quản trị. Mỗi thành viên đề xuất dependencies trong file riêng; leader tổng hợp. Không tự động tăng P1 thành bắt buộc.
- Phase 5 chỉ bắt đầu sau khi Phase 4 ổn định; mọi thành viên tiếp tục bổ sung báo cáo và minh chứng cho Phase 6.

## 4. Nội dung có thể gửi cho nhóm

> Mỗi bạn đọc README BRD, roadmap và CONTRIBUTING trước khi làm. Nhận Issue đúng vai trò, cập nhật tiến độ mỗi ngày và báo sớm khi bị chặn. Tạo nhánh mới từ develop, chỉ push nhánh của mình, mở PR vào develop và yêu cầu leader review. PR phải có mô tả, hướng dẫn chạy, kết quả kiểm tra và minh chứng phần việc. Không push trực tiếp main/develop, không tự merge, không sửa hợp đồng chung khi chưa thống nhất. Mỗi bạn nộp cả code, tài liệu và phần báo cáo tương ứng; hoàn thành được ghi nhận sau khi PR đã được duyệt và merge.
