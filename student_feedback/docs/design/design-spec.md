# Thiết kế dự án độc lập student_feedback

Trạng thái: chờ người dùng duyệt. Nhánh: chore/project-cleanup.

## Mục tiêu và quyết định

Người dùng chọn tổ chức lại theo chức năng trong folder student_feedback/ ngay tại gốc checkout tích hợp. Folder này là một project root riêng, không tạo Git repo lồng nhau. Giữ nguyên demo_v3 và các nguồn cũ để đối chiếu. Bản mới bao gồm chạy web, dữ liệu, huấn luyện, đánh giá, kiểm thử và hướng dẫn; có thể sao chép ra ngoài repo và sử dụng độc lập sau khi cài dependencies và chuẩn bị artifact/dataset.

Các phương án đã cân nhắc: (1) sao chép nguyên cấu trúc hiện tại, ít thay đổi nhưng giữ nợ kỹ thuật; (2) tổ chức lại theo chức năng, cần kiểm chứng tương đương nhưng dễ bảo trì. Người dùng chọn (2).

Đây là tái cấu trúc, không thiết kế lại UI, thay thuật toán, nâng dependencies, thêm tài khoản/database hoặc tự động triển khai model mới. Bảo toàn 3 tab và API v3. Dự án mới dùng FastAPI, HTML/CSS/JS và scikit-learn như bản hiện tại.

## Cấu trúc đề xuất

```text
student_feedback/
  README.md
  pyproject.toml
  .gitignore
  .env.example
  requirements/             # runtime, train, test, browser và lock
  src/
    feedback_ai/
      api/                  # app factory, routes, schemas, error mapping
      services/             # phân tích đơn/danh sách, cảm xúc theo chủ đề
      inference/            # model loader, signals, policy, evidence detector
      data/                 # acquisition, loader, normalization, validation, EDA
      training/             # sentiment/topic, lựa chọn, thí nghiệm
      evaluation/           # metrics, confusion matrix, so sánh, error analysis
      io/                   # CSV/XLSX import và export
      common/               # hashing, JSON, nhãn dùng chung
      resources/            # rules.json được đóng gói
      web/                  # HTML/CSS/JS và Excel mẫu được đóng gói
      config.py
      cli.py
    ml/                     # shim tương thích pickle cũ khi cần
    reports/                # shim tối thiểu cho callback pickle cũ khi cần
  configs/                  # cấu hình baseline, thí nghiệm và profile serving
  data/                     # raw/processed, ignored trừ hướng dẫn
  artifacts/                # serving, candidates, manifest; payload local ignored
  outputs/                  # báo cáo/metrics theo run, generated và ignored
  notebooks/                # EDA, sentiment, topic gọi module của project mới
  tests/                    # unit, integration, browser, parity; conftest.py
  docs/                     # architecture, data, training, evaluation, operations
```

Tên file/module chi tiết do implementer quyết định. Chỉ tạo shim thực sự cần cho deserialization; toàn bộ code mới import feedback_ai, không dùng shim làm kiến trúc chính. Không đưa toàn bộ logs và bằng chứng lịch sử vào project mới.

## Phụ thuộc và tính độc lập

Hiện demo_v3.service gọi demo_v2.service; module này dùng backend.model_service và reports.ct5_selective_prediction. Các hàm inference dùng chung phải chuyển vào feedback_ai, không import script thí nghiệm để chạy server. Tách batch.py thành routes/schema, file import/export và dịch vụ; tách frontend theo tab, state, import, API và render, giữ hợp đồng API và thứ tự thao tác.

Model hiện nằm ở .local-tools/ct4-augmentation/run-1/research-selected; policy và provenance nằm ở .local-tools/ct5-selective-prediction/run-1. Bản mới sử dụng artifacts/serving với manifest mô tả đường dẫn tương đối, checksum và nguồn gốc. Có lệnh nhập bundle local chỉ sao chép danh sách file cần thiết, kiểm tra checksum trước/sau. Lệnh này có thể nhận đường dẫn nguồn cũ cho migration một lần; server/train/evaluate không tự tìm lại repo cũ.

Không thay byte của model và rules đang dùng. Giữ kiểm tra nhãn, phiên bản, metadata, receipt và checksum; không sửa receipt gốc để làm hợp lệ đường dẫn mới. Lưu receipt gốc như bằng chứng và dùng migration manifest liên kết hash với vị trí mới. Kiểm tra callback của pickle bằng loader trong tiến trình độc lập; artifact có thể tham chiếu ml.preprocessing.normalize_text và module reports. Cung cấp shim tự chứa trỏ tới implementation tương đương trong project mới, không sys.path hack hoặc import ngoài folder. Không deserialize artifact không rõ nguồn.

Các giá trị mặc định resolve theo project/config, không cwd. Hỗ trợ cấu hình đường dẫn rõ ràng; .env.example là tài liệu, không ngụ ý tự load .env nếu chưa triển khai. Giữ Python 3.13 và phiên bản ML hiện có. Runtime/train/test dùng nhóm dependency riêng, lock xuất phát từ môi trường hiện hành, bổ sung openpyxl và tài nguyên web vào package. Kiểm chứng wheel chứa tài nguyên và chạy được từ cwd bên ngoài.

