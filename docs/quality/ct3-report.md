# CT3 — Kết hợp đặc trưng từ + ký tự, 2026-10-31

Đã triển khai công cụ và chạy sáu cấu hình (12 lần fit). Đây là thí nghiệm
nghiên cứu local; **hai model demo trong models/ chưa được thay**. Không triển
khai CT4–CT5 hoặc Phase 6. Hướng từ + ký tự do người dùng xác nhận; các giá trị
tham số cụ thể bên dưới là lựa chọn triển khai được đóng băng trước đo.

## Trả lời câu hỏi “chính xác hơn bao nhiêu phần trăm?”

Trên cùng **1.583 câu validation**, CT3 cải thiện khả năng cân bằng giữa các lớp
ở nhiệm vụ cảm xúc, nhưng **chưa tăng tỷ lệ trả đúng tổng thể**. Chọn từng task
theo Macro F1 như protocol CT1 cho bộ ghép nghiên cứu: cảm xúc CT3 char_2_none,
chủ đề CT2 sqrt_balanced. Chủ đề CT3 chưa vượt CT2 theo tiêu chí đó.

| Chỉ số validation | Ban đầu | CT2 | Ghép tốt nhất đến CT3 | So ban đầu (điểm %) |
| --- | ---: | ---: | ---: | ---: |
| Accuracy cảm xúc | 91,4719% | 91,2824% | 91,0929% | −0,3790 |
| Macro F1 cảm xúc | 75,2966% | 77,5003% | 78,9855% | +3,6889 |
| Accuracy chủ đề | 87,9975% | 87,8080% | 87,8080% | −0,1895 |
| Macro F1 chủ đề | 75,4173% | 76,8397% | 76,8397% | +1,4224 |
| Cả hai nhãn cùng đúng | 81,8699% | 81,7435% | 81,5540% | −0,3159 |

Hai nhãn cùng đúng: ban đầu **1296/1583**, CT2 **1294/1583**, ghép đến CT3
**1291/1583**. So ban đầu giảm 5 câu đúng, **0,3159 điểm phần trăm**, tương
đương **giảm tương đối 0,3858%**. So CT2 giảm 3 câu, 0,1895 điểm phần trăm.
Macro F1 cảm xúc tăng 3,6889 điểm phần trăm (tăng tương đối 4,8991%), không
được diễn đạt thành “trả lời đúng hơn 4,8991%”.

Nếu chỉ ghép hai ứng viên mới của CT3 (cảm xúc char_2_none, chủ đề
char_0.5_ct2): Accuracy chủ đề 87,4289%, Macro F1 chủ đề 76,8175%; cả hai đúng
**1286/1583 = 81,2382%**, giảm **0,6317 điểm phần trăm** (−0,7716% tương đối)
so ban đầu. Vì vậy bảng chính ghi rõ chủ đề giữ CT2, không gán lợi ích CT2
thành thành quả mới của CT3.

**Ứng dụng đang phục vụ giữ nguyên baseline: mức thay đổi chất lượng triển
khai là 0%.** Số trên là phép đo ứng viên nghiên cứu trên validation đã được
dùng nhiều lần, chưa chứng minh độ chính xác trên phản hồi mới độc lập.

## Phương pháp và cấu hình

- Giữ UIT-VSFC train 11426 / validation 1583 và normalizer NFC/lower/whitespace.
- FeatureUnion: word TF-IDF baseline unigram/bigram và char_wb TF-IDF 3–5 ký tự;
  min_df=2, sublinear_tf=True, mỗi nhánh norm=l2, không strip dấu. Không thêm
  chuẩn hóa ở loader/API/UI. Không L2 lại sau khi ghép, nên trọng số nhánh cũng
  thay đổi độ lớn vector mà LinearSVC nhận; không coi đây là phép cô lập chỉ một
  yếu tố ngôn ngữ.
- Trọng số word=1, char=0.5/1/2; mỗi mức thử none và ct2. ct2 dùng balanced cho
  sentiment, sqrt_balanced cho topic, tính trọng số chỉ từ nhãn train.
- LinearSVC C=1, dual=auto, max_iter=5000, random_state=42. Không dò thêm C hay
  chọn thêm cấu hình sau khi xem điểm.
- Fit chỉ train; không suy luận test trong CT3. Xếp từng task bằng Macro F1
  validation rồi Accuracy trong các dải 1e-6 tính từ cực đại cố định; hòa giữ
  original → CT2 → thứ tự cấu hình khai báo. Known cases không tham gia chọn.
- Toàn bộ 12 lần fit thật không có cảnh báo. Môi trường/nguồn được ràng buộc qua
  CT2 receipt → CT1 receipt và snapshot, runner hash, payload hash.

## Tất cả cấu hình mới

| Char weight / weighting | Accuracy cảm xúc | Macro F1 cảm xúc | Accuracy chủ đề | Macro F1 chủ đề |
| --- | ---: | ---: | ---: | ---: |
| 0.5 / none | 91,4719% | 76,5377% | 87,7448% | 75,8953% |
| 0.5 / ct2 | 91,2192% | 77,3625% | 87,4289% | 76,8175% |
| 1 / none | 91,4087% | 78,0481% | 87,4921% | 76,3488% |
| 1 / ct2 | 90,9665% | 77,8145% | 86,6709% | 75,7781% |
| 2 / none | 91,0929% | 78,9855% | 87,0499% | 76,0965% |
| 2 / ct2 | 90,5875% | 77,3278% | 86,1023% | 74,6627% |

