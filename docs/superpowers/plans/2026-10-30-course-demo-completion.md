# Kế hoạch hoàn thiện demo học phần — leader đã duyệt

Leader duyệt sáu phase trong hội thoại ngày 2026-10-30, yêu cầu bắt đầu Phase 1 và tự lấy dữ liệu/API cần thiết. Tiến độ: `course-demo-progress.md`.

> **For agentic workers:** Sau khi leader duyệt, dùng superpowers:executing-plans để triển khai từng phase; kiểm thử trước khi sửa hành vi, review độc lập trước bàn giao cuối.

**Goal:** Hoàn thiện sản phẩm AI P0 chạy local: câu phản hồi mới → API → hai model thật → hai nhãn trên web; có code, báo cáo Word, slide PowerPoint và bằng chứng demo tái lập.

**Architecture:** Kế thừa bản tích hợp trong `.local-tools/integration-p0`, nhánh `feature/integration-p0`. Giữ FastAPI phục vụ HTML/CSS/JavaScript cùng origin, Data dùng chung và hai pipeline TF-IDF + classifier độc lập. Bảo toàn bản gốc các thành viên; không khởi tạo lại dự án.

**Tech Stack:** CPython 3.13.x, scikit-learn 1.6.1, pandas/NumPy/SciPy/joblib, FastAPI, pytest, Playwright; python-docx/python-pptx cho tài liệu bàn giao.

**Spec:** `docs/specs/mvp.md`, `api-contract.md`, `data-contract.md`, `environment.md`; điều chỉnh mục tiêu do leader nêu ngày 2026-10-30 trong hội thoại.

## Phạm vi và quyết định cần duyệt

- Ưu tiên demo học phần local, không thêm yêu cầu production, cloud, tài khoản, database hoặc SLA.
- Dùng dataset UIT-VSFC và hai artifact hiện có; không thu thập lại dữ liệu hay train lại chỉ để làm đẹp kết quả.
- Theo chỉ đạo mới của leader, giấy phép chưa xác định không chặn thực hiện kỹ thuật demo local. Ghi trung thực `license unknown`; không coi chỉ đạo này là giấy phép của chủ dữ liệu. Việc công bố/phân phối dataset/model không thuộc kế hoạch.
- P0 gồm EDA, so sánh ba thuật toán mỗi task, API/web một câu, kiểm thử và báo cáo. CSV/export/Dashboard (P1) chỉ bổ sung nếu leader duyệt riêng.
- Giữ chủ sở hữu TV2 Data, TV3 Sentiment, TV4 Topic, TV5 Backend, TV6 Frontend. Trợ lý sửa bổ sung/tích hợp theo ủy quyền leader; ghi riêng phần hỗ trợ, không gán toàn bộ thay đổi cho thành viên.
- Hợp đồng vẫn 1.0: tối đa 5000 Unicode code point, timeout UI 10000 ms, hai nhãn chuỗi, 422/503/500 theo envelope chung.
- Không reset, force push, tự approve/merge hoặc push thẳng main/develop. Kế hoạch kết thúc bằng bản local review được và danh sách thay đổi để leader quyết định PR.

## Hướng tiếp cận

**Đề xuất:** Hoàn thiện P0 trên nền hiện có. Ưu điểm là bảo toàn thí nghiệm và đóng góp, tập trung sửa phần thiếu thực tế; hạn chế là giữ các giới hạn chất lượng của baseline.

**Chưa chọn:** Tối ưu lại model hoặc mở rộng P1 ngay. Các hướng này tăng công việc thí nghiệm/phạm vi và không cần thiết để đạt demo hai nhiệm vụ. Chỉ xem xét sau khi demo P0 ổn định và có yêu cầu riêng.

## Bằng chứng hiện có, không phải nghiệm thu cuối

