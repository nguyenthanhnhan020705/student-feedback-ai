# Báo cáo vai trò Data

## 1. Mục tiêu

Phụ trách chuẩn bị và kiểm tra dữ liệu đầu vào cho project `student-feedback-ai`, sử dụng bộ dữ liệu UIT-VSFC phục vụ bài toán phân tích phản hồi sinh viên.

Các nhiệm vụ chính:
- Xác định nguồn dữ liệu và lưu trữ dữ liệu gốc.
- Xây dựng hoặc kiểm tra quy trình đọc các tập dữ liệu.
- Chuẩn hóa dữ liệu văn bản và nhãn theo quy ước của project.
- Kiểm tra dữ liệu lỗi, dữ liệu thiếu và tính nhất quán giữa các tập dữ liệu.
- Thực hiện khám phá dữ liệu (EDA), ghi nhận kết quả vào báo cáo và bàn giao dữ liệu cho các thành viên phụ trách mô hình.

## 2. Nguồn dữ liệu

- Tên bộ dữ liệu: UIT-VSFC (Vietnamese Students' Feedback Corpus).
- Nguồn tham khảo: https://huggingface.co/datasets/ura-hcmut/UIT-VSFC
- Các tập dữ liệu sử dụng: `train`, `valid`, `test`.
- Định dạng dữ liệu đầu vào: CSV.
- Các trường dữ liệu chính: `text`, `label`.

Dữ liệu gốc được lưu trong `data/raw/`. Không chỉnh sửa trực tiếp các file dữ liệu gốc trong quá trình tiền xử lý.

## 3. Quy trình xử lý dữ liệu

### 3.1. Đọc dữ liệu

Sử dụng module `ml/data.py` để đọc các tập `train`, `valid`, `test`. Kiểm tra sự tồn tại của file, cấu trúc cột và khả năng đọc dữ liệu trước khi đưa vào các bước phân tích tiếp theo.

### 3.2. Kiểm tra và chuẩn hóa

Thực hiện kiểm tra dữ liệu theo quy tắc của project, bao gồm:
- Kiểm tra các cột bắt buộc `text` và `label`.
- Chuẩn hóa văn bản theo quy tắc đã triển khai trong mã nguồn.
- Kiểm tra văn bản rỗng, nhãn rỗng và nhãn không thuộc tập nhãn cho phép.
- Kiểm tra sự nhất quán giữa các tập dữ liệu.

Các bản ghi không hợp lệ được xử lý theo chính sách trong loader hoặc pipeline. Những trường hợp bị loại bỏ hay sửa đổi cần được ghi nhận để bảo đảm khả năng truy vết.

### 3.3. Khám phá dữ liệu (EDA)

Thực hiện khám phá dữ liệu bằng notebook `notebooks/01_eda.ipynb`.

Các nội dung phân tích gồm:
- Kích thước từng tập dữ liệu.
- Phân bố nhãn cảm xúc.
- Số lượng và tỷ lệ bản ghi theo nhãn.
- Độ dài văn bản và đặc điểm cơ bản của phản hồi sinh viên.
- Các vấn đề dữ liệu phát hiện trong quá trình kiểm tra.

Chỉ đưa số liệu, biểu đồ và nhận xét vào báo cáo sau khi đã chạy và kiểm tra kết quả thực tế.

## 4. Quản lý dữ liệu và manifest

File `manifest.json` được sử dụng để lưu thông tin mô tả dữ liệu và hỗ trợ truy vết nguồn dữ liệu theo cấu trúc thực tế của project.

Cần kiểm tra các thông tin có trong manifest, chẳng hạn:
- Nguồn dữ liệu và phiên bản hoặc mã commit nếu có.
- Danh sách tập dữ liệu.
- Đường dẫn hoặc thông tin nhận diện các file đầu vào.
- Thông tin số lượng bản ghi hoặc kiểm tra dữ liệu nếu được triển khai.
- Thông tin phiên bản và quy tắc xử lý nếu có.

Manifest cần phản ánh đúng dữ liệu và quy trình đã thực hiện; không xem việc có file `manifest.json` là bằng chứng rằng tất cả nội dung đã được xác minh.

## 5. Kết quả thực hiện

- Notebook EDA: `notebooks/01_eda.ipynb`.
- Module đọc dữ liệu: `ml/data.py`.
- Manifest dữ liệu: `manifest.json` tại `report/data/manifest.json`.
- Báo cáo vai trò Data: `docs/data/report.md`.

Kết quả kiểm tra thực tế:

| Hạng mục | Kết quả |
|---|---|
| Đọc thành công các tập dữ liệu | [Đã xác nhận ] |
| Kiểm tra cấu trúc cột | [Gồm 2 cột text và label] |
| Kiểm tra bản ghi rỗng và nhãn không hợp lệ | [Phát hiện bản ghi có bản ghi text và label rỗng trong UIT-VSFC_valid.csv, tại dòng CSV 1585], [về nhãn không hợp lệ thì chưa kiểm tra tính phù hợp]  |
| Thống kê số lượng bản ghi | [train: 11426 bản ghi; test: 3166 bản ghi; valid: 1583 bản ghi] |
| Phân tích phân bố nhãn | [train: 5643 positive(49,39%), 5325 negative(46,60%), 458 neutral(0.4%)],
                           [test: 1590 positive(50.22%), 1409 negative(44.50%), 167 neutral (5,27%)],
                           [valid: 805 positive(50,85%), 705 negative(44,54%), 73 neutral(4,61%)] |
| Hoàn thành notebook EDA | [Đã thực hiện khám phá dữ liệu bao gồm đọc dữ liệu; thống kê số lượng bản ghi từng tập train, test, valid; thống kê số lượng và tỷ lệ nhãn sentiment của từng tập; thiết lập biểu đồ số lượng các nhãn sentiment; khảo sát đặc điểm độ dài văn bản. Kết quả được lưu trong notebook để phục vụ kiểm tra và đánh giá dữ liệu] |
| Hoàn thành kiểm tra manifest | [Đã kiểm tra ] |

## 6. Minh chứng

Các minh chứng được lưu theo cấu trúc của project:

- `evidence/data/`: ảnh chụp hoặc log thể hiện kết quả kiểm tra dữ liệu, quá trình xử lý và manifest.
- `metrics/`: lưu số liệu thống kê nếu project quy định vị trí này cho kết quả Data.
- `figures/`: lưu biểu đồ EDA đã tạo từ dữ liệu thật.

Tên file và vị trí lưu minh chứng cần thống nhất với nhóm. Không đưa ảnh minh họa tự tạo hoặc số liệu chưa được chạy thực tế vào phần nghiệm thu.

## 7. Bàn giao và hạn chế

Bàn giao cho các thành viên Sentiment và Topic dữ liệu cùng quy tắc đọc, chuẩn hóa và nhãn đã thống nhất trong project.

Trước khi nghiệm thu, cần xác nhận:
- Các tập dữ liệu được đọc đúng.
- Chính sách xử lý dữ liệu không hợp lệ được ghi nhận.
- Các thống kê và biểu đồ có thể tái tạo từ notebook hoặc mã nguồn.
- Manifest phù hợp với nguồn dữ liệu và phiên bản đang sử dụng.
- Các file đầu ra và minh chứng được lưu đúng vị trí.
Những hạng mục chưa có kết quả chạy thực tế được ghi nhận là chưa hoàn thành, không thay bằng số liệu giả.
