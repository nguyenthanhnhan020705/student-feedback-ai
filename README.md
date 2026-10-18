# STUDENT FEEDBACK AI

**Hệ thống phân tích cảm xúc và phân loại chủ đề phản hồi sinh viên bằng Machine Learning**  
*Student Feedback Sentiment & Topic Classification System*

> **Trạng thái:** Đang xây dựng – đồ án cuối kỳ môn Cơ sở và Ứng dụng Trí tuệ nhân tạo (AI).  
> **Nhóm:** 06 thành viên, chuyên ngành GIS / Hệ thống thông tin.  
> **Thời gian triển khai:** 03 tuần (21 ngày).  
> **Người quản lý dự án:** Trưởng nhóm (Leader).  
> **Lưu ý:** Đây là tài liệu giới thiệu, đặc tả chức năng và hướng dẫn triển khai. Các tính năng, kết quả AI và chỉ số đánh giá chỉ được xem là **hoàn thành sau khi được lập trình, huấn luyện và kiểm thử thực tế**.

---

## 1. Giới thiệu dự án

### 1.1. Bối cảnh và vấn đề

Tại các trường đại học, sinh viên thường đưa ra phản hồi về giảng viên, nội dung chương trình đào tạo, phòng học và cơ sở vật chất. Nếu lượng phản hồi lớn, việc đọc và phân loại thủ công mất thời gian và khó tổng hợp thành báo cáo.

Dự án **Student Feedback AI** ứng dụng **Natural Language Processing (NLP)** và **Machine Learning (ML)** để phân loại tự động phản hồi tiếng Việt theo hai nhiệm vụ độc lập:

1. **Phân loại cảm xúc (Sentiment Classification):** `Tiêu cực`, `Trung tính`, `Tích cực`.
2. **Phân loại chủ đề (Topic Classification):** `Giảng viên`, `Chương trình đào tạo`, `Cơ sở vật chất`, `Khác`.

Kết quả được tích hợp vào website để phân tích một câu, xử lý nhiều câu từ CSV và tổng hợp Dashboard.

### 1.2. Ví dụ đầu vào / đầu ra mong muốn

| Phản hồi tiếng Việt | Cảm xúc kỳ vọng | Chủ đề kỳ vọng |
|---|---|---|
| Giảng viên giảng bài rất dễ hiểu và nhiệt tình. | Tích cực | Giảng viên |
| Máy chiếu trong phòng học thường xuyên bị hỏng. | Tiêu cực | Cơ sở vật chất |
| Môn học gồm ba tín chỉ. | Trung tính | Chương trình đào tạo |

Các ví dụ trên **chỉ thể hiện ý nghĩa bài toán**, không phải kết quả đã đo của mô hình.

**Giới hạn của phiên bản đầu:** Một câu được dự đoán **01 nhãn cảm xúc + 01 nhãn chủ đề**. Ví dụ câu "Giảng viên nhiệt tình nhưng phòng học khá nóng" chứa nhiều khía cạnh, do đó có thể gây nhầm lẫn. Phân tích cảm xúc theo từng khía cạnh (ABSA) là hướng mở rộng, **không bắt buộc trong 3 tuần**.

### 1.3. Mục tiêu học thuật

- Nghiên cứu quy trình ML có giám sát (Supervised Learning) cho bài toán phân loại văn bản.
- Khảo sát và chuẩn hóa dữ liệu tiếng Việt; biểu diễn văn bản bằng **TF-IDF**.
- Huấn luyện, so sánh **Multinomial Naive Bayes**, **Logistic Regression** và **Linear SVM** cho **từng nhiệm vụ**.
- Báo cáo **Accuracy, Precision, Recall, Macro F1-score, Confusion Matrix** trên tập kiểm thử độc lập.
- Tích hợp mô hình tốt nhất của mỗi nhiệm vụ vào website thật thông qua **FastAPI**.
- Cung cấp mã nguồn có thể tái lập, tài liệu hướng dẫn và demo cuối kỳ.

**Không thuộc phạm vi bắt buộc:** Chatbot/LLM, PhoBERT, đăng nhập/đăng ký, ứng dụng điện thoại, bản đồ GIS, tự động thu thập dữ liệu sinh viên, triển khai cloud. Chỉ làm khi các chức năng cốt lõi đã ổn định.

---

## 2. Người dùng và chức năng hệ thống

**Đối tượng sử dụng dự kiến:** Sinh viên hoặc người thực hiện khảo sát; giảng viên, khoa, bộ phận quản lý đào tạo cần tổng hợp phản hồi.