- Core suite từng chạy 132 passed, 16 browser tests deselected, 12 warnings; sau đó đã thêm regression test thất bại nên không được gọi suite hiện tại là xanh.
- Browser lần đầu: 14 passed, 2 failed; đã có ảnh suy luận thật trên Chrome và Edge.
- Các lỗi đã tái hiện còn mở: chấp nhận nhãn `constructor`/`toString`; timeout chỉ bao fetch headers, không bao response body; JSON byte UTF-8 sai trả 400 ngoài hợp đồng thay vì 422.
- Reviewer còn yêu cầu đánh giá độ đầy đủ metrics metadata, chuỗi phiên bản Python, thứ tự nhãn. Không tự coi mọi đề xuất là lỗi trước khi đối chiếu hợp đồng.
- Đã có script `reports/build_delivery.py`; chưa xuất/kiểm chứng báo cáo Word và PowerPoint.

## Review Focus

1. Corpus/checksum/manifest và hai artifact phải cùng nguồn được ghi nhận — Phase 2.
2. Model thiếu/hỏng/metadata sai không làm server sập hoặc trả nhãn giả — Phase 3.
3. JSON/Unicode sai phải có lỗi đúng hợp đồng — Phase 3.
4. UI timeout cả response body, từ chối nhãn lạ, giữ input và phục hồi sau lỗi — Phase 4.
5. Cài mới, restart, chạy từ thư mục khác và demo không có mạng ngoài phải hoạt động — Phase 1 và 5.

## Phase 1 — Chốt bản tích hợp và môi trường

**Liên quan:** Leader và tất cả vai trò. **Files:** requirements*.txt, pytest.ini, .env.example, docs/development.md, reports/evidence/phase-6/source-inventory.json.

- [x] Kiểm tra Git/status và các bản local có thay đổi mới kể từ lần gom; chỉ đối chiếu, không chép đè mù quáng.
- [x] Ghi nguồn từng phần: nhánh/commit, thay đổi chưa commit, artifact hash và phạm vi đóng góp.
- [x] Kiểm các lock đã tạo khớp năm phiên bản ML trong metadata; ghi rõ runtime, test, browser và công cụ báo cáo.
- [x] Cài theo lock vào môi trường sạch, kiểm import và `python -m pip check`; không nâng gói ML ngoài lock.
- [x] Chuẩn hóa hướng dẫn một lệnh chạy server và đường dẫn model độc lập cwd; kiểm startup khi chưa có model.

**Đạt khi:** Cài sạch thành công, pip check không lỗi, API/UI khởi động được; baseline lỗi còn mở được liệt kê cụ thể. Không coi tests lỗi do đã biết là pass.

## Phase 2 — Xác minh Data và hai model (TV2–TV4)