## Lợi ích và tổn thất

Sentiment char_2_none so baseline: **23 ca sai thành đúng, 29 ca đúng thành
sai** trên validation. Neutral Recall **27,3973% → 43,8356%** (+16,4384 điểm %),
F1 **39,6040% → 51,6129%** (+12,0089 điểm %); Precision giảm
**71,4286% → 62,7451%** (−8,6835 điểm %).

| Lớp cảm xúc | Δ Precision (điểm %) | Δ Recall (điểm %) | Δ F1 (điểm %) |
| --- | ---: | ---: | ---: |
| negative | +0,4060 | −1,1348 | −0,3440 |
| neutral | −8,6835 | +16,4384 | +12,0089 |
| positive | +0,0229 | −1,2422 | −0,5984 |

Topic CT3 char_0.5_ct2 so baseline: **15 ca sai thành đúng, 24 ca đúng thành
sai**. Other Recall 41,0526%, F1 49,0566%; đổi lại Accuracy giảm. Bộ ghép giữ
Topic CT2 có 18 ca sai thành đúng, 21 ca đúng thành sai; đây là kết quả CT2 cũ.
JSON lưu đầy đủ per-class, confusion matrix, IDs và mọi nhãn thay đổi, bao gồm
sai sang nhãn sai khác, so cả original và CT2.

## 39 ca chẩn đoán đã biết

| Có nhãn kỳ vọng | Ban đầu | CT2 | Ghép đến CT3 |
| --- | ---: | ---: | ---: |
| Cảm xúc | 21/30 = 70% | 21/30 = 70% | 25/30 = 83,3333% |
| Chủ đề | 29/29 = 100% | 28/29 = 96,5517% | 28/29 = 96,5517% |
| Đủ hai kỳ vọng, cả hai đúng | 18/25 = 72% | 18/25 = 72% | 22/25 = 88% |

Tăng 13,3333 điểm % cảm xúc và 16 điểm % joint **chỉ trên các ca chẩn đoán có
nhãn đề xuất**. Nhãn do trợ lý đề xuất, chưa được rà độc lập; null không tính
đúng/sai. Không suy rộng những điểm này thành mức cải thiện toàn hệ thống.
Các ca cảm xúc mới đúng: known-006, 013, 022, 023; không có ca cảm xúc đã đúng
thành sai trong mẫu nhỏ này. Chủ đề known-019 vẫn hồi quy từ CT2. Việc thêm ký
tự chưa chứng minh đã xử lý đầy đủ phủ định, không dấu, emoji hay ngoài miền.

## Tái lập và kiểm chứng

Run chính thức: `.local-tools/ct3-word-char/run-1/`. Runner:
`reports/ct3_word_char.py`; tests: `tests/test_ct3_word_char.py`.

```powershell
./.venv/Scripts/python.exe -B reports/ct3_word_char.py verify
```

Replay không fit: kiểm mọi checksum, nguồn/runtime CT1/CT2, cấu hình hiệu lực,
metadata/readiness, dự đoán/metrics/percent/delta/xếp hạng và bộ ghép tải lại.
Cả word và char vocabulary/IDF được đối chiếu trực tiếp với document frequency
train; validation/known cases không được đưa vào vocabulary. Tạo run mới bằng
CLI run --output dưới .local-tools/ct3-word-char/<tên-mới>; công cụ từ chối đường
dẫn demo, output đã tồn tại và đường dẫn chồng lên control. Không đổi
SFAI_MODEL_DIR để tự triển khai ứng viên.

Logs và bản sao config/results/summary/receipt ở `reports/evidence/ct3/`.
Snapshot/model/dataset vẫn local, quyền phân phối nguồn vẫn unknown. Chi tiết
suite cuối và review được ghi trong README bằng chứng và ledger CT3.

Kiểm chứng cuối: **281 tests đạt, 0 skip, 14 cảnh báo thư viện đã biết** trong
197,07 giây; pip check đạt. Replay tiến trình mới đạt đủ 12 artifact và bộ ghép;
49 đầu vào CT1, 19 payload CT2 và hash runner CT2 giữ nguyên. Review độc lập
không có Critical/Important. Còn một minor: replay chưa kiểm giá trị mô tả
schema_version/promotion ở receipt; model/metrics/payload/selection vẫn được
kiểm. Không coi replay là chứng nhận mọi trường receipt hoặc tính xác thực
ngoài hệ thống local. Chi tiết: `reports/evidence/ct3/review.md`.

**Đề xuất:** giữ baseline phục vụ khi ưu tiên tỷ lệ trả đúng tổng thể. Lưu ứng
viên cảm xúc CT3 để cân nhắc nếu ưu tiên neutral/Macro F1; cần đánh giá mới độc
lập và quyết định rõ về tổn thất trước khi thay model. Không tự chọn lại theo
điểm test hay vá nhãn theo 39 câu đã biết.