## Dữ liệu, huấn luyện và đánh giá

Giữ split UIT-VSFC chính thức, mapping nhãn gốc, normalization, tham số và tiêu chí chọn model bằng validation. Lệnh riêng cho acquisition/import, validate, EDA, train sentiment/topic và evaluate. Train tạo run mới, không ghi đè artifacts/serving. Bộ dữ liệu và model không tự đưa lên Git; README hướng dẫn chuẩn bị từ nguồn và local bundle.

Mang vào code tái lập các hướng nghiên cứu hiện có CT1–CT5: baseline evaluation, class weights, word/character features, augmentation và selective prediction. Tách reusable logic khỏi CLI tạo báo cáo; không copy nguyên lịch sử outputs. Cấu hình/seed/provenance đi cùng mỗi run. Notebook gọi các API/CLI mới, không phụ thuộc thư mục cha.

Baseline dùng 3 nhãn sentiment và 4 nhãn topic gốc. Serving v3 dùng nhãn hỗn hợp/chưa xác định và nhiều chủ đề dựa trên rules; CT4 chỉ audit. Hai bộ nhãn được phân biệt rõ trong code/docs/metrics. Không dùng điểm baseline để tuyên bố độ chính xác của bộ nhãn v3.

Phạm vi xác minh: chạy pipeline dữ liệu trên dataset local, chạy train/evaluate baseline thực tế với output mới và kiểm thử các thí nghiệm bằng fixtures. Không mặc định chạy lại toàn bộ CT1–CT5 tốn thời gian; cung cấp lệnh tái lập, ghi rõ những thí nghiệm chưa chạy lại. Server tiếp tục dùng bundle frozen hiện tại, không promote model vừa train.

## Hành vi ứng dụng phải giữ

Giữ /api/health, /api/v3/predict, /import, /analyze-row, /export dưới prefix hiện tại; nhãn, JSON, mã HTTP, lỗi và giới hạn input/file giống bản cũ. Giữ 5000 codepoint/phản hồi, 500 dòng, 5 MiB; bảo toàn duplicate, multiline cell, source row/id, dòng lỗi, retry/stop và xuất đầy đủ dù đang lọc. Giữ cách tính thống kê và cảm xúc theo chủ đề. Kiểm tra route asset và tải template.

Giao diện tiếp tục 3 tab, state riêng cho paste/file, bảo toàn input, chống kết quả stale, timeout, recovery, keyboard và mobile. Bản mới chạy cổng mặc định 8003 trong đối chiếu, để bản cũ 8002 tiếp tục hoạt động; cổng có thể cấu hình.

## Kiểm thử và tiêu chí chấp nhận

1. Trước migration ghi hash nguồn/artifact/rules và lưu corpus parity cùng output thực tế của bản cũ.
2. Chạy server cũ/mới trên cùng input; so sánh status/JSON, nhãn và logic lỗi; XLSX so sánh sheet/cell/type thay vì hash ZIP có timestamp.
3. Fixture browser nằm trong conftest.py của project mới, không import file test đã mất; pytest thu thập toàn bộ test. Test unit không đòi artifact private; integration/browser đánh dấu rõ, không coi skip là thành công tích hợp.
4. Chạy đủ integration với bundle local thật, browser Chrome/Edge nếu có, gồm tab, nhập CSV/XLSX, retry, stop, export và mobile.
5. Copy riêng student_feedback ra thư mục tạm ngoài repo, cài project vào venv riêng, bỏ PYTHONPATH cũ; kiểm tra module origins nằm trong project/package mới, chạy health/predict và data/train/evaluate. Không truy cập .local-tools cũ ngoài lệnh migration có nguồn chỉ định.
6. Thiếu/hỏng bundle: server vẫn phục vụ UI và health chưa sẵn sàng; suy luận trả lỗi hợp đồng. Bundle đúng: kết quả tương đương bản cũ.
7. README có lệnh cài, chuẩn bị dữ liệu/model, chạy, train, evaluate, test và giới hạn; không hướng dẫn backend.main cũ.
8. Hash file nguồn cũ và artifact frozen trước/sau giống nhau. Chỉ thêm folder mới và tài liệu thiết kế/kế hoạch được duyệt.

## Trình tự và bàn giao

Thực hiện sau khi duyệt thiết kế: khóa baseline -> skeleton/package/config -> bundle loader/compatibility -> chuyển inference/API/UI -> data/train/evaluate/research -> test parity/isolated install -> docs và kiểm tra cuối. Chia commit theo mốc trên nhánh clean. Không merge main hoặc xóa bản cũ trong phạm vi này. Các lỗi cũ ngoài mục tiêu ghi riêng; nếu sửa làm đổi output phải có quyết định riêng, không giấu trong refactor.

Quyết định giao implementer: tên module nhỏ, cách chia JS, test fixtures và CLI flags cụ thể, layout tài liệu. Không tự quyết định đổi schema, nhãn, artifact phục vụ, preprocessing hoặc thuật toán.