**Files:** ml/data.py, preprocessing.py, labels.py, train/evaluate/predict_{sentiment,topic}.py; notebooks/01–03; reports/data, metrics, figures, models/*metadata.json; tests/test_data.py, test_labels.py, test_preprocessing.py, test_sentiment*.py, test_topic*.py.

- [x] Đối chiếu checksum dữ liệu thật, schema, nhãn và split 11426/1583/3166 với manifest; nếu khác thì điều tra, không sửa số liệu để khớp.
- [x] Chạy tests TV2–TV4 với `TV2_RUN_REAL_DATA=1`, không skip các bài nghiệm thu cần dữ liệu thật.
- [x] Đối chiếu cấu hình, selection, metrics và notebook output; kiểm pipeline fit train và chọn theo validation từ code/bằng chứng có sẵn.
- [x] Tải lại hai artifact trong tiến trình mới, kiểm runtime/checksum/nhãn và so với các câu đối chiếu đã lưu.
- [x] Bổ sung regression test trước khi sửa lỗi thực sự; không huấn luyện lại nếu chỉ là lỗi nạp/tài liệu.
- [x] Cập nhật báo cáo riêng: giới hạn neutral/other, mẫu trùng, chỉ số thật và trạng thái nguồn.

**Đạt khi:** Các tests Data/ML chạy đạt, hai artifact tải được và nhất quán với metrics/bằng chứng. Không đặt ngưỡng Accuracy/F1 mới; không gán là đúng mọi câu người dùng nhập. Nếu cần sửa thuật toán/đổi dữ liệu, báo ảnh hưởng và xin duyệt thay đổi thí nghiệm trước khi chạy lại.

## Phase 3 — Hoàn thiện Backend (TV5)

**Files:** backend/main.py, model_service.py, schemas.py, routes/health.py, routes/predict.py; tests/test_backend.py, test_health.py, test_model_service.py, test_predict.py, integration/test_prediction_flow.py.

- [x] Chạy lại `test_invalid_utf8_json_has_contract_error`: hiện trả 400; sửa để nhận 422 với INVALID_INPUT và `$body/invalid_json`, không làm đổi lỗi 404/405 thông thường.
- [x] Đối chiếu các phát hiện metadata với schema 1.0; viết test trường lồng thiếu/sai, sai kiểu, phiên bản không hợp lệ và nhãn theo yêu cầu trước khi sửa.
- [x] Chạy health/predict với hai artifact thật; so nhãn API và pipeline trực tiếp cho nhiều câu tự viết.
- [x] Kiểm thiếu/hỏng từng model, lỗi suy luận, kiểu input sai, blank, 5000/5001 code point, malformed JSON; không trả nhãn một phần.
- [x] Kiểm static assets, không lộ thư mục model, và đường dẫn khi đổi cwd.

**Đạt khi:** API chạy hai model thật, tests Backend/integration đạt và mỗi lỗi đúng envelope. Ghi log thực tế; warning thư viện được mô tả nếu không ảnh hưởng hành vi.

Kết quả 2026-10-30: 119 tests Backend/tích hợp đạt; HTTP thật và 59 hash được kiểm. Review không có Critical/Important; minor tên trường lỗi cho khóa JSON lone surrogate được hoãn và công khai tại `reports/evidence/phase-3/README.md`. Toàn suite 196 passed, 4 lỗi UI thuộc Phase 4; không tuyên bố mọi trường hợp biên đều đúng hợp đồng.

## Phase 4 — Hoàn thiện Frontend và trải nghiệm demo (TV6)

**Files:** frontend/api.js, app.js, index.html, styles.css; tests/frontend/test_ui.py; docs/frontend/{ui-notes,report}.md.

- [x] Chạy regression `test_rejects_prototype_names_as_prediction_labels`; sửa kiểm nhãn bằng own-property/allowlist, không nhận thuộc tính prototype thành nhãn hợp lệ.
- [x] Chạy `test_timeout_includes_response_body`; giữ timer đến khi đọc xong JSON, phân biệt AbortError với lỗi parse/server và luôn mở lại UI sau lỗi.
- [x] Kiểm blank/Unicode 5000–5001, loading, chống gửi trùng, lỗi 422/503/500, mất mạng, reconnect, giữ input và xóa kết quả cũ.
- [x] Kiểm mock được nhận diện rõ; bản demo thật không có fallback nhãn mẫu.
- [x] Chỉnh mức cần thiết để giao diện tiếng Việt dễ đọc, bố cục gọn, nút/trạng thái rõ trên màn hình demo; không thêm framework hoặc chức năng mới.
- [x] Chạy Chrome và Edge đã cài, ghi phiên bản và ảnh suy luận thực từ UI → API → hai model.

**Đạt khi:** Tests trình duyệt đạt trên cả hai browser; hiển thị hai nhãn thật, phản hồi lỗi rõ và không bị kẹt loading.

Kết quả 2026-10-31: 42 tests Frontend đạt trên Chrome/Edge; toàn suite 224 passed, không skip, 12 warnings đã biết. Review độc lập không có phát hiện trong phần sửa; xem reports/evidence/phase-4/README.md. Chưa triển khai Phase 5–6.

## Phase 5 — Kiểm thử tổng thể và đóng gói demo

**Files:** tests/, docs/development.md, docs/acceptance.md, reports/demo-script.md, reports/evidence/phase-6/.

- [x] Chạy toàn suite: `$env:TV2_RUN_REAL_DATA='1'; ./.venv/Scripts/python.exe -m pytest -q`; các tests real artifact/browser bắt buộc không skip để tính đạt.
- [x] Kiểm startup lạnh, restart, thiếu model và đổi cwd; diễn tập nhập câu mới, câu lỗi và phục hồi.
- [x] Xác minh demo không phụ thuộc dịch vụ ML/mạng ngoài sau khi đã cài dependencies và có artifact local; đo thời gian thực, không tự đặt SLA.
- [x] Chạy review độc lập trên bản cuối, sửa lỗi chặn demo/vi phạm hợp đồng bằng regression test, chạy lại bộ liên quan và toàn suite.
- [x] Chuẩn bị bản bàn giao local dễ tìm: code, lock, hướng dẫn, vị trí artifact và cách chạy. Dataset/model vẫn local, không tự upload.
- [x] Ma trận nghiệm thu phân biệt kỹ thuật đạt, hạn chế, P1 không áp dụng và việc leader còn cần duyệt.

**Đạt khi:** Toàn luồng chạy lặp lại được, không còn lỗi chặn demo, có log/ảnh và hướng dẫn đã thực thi. Phát hiện lỗi ở phase trước thì quay lại sửa, không bỏ qua để đúng thứ tự.

## Phase 6 — Báo cáo, slide và bàn giao leader

**Files:** reports/build_delivery.py, final-report.docx, presentation.pptx, demo-script.md, contributions.md; README.md, docs/team-start.md, docs/roadmap/*, docs/acceptance.md, docs/archive/scaffold-manifest-phase0.json và báo cáo vai trò.

- [ ] Tổng hợp báo cáo theo 6 phần BRD: Goal and Motivation, Background, Proposed Model, Technique/Method, Result, Conclusion & Future Work; tối đa 80 trang.
- [ ] Bảng so sánh đủ ba thuật toán cho mỗi task, chỉ số từng lớp, confusion matrix, ảnh app thật, cách tái lập và giới hạn.
- [ ] Tạo slide từ cùng số liệu, kịch bản thuyết trình/demo và câu hỏi thường gặp về train/validation/test, TF-IDF, mất cân bằng lớp, sai dự đoán.
- [ ] Ghi đóng góp đúng lịch sử thành viên và phần hỗ trợ tích hợp; không tự tạo tên, lịch nộp hoặc minh chứng làm việc.
- [ ] Cập nhật tài liệu tổng quan lỗi thời; giữ bản thí nghiệm lịch sử để truy vết. Không ghi quyền nguồn là approved.
- [ ] Xuất Word/PPTX, mở/kiểm cấu trúc và nội dung, kiểm hình/bảng/layout. Giao leader bản xem trước cùng danh sách file thay đổi.

**Đạt khi:** Bộ code + demo + báo cáo + slide nhất quán và review được. Leader bổ sung thông tin hành chính còn thiếu trước nộp; trợ lý không tự gửi Classroom hay merge repository.

## Cách thực hiện sau duyệt

- Chạy lần lượt Phase 1–6, kế thừa kết quả đã làm; không làm lại chỉ để đủ quy trình.
- Trợ lý triển khai trực tiếp và báo ngắn kết quả mỗi phase; tiếp tục phase sau khi đủ điều kiện kỹ thuật, không xin lại phép cho từng sửa nhỏ.
- Dừng và hỏi khi thiếu đầu vào thật sự không tự lấy được hoặc phải thay phạm vi/giao diện chung; nêu rõ phần bị chặn và cách người dùng cung cấp. Không tự thêm cổng xin giấy phép vào demo local đã được leader chọn.
- Chưa triển khai theo kế hoạch này trước khi leader duyệt. Đây là kế hoạch mới thay thế hướng dừng toàn bộ vì giấy phép ở ledger trước; không xóa lịch sử đó.
