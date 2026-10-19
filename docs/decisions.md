# Nhật ký quyết định Phase 0

**Bộ đặc tả:** v1.0, soạn 2026-10-19. **Trạng thái:** Đã đề xuất đầy đủ quyết định kỹ thuật; chờ leader duyệt bằng văn bản. Không tự ghi ngày phê duyệt hoặc M0 hoàn thành thay leader.

| Mã | Quyết định v1.0 đề xuất | Lý do / người thực hiện |
| --- | --- | --- |
| D-01 | Giữ P0 như BRD; CSV/Dashboard là P1 chưa giao triển khai | Bảo vệ phạm vi học phần/21 ngày; leader |
| D-02 | Một server FastAPI phục vụ API và frontend cùng origin | Ít cấu hình/CORS khi demo; Backend phục vụ, Frontend gọi URL tương đối |
| D-03 | CPython 3.13.x 64-bit, scikit-learn 1.6.1; một bộ lock chung ở Phase 1 | Máy hiện tại 3.13.3 64-bit; leader khóa deps trước train |
| D-04 | DataFrame id/text/sentiment/topic/split, canonical labels chuỗi | Hai mô hình và API không tự giải mã số nguồn; Data |
| D-05 | NFC + lower + thu gọn whitespace, chỉ nằm trong preprocessor pipeline | Tránh lệch hoặc lặp xử lý; Data viết, ML sử dụng |
| D-06 | TF-IDF bigram, NB/LR/SVM tham số cụ thể; không grid search baseline | So sánh đủ yêu cầu, giữ thời gian; Sentiment và Topic |
| D-07 | Chọn validation Macro F1; tie Accuracy rồi thứ tự model cố định | Không dùng test để chọn/tối ưu; hai người ML |
| D-08 | Giữ split nguồn, báo trùng; dữ liệu lỗi không âm thầm drop/remap | Tái lập và công bố giới hạn; Data + leader |
| D-09 | Pipeline + metadata riêng, checksum/version/classes được kiểm tra | Bàn giao M2 minh bạch; ML xuất, Backend kiểm tra |
| D-10 | Input raw tối đa 5000 code point, không blank; 422/503/500 cùng envelope | UI/API có cùng tiêu chí; Backend/Frontend |
| D-11 | UI một request/lần, timeout 10000 ms, không confidence giả | Dễ kiểm tra hành vi; Frontend |
| D-12 | P1 dự phòng: 2 MiB/1000 record UTF-8 CSV, lỗi dòng có kết quả, summary tính dòng thành công | Tránh hai phần tự chọn khác schema; chỉ làm khi leader cho phép |
| D-13 | Năm vai trò code/tests song song sau M0; chỉ chờ tại M1/M2/M3 thực tế | Giữ quyền sở hữu file riêng và tận dụng song song |
| D-14 | Không đặt ngưỡng Accuracy/F1 hoặc SLA khi nguồn chưa quy định | Nghiệm thu phương pháp/kết quả thật, không tự gán điểm đạt |

## Những vấn đề nguồn chưa thể xác nhận bằng đặc tả

| Nội dung BRD | Cách xử lý và thời điểm | Có chặn chuẩn bị code/tests? |
| --- | --- | --- |
| TBD-01 — tên người, ngày bắt đầu/hạn nộp | Leader điền trước khi gán Issue/đưa ra deadline thực tế | Không chặn chuẩn bị; phải có khi giao người cụ thể |
| TBD-02 — dataset, quyền dùng, checksum, số dòng/mã thực tế | Data xác minh trước M1 và training thật; dataset card hiện license unknown | Không chặn fixture/tests; có chặn M1/training nếu chưa xác minh |
| TBD-03 — API/labels/batch/error | Đã định nghĩa cụ thể tại API và Data contract v1.0, chờ duyệt bộ này | Sau duyệt không còn chặn giao diện |
| TBD-04 — CSV/Dashboard cam kết hay không | Giữ P1, chưa triển khai; leader quyết định riêng sau P0 ổn định | Không chặn P0 |
| TBD-05 — giới hạn input/hiệu năng/ML | Chốt 5000 code point, P1 2 MiB/1000 record; không thêm SLA hoặc ngưỡng ML | Không chặn schema P0 |
| TBD-06 — Python/deps/entrypoint/frontend | Quyết định cụ thể ở environment.md; Phase 1 kiểm chứng lock/import/startup | Không chặn viết đặc tả; train cần lock chung đạt |
| TBD-07 — người dùng/demo mới | Người dùng demo là nhóm/giảng viên; tự nhập câu mới không chứa dữ liệu riêng tư | Không chặn P0 |
| TBD-08 — lịch thuyết trình/Classroom | Leader xác nhận trước Phase 6; không tự đặt lịch | Không chặn phát triển |

## Phê duyệt và thay đổi

Ngày duyệt chưa được ghi. Leader đọc [bộ đặc tả](specs/README.md), xác nhận hoặc sửa quyết định; sau đó mới ghi phiên bản/ngày duyệt và đánh dấu M0. Không triển khai hoặc tự đổi hợp đồng khác v1.0 trước bước đó.

Nếu thay field/nhãn/giao diện artifact hoặc Python/ML lock sau M0, leader ghi quyết định v1.x, liệt kê phần chịu ảnh hưởng và yêu cầu các bên cập nhật tests trước khi merge. Người soạn code và người duyệt PR theo quy tắc GitHub hiện có, không tự tắt bảo vệ để hợp nhất.
