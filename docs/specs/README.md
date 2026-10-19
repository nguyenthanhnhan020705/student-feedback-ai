# Phase 0 — Bộ đặc tả v1.0 đề xuất duyệt

**Ngày soạn:** 2026-10-19. **Người phê duyệt:** leader `@nguyenthanhnhan020705`.  
**Trạng thái:** Đã soạn đủ quyết định kỹ thuật và tự rà soát; chờ leader duyệt phiên bản bằng văn bản. Chưa công bố M0 đã được phê duyệt, chưa triển khai code ứng dụng.

## Tài liệu có hiệu lực cùng phiên bản

| Tài liệu | Quyết định chính |
| --- | --- |
| [MVP](mvp.md) | P0/P1, kiến trúc, UI, kiểm thử và nghiệm thu |
| [API](api-contract.md) | JSON, giới hạn, nhãn, HTTP status và hành vi lỗi |
| [Data/model](data-contract.md) | Loader/chuẩn hóa, split, nhãn, pipeline, metrics và metadata |
| [Môi trường](environment.md) | Python, giới hạn dependencies, đường dẫn và lệnh mục tiêu |
| [Quyết định](../decisions.md) | Các lựa chọn v1.0 và việc được chuyển cho Phase 1–2 |

Đọc MVP trước, sau đó đọc API/Data theo vai trò. Trong trường hợp bảng tóm tắt ở roadmap/README ngắn hơn, hợp đồng kỹ thuật v1.0 trong bộ này là nguồn chi tiết để triển khai sau khi leader duyệt. Thay đổi giao diện phải được leader nâng phiên bản và thông báo cả phần cung cấp lẫn phần sử dụng.

## Tóm tắt để leader duyệt

- P0: phản hồi tiếng Việt → một nhãn sentiment + một nhãn topic bằng TF-IDF và mô hình thật; đủ EDA, so sánh ba thuật toán/nhiệm vụ, kiểm thử và báo cáo.
- P1: CSV/export/Dashboard vẫn tùy chọn, chưa giao triển khai; giới hạn và hợp đồng dự phòng đã được định nghĩa để tránh tự đặt khác nhau.
- FastAPI phục vụ API và frontend cùng origin `http://127.0.0.1:8000`; HTML/CSS/JavaScript thuần.
- Runtime CPython 3.13.x 64-bit; leader khóa bộ dependencies thực tế tại Phase 1 trước khi huấn luyện/bàn giao artifact.
- Input một câu: chuỗi không chỉ có khoảng trắng, tối đa 5000 Unicode code point; HTTP 422/503/500 có error envelope thống nhất.
- Data và hai mô hình dùng nhãn chuỗi chuẩn; mã nguồn UIT-VSFC được ánh xạ một lần tại loader.
- Năm người bắt đầu code/tests độc lập sau M0; huấn luyện thật chỉ cần M1, không chờ EDA/báo cáo Data hoàn tất.

## Phân biệt quyết định và kiểm chứng thực tế

Các giới hạn 5000 ký tự, 2 MiB/1000 dòng CSV và timeout UI 10 giây là lựa chọn thiết kế cho demo, không phải số đo hiệu năng. Python 3.13.3 64-bit đã được đọc trên máy hiện tại; ứng dụng/dependencies/dataset/model chưa được cài hoặc chạy để nghiệm thu. Quyền dùng dữ liệu và bộ lock môi trường phải có bằng chứng ở các mốc được chỉ định.

Leader duyệt bộ đặc tả rồi ghi ngày/phiên bản vào nhật ký quyết định; khi đó mới chuyển M0 sang Đã chốt và giao nhóm triển khai. Các file code/tests của thành viên tiếp tục được giữ trống trong Phase 0 này.