### F01 – Phân tích một phản hồi (bắt buộc)

- Nhập **một câu hoặc đoạn phản hồi tiếng Việt** trong ô nhập.
- Bấm **Phân tích AI**.
- Website gọi API `POST /api/predict` để dự đoán bằng hai mô hình ML đã huấn luyện.
- Hiển thị **cảm xúc** và **chủ đề**; thông báo rõ ràng khi đầu vào trống hoặc mô hình chưa sẵn sàng.
- Không tạo nhãn giả/hard-code trên giao diện hoặc trong backend.

### F02 – Phân tích CSV hàng loạt (mục tiêu tuần 3)

- Nhận tệp `.csv` UTF-8 có cột `text` (mỗi dòng một phản hồi).
- Gọi `POST /api/predict-batch`; backend phân loại từng dòng.
- Hiển thị bảng kết quả và cho phép xuất CSV với các cột `text`, `sentiment`, `topic`.
- Phiên bản đầu hỗ trợ **tối đa 1.000 dòng/tệp và 2 MB/tệp**; nếu vượt giới hạn, báo lỗi dễ hiểu.

### F03 – Dashboard thống kê (mục tiêu tuần 3)

- Tổng số phản hồi đã phân tích của **lần xử lý hiện tại**.
- Biểu đồ phân bố 3 nhóm cảm xúc.
- Biểu đồ phân bố 4 nhóm chủ đề.
- Bảng xem kết quả chi tiết và tải dữ liệu.
- Các con số phải tính từ **kết quả mô hình thực tế của lượt phân tích**, không hiển thị tỷ lệ mẫu cố định.
- Không bắt buộc có cơ sở dữ liệu để lưu lịch sử trong phiên bản đầu.

### F04 – Báo cáo đánh giá thuật toán (bắt buộc)

- Trình bày các mô hình đã thử cho từng nhiệm vụ (cảm xúc / chủ đề).
- Bảng Accuracy, Precision, Recall và Macro F1; Confusion Matrix của mô hình được chọn.
- Có notebook/script làm căn cứ tái lập kết quả.
- Giao diện có thể chỉ cần một trang **Model Evaluation** đọc các file JSON kết quả thực nghiệm (không cần huấn luyện ngay trên web).
- **Không tự sinh dữ liệu đánh giá giả định** khi chưa chạy mô hình.

### Giao diện dự kiến

1. **Trang Phân tích AI:** textarea, nút phân tích, 2 thẻ kết quả.
2. **Trang Phân tích CSV:** chọn tệp, xử lý, bảng kết quả, nút xuất CSV.
3. **Trang Dashboard:** thẻ thống kê, biểu đồ cảm xúc/chủ đề.
4. **Trang Đánh giá ML:** bảng so sánh thuật toán và hình Confusion Matrix (nếu đã có kết quả).

Thiết kế: giao diện đơn giản, hiện đại, dùng tiếng Việt, dễ demo trên màn hình máy tính; ưu tiên responsive ở mức cơ bản, không cần framework frontend phức tạp.

---

## 3. Dataset: UIT-VSFC

