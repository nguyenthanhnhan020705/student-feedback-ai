# Phase 6 — Nghiệm thu và bàn giao

**Trạng thái:** Chưa bắt đầu.  
**Thời gian:** Ngày 15–21; thu thập nội dung báo cáo từ Phase 2.  
**Phụ trách:** TV1 tổng hợp; TV2–TV6 cung cấp minh chứng phần việc.  
**Phụ thuộc:** Phase 4 đạt; bổ sung Phase 5 nếu triển khai.  
**Quay lại:** [Lộ trình](README.md).

Mỗi người viết phần báo cáo riêng ở `docs/<vai-tro>/report.md`, leader là người duy nhất ghép báo cáo/slide tổng hợp. Đã có [bảng nghiệm thu](../acceptance.md); hiện chưa có tiêu chí sản phẩm nào được nghiệm thu từ khung trống.

## Mục tiêu

Bàn giao sản phẩm chạy được, có thể tái lập và có báo cáo phản ánh kết quả thật. Kiểm tra lại AC-01–AC-08 theo phạm vi đã triển khai, hoàn tất NFR-02/04/05 và BO-04.

## Công việc

- [ ] P6.1: Chạy bộ kiểm thử P0 và P1 nếu có; lập danh sách lỗi, sửa lỗi chặn demo và chạy lại kiểm tra liên quan.
- [ ] P6.2: Cài đặt từ môi trường mới theo hướng dẫn; xác minh lấy dữ liệu/artifact đúng quyền, tải model, chạy API/UI và tái hiện thí nghiệm theo cấu hình đã lưu.
- [ ] P6.3: Hoàn thiện ma trận AC → minh chứng → kết quả; phân biệt đạt, chưa đạt và không áp dụng cho P1 bị bỏ qua.
- [ ] P6.4: Cập nhật README và hướng dẫn theo cấu trúc/lệnh thực tế; ghi phiên bản môi trường, giới hạn, lỗi còn tồn tại và cách tái lập.
- [ ] P6.5: Tổng hợp báo cáo theo 6 phần học thuật trong BRD, tối đa 80 trang theo yêu cầu hiện có; sử dụng metrics và hình chạy thật.
- [ ] P6.6: Hoàn thiện slide, kịch bản demo và bảng đóng góp thực tế; xác nhận lịch thuyết trình và yêu cầu nộp bài mới nhất với đầu mối học phần.
- [ ] P6.7: Rà soát thông tin riêng tư, bí mật và quyền phân phối dữ liệu/model trong gói bàn giao; kiểm tra mở được báo cáo và slide.
- [ ] P6.8: Diễn tập từ khởi động hệ thống đến dự đoán câu mới; demo CSV/Dashboard nếu đã đạt; ghi nhận kết quả cuối.

## Sản phẩm dự kiến

| File | Nội dung |
| --- | --- |
| `docs/acceptance.md` | Ma trận nghiệm thu và liên kết minh chứng |
| `docs/development.md`, `README.md` | Hướng dẫn chạy và trạng thái thực tế |
| `reports/final-report.docx` hoặc `reports/final-report.pdf` | Báo cáo cuối kỳ |
| `reports/presentation.pptx` | Slide thuyết trình |
| `reports/demo-script.md`, `reports/contributions.md` | Kịch bản và đóng góp thực tế |
| `reports/evidence/phase-6/` | Log kiểm thử, tái lập và diễn tập |

## Điều kiện hoàn thành và kiểm chứng

- Lệnh dự kiến `python -m pytest -q` chạy đạt; những bài cần dataset/artifact thật phải chạy đủ cho nghiệm thu, không coi bị bỏ qua là đã đạt.
- Hướng dẫn cài đặt/khởi động được thực hiện thành công từ môi trường mới và có log.
- Từng AC bắt buộc có bằng chứng truy cập được; AC-05/06 chỉ ghi không áp dụng nếu Phase 5 đã được bỏ khỏi phạm vi.
- Không còn lỗi chặn demo; mọi hạn chế còn lại được mô tả trong báo cáo.
- Báo cáo, slide, code và mô hình thống nhất với cùng phiên bản bàn giao; lịch sử đóng góp phản ánh công việc thực tế.

Việc nộp lên Classroom hoặc gửi cho giảng viên được thực hiện theo hướng dẫn của người phụ trách; checklist này không tự động gửi tài liệu ra ngoài.
