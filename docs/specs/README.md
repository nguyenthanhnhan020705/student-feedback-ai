# Phase 0 — Bộ đặc tả v1.0 đã duyệt

**Ngày soạn:** 2026-10-19. **Người phê duyệt:** leader `@nguyenthanhnhan020705`.  
**Trạng thái:** Leader đã chốt v1.0 ngày 2026-10-19 bằng xác nhận trong hội thoại. M0 hoàn thành về đặc tả; các thành viên có thể bắt đầu theo hợp đồng chung. Code ứng dụng chưa được triển khai/nghiệm thu.

## Tài liệu có hiệu lực cùng phiên bản

| Tài liệu | Quyết định chính |
| --- | --- |
| [MVP](mvp.md) | P0/P1, kiến trúc, UI, kiểm thử và nghiệm thu |
| [API](api-contract.md) | JSON, giới hạn, nhãn, HTTP status và hành vi lỗi |
| [Data/model](data-contract.md) | Loader/chuẩn hóa, split, nhãn, pipeline, metrics và metadata |
| [Môi trường](environment.md) | Python, giới hạn dependencies, đường dẫn và lệnh mục tiêu |
| [Quyết định](../decisions.md) | Các lựa chọn v1.0 và việc được chuyển cho Phase 1–2 |

Đọc MVP trước, sau đó đọc API/Data theo vai trò. Trong trường hợp bảng tóm tắt ở roadmap/README ngắn hơn, hợp đồng kỹ thuật v1.0 trong bộ này là nguồn chi tiết để triển khai sau khi leader duyệt. Thay đổi giao diện phải được leader nâng phiên bản và thông báo cả phần cung cấp lẫn phần sử dụng.

## Quyết định v1.0 có hiệu lực

- P0: phản hồi tiếng Việt → một nhãn sentiment + một nhãn topic bằng TF-IDF và mô hình thật; đủ EDA, so sánh ba thuật toán/nhiệm vụ, kiểm thử và báo cáo.
- P1: CSV/export/Dashboard vẫn tùy chọn, chưa giao triển khai; giới hạn và hợp đồng dự phòng đã được định nghĩa để tránh tự đặt khác nhau.
- FastAPI phục vụ API và frontend cùng origin `http://127.0.0.1:8000`; HTML/CSS/JavaScript thuần.
- Runtime CPython 3.13.x 64-bit; leader khóa bộ dependencies thực tế tại Phase 1 trước khi huấn luyện/bàn giao artifact.
- Input một câu: chuỗi không chỉ có khoảng trắng, tối đa 5000 Unicode code point; HTTP 422/503/500 có error envelope thống nhất.
- Data và hai mô hình dùng nhãn chuỗi chuẩn; mã nguồn UIT-VSFC được ánh xạ một lần tại loader.
- Năm người bắt đầu code/tests độc lập sau M0; huấn luyện thật chỉ cần M1, không chờ EDA/báo cáo Data hoàn tất.

## Phân biệt quyết định và kiểm chứng thực tế

Các giới hạn 5000 ký tự, 2 MiB/1000 dòng CSV và timeout UI 10 giây là lựa chọn thiết kế cho demo, không phải số đo hiệu năng. Python 3.13.3 64-bit đã được đọc trên máy hiện tại; ứng dụng/dependencies/dataset/model chưa được cài hoặc chạy để nghiệm thu. Quyền dùng dữ liệu và bộ lock môi trường phải có bằng chứng ở các mốc được chỉ định.

Leader đã duyệt; xem [nhật ký quyết định](../decisions.md) và [trạng thái Phase 0](../roadmap/phase-0-specification.md). Năm nhánh chức năng dùng cùng bản đã duyệt. Code/tests vẫn trống để thành viên triển khai; M1 của Data và môi trường Phase 1 chưa được nghiệm thu. Phê duyệt nội dung trong hội thoại không thay thế approval PR trên GitHub khi hợp nhất vào develop/main.