**Nguồn tham khảo chính:** [UIT-VSFC – GitHub giới thiệu corpus](https://github.com/kietnv/uit-vsfc), [UIT NLP Group – Datasets](https://sites.google.com/uit.edu.vn/uit-nlp/datasets).

- Bộ dữ liệu **Vietnamese Students' Feedback Corpus (UIT-VSFC)** gồm **hơn 16.000 câu** phản hồi sinh viên có gán nhãn cho cả sentiment và topic.
- Một bản phân phối phổ biến gồm **11.426 train / 1.583 validation / 3.166 test** (tổng 16.175 câu). **Phải kiểm tra số lượng và sơ đồ nhãn với đúng bản nhóm tải về trước khi sử dụng.**
- Sử dụng dữ liệu cho nghiên cứu/học tập; kiểm tra **giấy phép và quy định chia sẻ** trước khi đưa toàn bộ corpus lên GitHub. Repository không tự động chứa bản sao dữ liệu của bên thứ ba.

### Cấu trúc dữ liệu chuẩn nội bộ

Sau khi đọc dữ liệu gốc, bộ xử lý xuất ba tệp CSV:

```text
data/processed/train.csv
data/processed/validation.csv
data/processed/test.csv
```

Mỗi tệp có ba cột:

```csv
text,sentiment,topic
"Giảng viên rất nhiệt tình",2,0
```

Dòng ví dụ chỉ minh họa cấu trúc. **Không dùng những ví dụ do nhóm tự viết làm số liệu đánh giá thay cho corpus chuẩn.**

**Bảng nhãn dự kiến theo một bản phân phối UIT-VSFC:**

| Trường | Mã | Ý nghĩa |
|---|---|---|
| `sentiment` | `0` | Tiêu cực (`negative`) |
| `sentiment` | `1` | Trung tính (`neutral`) |
| `sentiment` | `2` | Tích cực (`positive`) |
| `topic` | `0` | Giảng viên (`lecturer`) |
| `topic` | `1` | Chương trình đào tạo (`training_program`) |
| `topic` | `2` | Cơ sở vật chất (`facility`) |
| `topic` | `3` | Khác (`other`) |

> **Bắt buộc:** TV2 và TV3/TV4 kiểm tra nhãn gốc khi tải về; nếu phiên bản khác dùng mã khác, sửa cấu hình mapping và ghi nguồn. Không suy đoán ý nghĩa nhãn từ một vài ví dụ.

### Nguyên tắc xử lý dữ liệu

- Giữ nguyên tập **train / validation / test** nếu nguồn đã cung cấp; không trộn rồi chia ngẫu nhiên để tránh sai lệch so sánh.
- Chuẩn hóa Unicode/khoảng trắng/ký tự không cần thiết một cách nhất quán.
- Nếu dùng tách từ tiếng Việt, **hàm tiền xử lý lúc train phải giống hệt lúc predict**.
- `TfidfVectorizer` phải **fit trên train**, rồi transform cho validation và test, tránh **data leakage**.
- Không chọn thuật toán theo test. Chọn siêu tham số bằng validation; chạy test khi đã chốt mô hình.
- Thống kê mất cân bằng lớp và xem kỹ F1 theo từng nhãn, nhất là nhãn trung tính.

---

## 4. Kiến trúc kỹ thuật

```text
                    ┌──────────────────────┐
                    │  Frontend (Browser)  │
                    │ HTML / CSS / JS      │
                    └──────────┬───────────┘
                               │ HTTP / JSON / CSV
                               ▼
                    ┌──────────────────────┐
                    │   FastAPI Backend    │
                    │ /api/predict         │
                    │ /api/predict-batch   │
                    │ /api/health          │
                    └──────────┬───────────┘
                               │
                   ┌───────────┴───────────┐
                   ▼                       ▼
       ┌────────────────────┐  ┌────────────────────┐
       │ Sentiment Pipeline │  │ Topic Pipeline     │
       │ TF-IDF + ML        │  │ TF-IDF + ML        │
       └────────────────────┘  └────────────────────┘
                   ▲                       ▲
                   └───────────┬───────────┘
                               │
                Python scripts / Jupyter / Colab
                         UIT-VSFC Dataset
```

**Phân biệt công cụ:**

- **VS Code:** nơi làm việc chính, code Python/FastAPI, HTML/CSS/JS, Git/GitHub, chạy và kiểm thử dự án.
- **Google Colab hoặc Jupyter Notebook:** khám phá dữ liệu, huấn luyện và đánh giá các mô hình ML; notebook được lưu vào repository (không commit dữ liệu nhạy cảm).
- **Python + scikit-learn:** ML truyền thống, đủ cho phạm vi 3 tuần; không cần GPU.
- **FastAPI:** backend tích hợp mô hình và phục vụ giao diện.
- **Chart.js:** hiển thị Dashboard.
- **GitHub:** cộng tác qua nhánh và Pull Request.

**Lưu mô hình:** Mỗi nhiệm vụ xuất một **pipeline duy nhất** (tiền xử lý tương thích + vectorizer + classifier) dưới dạng `.joblib`; dự đoán phải sử dụng lại pipeline đã huấn luyện. Không dùng mã giả để thay thế suy luận thật. Chỉ tải `.joblib` từ nguồn do nhóm tin cậy.

### Cấu trúc thư mục mục tiêu

```text
student-feedback-ai/
├── .gitignore
├── README.md
├── requirements.txt
├── data/
│   ├── raw/                         # dataset tải về; không commit mặc định
│   └── processed/                   # train / validation / test
├── notebooks/
│   ├── 01_eda.ipynb
│   ├── 02_preprocessing.ipynb
│   ├── 03_sentiment_training.ipynb
│   └── 04_topic_training.ipynb
├── ml/
│   ├── preprocess.py                # chuẩn hóa/chuyển đổi dữ liệu
│   ├── train_sentiment.py
│   ├── train_topic.py
│   ├── evaluate.py
│   └── inference.py
├── models/                          # pipeline .joblib sau khi train
├── backend/
│   ├── __init__.py
│   ├── main.py                       # FastAPI + phục vụ frontend
│   ├── schemas.py                    # Pydantic schema
│   └── model_service.py             # load & predict từ pipelines
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── app.js
├── reports/
│   ├── metrics_sentiment.json
│   ├── metrics_topic.json
│   └── figures/                      # confusion matrices / charts
├── docs/
│   ├── API_CONTRACT.md
│   ├── TASKS.md
│   └── PRESENTATION_PLAN.md
└── tests/
    ├── test_api.py
    └── test_preprocess.py
```

**Lưu ý Git:** Git không lưu thư mục rỗng; tạo `.gitkeep` tại những thư mục chưa có file. Không commit `venv/.venv`, `.env`, cache, file mô hình lớn hoặc dữ liệu chưa được phép phân phối.

---

## 5. Hợp đồng API (thống nhất ngay trước khi chia việc)

Tất cả API dùng tiền tố `/api`, trả mã lỗi HTTP phù hợp và mô tả lỗi bằng JSON. Đặt tên key bằng tiếng Anh cho code, hiển thị nhãn tiếng Việt trên giao diện.

### `GET /api/health`

Khi đã có đủ hai mô hình và tải thành công:

```json
{
  "status": "ready",
  "models_loaded": { "sentiment": true, "topic": true }
}
```

Nếu chưa có model, API có thể trả `status: "setup_required"` và chỉ rõ model nào chưa sẵn sàng; tuyệt đối không báo đã sẵn sàng khi chưa tải được model.

### `POST /api/predict`

**Request** (`application/json`):

```json
{
  "text": "Giảng viên rất nhiệt tình."
}
```

**Response – định dạng mẫu (KHÔNG phải kết quả mô hình đã chạy):**

```json
{
  "text": "Giảng viên rất nhiệt tình.",
  "sentiment": { "code": 2, "label": "positive", "label_vi": "Tích cực" },
  "topic": { "code": 0, "label": "lecturer", "label_vi": "Giảng viên" }
}
```

- Khi chạy thật, các trường `code`, `label`, `label_vi` lấy từ dự đoán của model và bảng nhãn đã xác minh.
- Nếu dùng SVM chưa hiệu chuẩn xác suất, **không hiển thị phần trăm độ tin cậy như xác suất thật**.
- Nếu `text` trống, chỉ chứa khoảng trắng hoặc vượt quá độ dài hợp lý, trả lỗi có giải thích (ví dụ `422`).
- Nếu model chưa có hoặc lỗi tải model, trả lỗi rõ ràng (`503`) chứ không giả lập kết quả dự đoán.

### `POST /api/predict-batch`

- Input: `multipart/form-data` với trường `file` là CSV UTF-8 có cột bắt buộc `text`.
- Ràng buộc: tối đa **1.000 dòng** và **2 MB** ở phiên bản đầu; kiểm tra định dạng/thiếu cột/ô trống.
- Output: JSON gồm `total`, `results`, `summary` để frontend dựng bảng, biểu đồ và xuất CSV.

**Định dạng phản hồi ví dụ (chỉ mô tả cấu trúc):**

```json
{
  "total": 1,
  "results": [
    {
      "text": "Giảng viên rất nhiệt tình.",
      "sentiment": "positive",
      "topic": "lecturer"
    }
  ],
  "summary": {
    "sentiment": { "positive": 1, "neutral": 0, "negative": 0 },
    "topic": { "lecturer": 1, "training_program": 0, "facility": 0, "other": 0 }
  }
}
```

### `GET /api/metrics`

- Đọc các file `reports/metrics_sentiment.json` và `reports/metrics_topic.json` **do code đánh giá mô hình thực tế xuất ra**.
- Trả `available: false` nếu chưa có báo cáo, không sinh Accuracy/F1 giả.
- Mọi phiên bản cập nhật API cần sửa `docs/API_CONTRACT.md` và thông báo đến TV5, TV6.

---

## 6. Huấn luyện, đánh giá và quản lý kết quả

### Thí nghiệm ML tối thiểu

Thực hiện **riêng cho sentiment và topic**:

1. **Baseline:** Multinomial Naive Bayes + TF-IDF.
2. **Model 2:** Logistic Regression + TF-IDF.
3. **Model 3:** LinearSVC (SVM tuyến tính) + TF-IDF.
4. Dùng validation để so sánh và chọn mô hình/siêu tham số.
5. Đánh giá mô hình cuối cùng trên test; lưu metrics và confusion matrix.
6. Lưu pipeline tốt nhất: `models/sentiment_pipeline.joblib`, `models/topic_pipeline.joblib`.

**Không đặt mục tiêu Accuracy/F1 cố định trước khi có thực nghiệm.** Macro F1 là chỉ số ưu tiên vì dữ liệu có thể mất cân bằng.

### Đầu ra bắt buộc từ nhóm ML

- Notebook hoặc script chạy lại được từ dữ liệu thật.
- Thông tin cấu hình huấn luyện, phiên bản thư viện, chia tập, random seed (nếu có).
- Bảng so sánh ít nhất 3 thuật toán **cho mỗi nhiệm vụ**.
- Tập kết quả test, classification report, confusion matrix.
- Hai file pipeline đã train **và hướng dẫn tạo/tải model hợp lệ cho việc demo**.

### Nguyên tắc bảo mật và trung thực học thuật

- Không sử dụng phản hồi có thông tin cá nhân thật mà chưa được phép; không công khai nội dung nhạy cảm.
- Không tự gán Accuracy hoặc độ tin cậy ảo để làm đẹp Dashboard.
- Không trộn phản hồi tự nhập để demo vào tập test chính thức rồi báo là kết quả nghiên cứu.
- Không sử dụng chatbot/LLM thay cho các pipeline ML khi thuyết trình rằng hệ thống "tự huấn luyện".
- Khi thêm dataset bên ngoài, ghi nguồn, quyền sử dụng và sự khác biệt với UIT-VSFC.

---

## 7. Chạy dự án trên VS Code (Windows – PowerShell)

> **Các lệnh dưới đây là quy ước cần triển khai.** Khi mới có README, dự án **chưa chắc chạy được**; chỉ chạy sau khi Codex/nhóm tạo xong những file tương ứng.

### 7.1. Cài môi trường

Yêu cầu: **Python 3.11 hoặc 3.12**, Git, VS Code, kết nối Internet trong lần cài package.

```powershell
# Thực hiện trong thư mục gốc student-feedback-ai
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Nếu không bật được môi trường ảo trong PowerShell, có thể dùng Python trực tiếp qua `.\.venv\Scripts\python.exe` thay vì thay đổi chính sách bảo mật máy.

### 7.2. Chuẩn bị dataset

1. Tải UIT-VSFC từ nguồn phù hợp về `data/raw/`.
2. Xác thực danh sách file, schema và bảng mã nhãn.
3. Dùng notebook/script của TV2 chuyển dữ liệu thành ba file `data/processed/{train,validation,test}.csv`.
4. Không được làm mất ranh giới các split.

### 7.3. Huấn luyện mô hình

> **Trạng thái Giai đoạn A:** Hai lệnh dưới đây hiện là CLI khung, có `--help`
> và chủ động báo chưa triển khai khi chạy training. TV3/TV4 sẽ hoàn thiện trên
> dữ liệu thật; bản khung không tạo model hay báo cáo thực nghiệm.

```powershell
python -m ml.train_sentiment
python -m ml.train_topic
```

Sau khi huấn luyện thành công, trong `models/` phải có hai pipeline `.joblib` và trong `reports/` phải có báo cáo đánh giá tương ứng.

### 7.4. Chạy web app

```powershell
uvicorn backend.main:app --reload
```

- Truy cập giao diện: <http://127.0.0.1:8000/>
- Tài liệu API tự sinh: <http://127.0.0.1:8000/docs>
- Trạng thái hệ thống: <http://127.0.0.1:8000/api/health>

**Quy ước:** Backend sẽ phục vụ `frontend/index.html` và tài nguyên frontend trên **cùng origin** để không cần cấu hình CORS phức tạp ở giai đoạn đầu.

### 7.5. Kiểm thử

```powershell
pytest -q
```

Các test cần kiểm tra: văn bản trống, thiếu model, phản hồi hợp lệ, CSV thiếu cột `text`, file vượt giới hạn, và tính nhất quán của nhãn. Test API có thể mock dịch vụ model để test cấu trúc, nhưng **bài demo thực tế phải chạy model thật**.

---

## 8. Phân công 06 thành viên

| Vai trò | Nhánh Git dự kiến | Phạm vi chính | Đầu ra |
|---|---|---|---|
| **TV1 – Leader** | `main` (review/merge), nhánh riêng khi code | Quản lý tiến độ, kiến trúc, API contract, tích hợp, test, tài liệu, báo cáo | Repo chuẩn, bản tích hợp, demo cuối |
| **TV2 – Data & EDA** | `feature/data-preprocessing` | Dataset, thống kê, chuẩn hóa, mapping, xử lý train/val/test | `data/processed`, `ml/preprocess.py`, notebook EDA |
| **TV3 – Sentiment ML** | `feature/sentiment-model` | TF-IDF, 3 thuật toán cảm xúc, so sánh, đánh giá | `ml/train_sentiment.py`, pipeline cảm xúc, metrics |
| **TV4 – Topic ML** | `feature/topic-model` | 3 thuật toán chủ đề, so sánh, đánh giá | `ml/train_topic.py`, pipeline chủ đề, metrics |
| **TV5 – Backend** | `feature/backend-api` | FastAPI, model service, endpoint, validation, tests | Backend/API chạy và kết nối model |
| **TV6 – Frontend** | `feature/frontend-dashboard` | UI phân tích câu, CSV, Dashboard, gọi API | Website demo, biểu đồ và xuất CSV |

**Phối hợp bắt buộc:** TV2 chốt dữ liệu và nhãn với TV3/TV4; TV3/TV4 chốt đầu ra pipeline với TV5; TV5 thống nhất API với TV6. Leader phụ trách review PR, giải quyết xung đột và tích hợp.

### Quy trình GitHub

- `main`: nhánh ổn định, **không push trực tiếp tính năng chưa được review**.
- Mỗi thành viên tạo `feature/...` từ `main` mới nhất, commit nhỏ và push hằng ngày khi có tiến triển.
- Tạo **Pull Request (PR)** mô tả những gì đã làm, cách chạy/test, file thay đổi, vấn đề còn tồn tại.
- Leader review rồi merge; thông báo cho các thành viên khác cập nhật `main`.
- Leader dùng **GitHub Issues** để giao việc, theo dõi hạn và gắn người phụ trách.

Ví dụ:

```powershell
git switch main
git pull origin main
git switch -c feature/data-preprocessing
# Sau khi hoàn thành một phần công việc:
git add .
git commit -m "Add dataset preprocessing"
git push -u origin feature/data-preprocessing
# Mở GitHub và tạo Pull Request vào main
```

---

## 9. Lộ trình 03 tuần (21 ngày)

| Mốc | Thời gian | Công việc chính | Điều kiện nghiệm thu |
|---|---|---|---|
| **Tuần 1 – Nền tảng** | Ngày 1–7 | Tạo khung repo, chốt API; tải/xử lý dữ liệu; train baseline; dựng frontend/backend khung | Dữ liệu xử lý hợp lệ, ít nhất một model cảm xúc dự đoán thật; API/UI khung mở được |
| **Tuần 2 – AI + Tích hợp** | Ngày 8–14 | Hoàn tất hai nhiệm vụ ML, so sánh 3 thuật toán, kết nối `/api/predict` với model thật | Nhập phản hồi từ browser và nhận hai nhãn dự đoán thật; có metrics test |
| **Tuần 3 – Hoàn thiện** | Ngày 15–21 | CSV, Dashboard, lỗi giao diện, test, báo cáo, PowerPoint và diễn tập | Demo ổn định, code + tài liệu + báo cáo + PPT đầy đủ |

**Quy tắc ưu tiên khi trễ tiến độ:**

1. **P0:** model sentiment + topic thật, `/api/predict`, UI đơn câu, báo cáo chỉ số ML.
2. **P1:** CSV hàng loạt và Dashboard.
3. **P2:** giao diện nâng cao, cloud deployment, Deep Learning/PhoBERT.

Không để tính năng phụ làm hỏng P0.

---

## 10. Kịch bản demo bảo vệ cuối kỳ (25 phút + 10 phút hỏi đáp)

| Thời lượng | Người trình bày | Nội dung |
|---|---|---|
| 0–3 phút | TV1 | Bài toán thực tế, mục tiêu và kiến trúc |
| 3–7 phút | TV2 | Dataset UIT-VSFC, EDA, tiền xử lý và nhãn |
| 7–12 phút | TV3 | TF-IDF và phương pháp ML phân loại cảm xúc |
| 12–16 phút | TV4 | Phân loại chủ đề, bảng so sánh và đánh giá |
| 16–22 phút | TV5 + TV6 | Live demo website: một câu mới → CSV → Dashboard |
| 22–25 phút | TV1 | Kết luận, hạn chế, hướng phát triển |
| 25–35 phút | Cả nhóm | Trả lời câu hỏi của giảng viên |

**Bộ minh chứng cần mang theo:** notebook/script training, file model, kết quả đánh giá test, sơ đồ kiến trúc, báo cáo Word/PDF, slide PPT và URL hoặc localhost của web demo. Chuẩn bị phương án demo offline nếu Internet không ổn định.

### Sản phẩm bàn giao cuối cùng

- [ ] Code nghiên cứu dữ liệu + huấn luyện và đánh giá ML.
- [ ] Hai pipeline sentiment/topic hoạt động thực sự.
- [ ] Bảng so sánh thuật toán và Confusion Matrix, có nguồn từ thực nghiệm.
- [ ] Web phân tích một phản hồi, dùng đúng model đã train.
- [ ] Upload CSV hàng loạt + biểu đồ Dashboard (mục tiêu P1).
- [ ] `README.md`, tài liệu API, hướng dẫn chạy và GitHub PR rõ ràng.
- [ ] Báo cáo `.docx` / `.pdf`, PowerPoint 20–30 phút và Q&A 10 phút.

---

## 11. Hướng dẫn dành cho Codex trong VS Code

> **Mục đích:** Giúp Codex tạo **bộ khung chung của repository** nhanh chóng để Leader phân công 5 thành viên cùng làm. **Không tự làm hết phần việc của nhóm trong một lần** nếu Leader chưa yêu cầu.

### Giai đoạn A – Leader yêu cầu Codex tạo khung (ưu tiên ngay)

1. Đọc toàn bộ `README.md` và **không xóa** `.gitignore`, lịch sử Git, hoặc thay đổi nhánh hiện tại ngoài yêu cầu.
2. Tạo thư mục/file theo **Mục 4**, file `.gitkeep` cho thư mục rỗng; tạo `requirements.txt`, thêm những rule `.gitignore` cần thiết.
3. Tạo một giao diện web tiếng Việt cơ bản gồm 4 tab/trang ở **Mục 2**; dùng **HTML/CSS/JavaScript thuần**, không bắt buộc React.
4. Tạo FastAPI tối thiểu đúng hợp đồng ở **Mục 5**; `/api/health` phải báo trạng thái model **thực**. Các endpoint suy luận chỉ trả kết quả khi có mô hình hợp lệ; nếu chưa có, trả `503` với thông báo dễ hiểu, **không tạo dự đoán giả**.
5. Tạo service tải hai `.joblib` theo đường dẫn cấu hình; kiểm tra file tồn tại, và handle lỗi thân thiện.
6. Tạo mã training dạng **khung hợp lệ** (`ml/`) với các hàm/CLI rõ ràng để TV2, TV3, TV4 tiếp tục; không bịa dataset hay kết quả đánh giá.
7. Tạo `docs/API_CONTRACT.md`, `docs/TASKS.md`, `docs/PRESENTATION_PLAN.md`, test tối thiểu và hướng dẫn chạy cập nhật.
8. Chạy các kiểm tra khả thi, **nói rõ test nào đã chạy, lỗi nào chưa sửa và phần nào cần dữ liệu/model thật**.
9. Không tự động commit hoặc push nếu Leader chưa yêu cầu.

### Giai đoạn B – Các thành viên phát triển trên nhánh riêng

- TV2 làm dữ liệu/tiền xử lý; TV3/TV4 hoàn thiện training & evaluation; TV5 viết API production; TV6 hoàn thiện frontend/dashboard.
- Mỗi nhánh chỉ sửa những vùng code thuộc phạm vi của mình, phối hợp qua API contract.
- Không viết đè code nhánh khác hoặc tự merge vào `main`.

### Tiêu chí chấp nhận của bản khung Codex

- [ ] Cấu trúc repo đúng Mục 4; lệnh cài môi trường hoạt động.
- [ ] `uvicorn backend.main:app --reload` khởi chạy thành công.
- [ ] Website mở tại `http://127.0.0.1:8000/`.
- [ ] Trang `/docs` thể hiện đúng endpoint.
- [ ] Nếu chưa có model, web/backend **không** nói AI đã dự đoán xong.
- [ ] `pytest -q` chạy các test khung (mock khi thích hợp).
- [ ] README/tài liệu nêu chính xác phần đã triển khai và phần chưa triển khai.

---

## 12. Tài liệu tham khảo

1. Nguyen, K. V., Nguyen, V. D., Nguyen, P. X. V., Truong, T. T. H., & Nguyen, N. L. T. (2018). *UIT-VSFC: Vietnamese Students’ Feedback Corpus for Sentiment Analysis*. 10th International Conference on Knowledge and Systems Engineering (KSE). DOI: [10.1109/KSE.2018.8573337](https://doi.org/10.1109/KSE.2018.8573337).
2. UIT-VSFC project: <https://github.com/kietnv/uit-vsfc>
3. UIT NLP Group datasets: <https://sites.google.com/uit.edu.vn/uit-nlp/datasets>
4. [scikit-learn documentation](https://scikit-learn.org/stable/)
5. [FastAPI documentation](https://fastapi.tiangolo.com/)
6. [Chart.js documentation](https://www.chartjs.org/docs/latest/)

---

**Tóm tắt định hướng:** Dự án ưu tiên **tính đúng đắn của phần AI, kết quả đánh giá kiểm chứng được và demo website hoạt động**. Với quỹ thời gian 3 tuần, hoàn thành chức năng cốt lõi và tích hợp ổn định quan trọng hơn phát triển nhiều tính năng nâng cao.

---

## 13. Trạng thái bộ khung Giai đoạn A (18/10/2026)

Đã tạo cấu trúc Mục 4, môi trường `.venv`, dependencies, backend bốn API,
frontend bốn tab tiếng Việt, khung ML/CLI, bốn notebook chưa có output và tài
liệu bàn giao. Backend phục vụ frontend trên cùng origin. Khi chưa có model:
health báo `setup_required`, endpoint suy luận trả `503`; đánh giá ML báo
`available: false`. Không có dữ liệu dự đoán hoặc Accuracy/F1 giả trong app.

### Chạy bản khung hiện tại

```powershell
# Không cần kích hoạt môi trường nếu dùng đường dẫn Python trực tiếp
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --reload
.\.venv\Scripts\python.exe -m pytest -q
```

Chạy server và pytest ở hai terminal riêng. Trên máy đã kiểm thử, cổng `8000`
đang được tiến trình khác sử dụng, nên ứng dụng đã được kiểm tra bằng:

```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --reload --port 8765
```

Khi dùng lệnh này, mở <http://127.0.0.1:8765/> và <http://127.0.0.1:8765/docs>.
Không cần dừng tiến trình khác đang chiếm cổng 8000.

**Môi trường kiểm chứng:** Windows, CPython **3.13.3** hiện có trên máy;
chưa kiểm chứng Python 3.11/3.12 được khuyến nghị ở Mục 7.1. Phiên bản các
dependency trực tiếp được ghi tại `requirements-tested.txt`; đây không phải
lock toàn bộ dependency bắc cầu. `requirements.txt` cho phép pip chọn phiên
bản tương thích với interpreter của từng máy. Nhóm ML/backend cần thống nhất
phiên bản thực tế khi huấn luyện và tải model.

**Kết quả đã chạy:** 43 test pytest đạt; HTTP smoke và Edge headless kiểm tra
bốn tab, lỗi thiếu model, CSV sai, trạng thái chưa có dữ liệu, bàn phím và
desktop/mobile đều đạt. Có một cảnh báo deprecation từ Starlette TestClient;
chi tiết và cách chạy lại xem [docs/TESTING.md](docs/TESTING.md).

**Chưa thực hiện:** tải/xác minh UIT-VSFC và mapping gốc, huấn luyện, so sánh
thuật toán, đánh giá test, tạo pipeline thật, kiểm thử suy luận thật và kiểm
thử giao diện với kết quả model thật. Dashboard có biểu đồ thanh cơ bản bằng
HTML/CSS; TV6 tiếp tục Chart.js, bảng so sánh và hình Confusion Matrix. Bản
khung không bao gồm báo cáo Word/PDF, slide hoặc triển khai cloud.

Tài liệu để Leader tiếp tục phân công:

- [Hợp đồng API và cấu hình model](docs/API_CONTRACT.md).
- [Phạm vi TV1–TV6 và mốc 21 ngày](docs/TASKS.md).
- [Kế hoạch thuyết trình](docs/PRESENTATION_PLAN.md).
- [Kiểm thử, giới hạn và checklist tích hợp](docs/TESTING.md).

Các file `reports/metrics_*.json` ban đầu chỉ đánh dấu chưa đánh giá. Khi có
model thật, đặt hai pipeline theo mặc định trong `models/` hoặc cấu hình
`SENTIMENT_MODEL_PATH`, `TOPIC_MODEL_PATH` trước khi chạy server. Chỉ tải file
joblib do nhóm tin cậy cung cấp; khởi động lại sau khi thay model.
