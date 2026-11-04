# Student Feedback AI

Demo học phần phân tích phản hồi sinh viên tiếng Việt: nhập một câu → hai pipeline AI → nhãn cảm xúc và chủ đề.

## Phạm vi hiện tại

- Cảm xúc: `negative`, `neutral`, `positive`.
- Chủ đề: `lecturer`, `curriculum`, `facility`, `other` (mapping chính thức xem đặc tả Data).
- UIT-VSFC, tiền xử lý dùng chung, TF-IDF; so sánh Naive Bayes, Logistic Regression và Linear SVM cho mỗi nhiệm vụ.
- FastAPI phục vụ API và giao diện HTML/CSS/JavaScript cùng origin; suy luận bằng hai model local.
- Đầu ra học phần: code, thí nghiệm, demo, báo cáo và slide. CSV/batch/export/Dashboard chưa thuộc phạm vi triển khai.

## Trạng thái đã xác minh

Bản tích hợp hiện ở `.local-tools/integration-p0` của checkout gốc, nhánh `feature/integration-p0`; chưa merge/push. Checkout gốc là nguồn công việc thành viên, không phải bản ứng dụng tích hợp đầy đủ.

Phase 1 của kế hoạch mới đã hoàn thành: cài môi trường sạch, khóa dependencies, `pip check` đạt; 13 tests health/tích hợp đạt với 1 cảnh báo thư viện. Server/UI chạy từ cwd ngoài repo, xử lý được trường hợp thiếu model. Đã có dataset, hai artifact và metrics thật local; chưa nghiệm thu toàn dự án.

Phase 2 đã hoàn thành xác minh Data/ML: 63 tests đạt, không skip; checksum nguồn và hai artifact khớp, metrics validation/test của winner tái lập. Không train lại. Xem [bằng chứng Phase 2](reports/evidence/phase-2/README.md).

Phase 3 đã hoàn thành phần Backend theo phạm vi kế hoạch: 119 tests Backend/tích hợp đạt, HTTP thật khớp hai pipeline; UTF-8 JSON sai trả đúng 422 và metadata được kiểm đầy đủ hơn. Review còn một lỗi nhỏ sẵn có ở tên trường lỗi của khóa JSON Unicode bất thường (vẫn từ chối 422); xem [bằng chứng Phase 3](reports/evidence/phase-3/README.md).

Phase 4 hoàn thành ngày 2026-10-31: sửa kiểm nhãn prototype/sai kiểu và timeout bao gồm response body; 42 tests Frontend đạt trên Chrome/Edge. Toàn suite với dữ liệu thật đạt 224 tests, không skip, 12 cảnh báo thư viện đã biết. Review độc lập không có phát hiện trong phần sửa. Xem [bằng chứng Phase 4](reports/evidence/phase-4/README.md). Phase 6 chưa triển khai; chưa nghiệm thu toàn sản phẩm.

Phase 5 hoàn thành phần kiểm thử/diễn tập local: 224 tests đạt, không skip; Chrome/Edge chạy restart, thiếu model và phục hồi dưới network guard. Gói nội bộ có manifest và kiểm chứng giải nén; xem [bàn giao demo](DEMO.md), [bằng chứng Phase 5](reports/evidence/phase-5/README.md) và [ma trận nghiệm thu](docs/acceptance.md). Review độc lập không còn phát hiện trong phạm vi Phase 5.

## Chạy dự án

CT1 cải tiến chất lượng đã thiết lập mốc đánh giá ngày 2026-10-31: snapshot
baseline, validation và 39 ca lỗi đã biết, có công cụ replay và quy trình chọn
ứng viên. Xem [bằng chứng CT1](reports/evidence/ct1/README.md) và
[quy trình đánh giá](docs/quality/ct1-protocol.md). CT1 chưa thay model hoặc
cải thiện dự đoán. CT2 đã chạy thí nghiệm trọng số lớp: xem
[báo cáo và đánh đổi](docs/quality/ct2-report.md). Các ứng viên nghiên cứu tăng
Macro F1 validation nhưng giảm Accuracy và có ca hồi quy; model demo giữ nguyên.
CT3 đã có thí nghiệm từ + ký tự; xem [báo cáo CT3](docs/quality/ct3-report.md).
Macro F1 cảm xúc tăng nhưng tỷ lệ hai nhãn cùng đúng giảm trên validation;
model demo vẫn giữ baseline. CT4–CT5 và Phase 6 chưa triển khai.

Đọc [hướng dẫn cài và chạy đã kiểm chứng](docs/development.md). Từ checkout gốc, chuyển đến `.local-tools/integration-p0`, sau đó:

```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

Mở `http://127.0.0.1:8000/`. Không cần API key, GPU hay database. Clone Git mới không tự có dữ liệu/model bị ignore; không coi file metadata là model đã sẵn sàng. Nguồn dataset vẫn ghi quyền sử dụng/phân phối `unknown`; không có bước công bố dataset/model trong kế hoạch local.

## Kế hoạch và phân công

Theo [kế hoạch sáu phase đã duyệt](docs/superpowers/plans/2026-10-30-course-demo-completion.md) và [nhật ký thực hiện](docs/superpowers/plans/course-demo-progress.md): môi trường → Data/ML → Backend → Frontend → kiểm thử/demo → báo cáo/bàn giao. Không dùng số phase của roadmap lịch sử để giao việc mới.

| Thành viên | Phụ trách | Nhánh |
| --- | --- | --- |
| TV2 | Data | `feature/data-preprocessing` |
| TV3 | Sentiment | `feature/sentiment-model` |
| TV4 | Topic | `feature/topic-model` |
| TV5 | Backend | `feature/backend-api` |
| TV6 | Frontend | `feature/frontend-dashboard` |

Giữ [quyền sở hữu chức năng](docs/function-ownership.md), [đặc tả Phase 0](docs/specs/README.md) và [quy trình review/PR](CONTRIBUTING.md). Leader duyệt trước merge; thay đổi hợp đồng chung cần duyệt riêng.

## Tài liệu và mã nguồn

- `ml/`, `notebooks/`: xử lý dữ liệu, train/evaluate/predict và thí nghiệm.
- `backend/`, `frontend/`, `tests/`: ứng dụng P0 và kiểm thử.
- `models/`, `data/`: artifact/dataset local và hướng dẫn.
- `reports/`: metrics, hình, bằng chứng thật và công cụ báo cáo; Word/PPTX cuối chưa nghiệm thu.
- `docs/archive/`: BRD, roadmap và ledger cũ để truy vết, không phải kế hoạch đang thực thi.

Xem [biên bản dọn dự án](docs/cleanup-2026-10-30.json). Chỉ loại file P1 rỗng; giữ code, bằng chứng, dữ liệu và công việc chưa commit.
