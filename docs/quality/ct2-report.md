# CT2 — Thử trọng số lớp, 2026-10-31

CT2 so sánh các ứng viên nghiên cứu với baseline-v2 của CT1. Hai artifact đang
phục vụ trong `models/` giữ nguyên. Không triển khai CT3–CT5 hoặc Phase 6.

## Phương pháp

Giữ nguyên UIT-VSFC train 11426 và validation 1583 câu, normalizer, TF-IDF,
LinearSVC C=1, max_iter=5000, dual=auto và random_state=42. Clone pipeline để
fit lại **chỉ train**, không mang trạng thái fitted từ baseline sang ứng viên.
Vocabulary và IDF sau fit phải khớp baseline đã xác minh train-only ở Phase 2.

Ba cấu hình cố định trước khi đo, áp dụng cho từng task:

- `sqrt_balanced`: căn bậc hai của N/(K × số mẫu lớp).
- `balanced`: N/(K × số mẫu lớp).
- `minority_x2`: neutral/other có trọng số 2, các lớp còn lại là 1.

N, K và số mẫu lớp đều lấy từ train. Trọng số không được suy ra từ validation
hoặc test. Không đổi C, resample, sửa nhãn hay thêm dữ liệu. Mỗi ứng viên lưu
trọng số thực, thời gian, cảnh báo và phiên bản môi trường. Tổng cộng 6 lần fit.
Không có cảnh báo trong sáu lần fit thật.

Xếp hạng từng task: lấy Macro F1 validation lớn nhất làm mốc cố định, giữ
những ứng viên cách mốc không quá 1e-6; trong nhóm này lấy Accuracy lớn nhất
làm mốc cố định và giữ những bản cách không quá 1e-6. Còn hòa giữ baseline rồi
thứ tự sqrt_balanced/balanced/minority_x2. Không so hòa dây chuyền từng cặp. Đây là
thứ hạng nghiên cứu; không phải quyết định thay model demo. 39 ca đã biết
chỉ dùng chẩn đoán/hồi quy; không chọn cấu hình theo chúng. Không chạy suy luận
test trong runner CT2; điểm test lịch sử không phải phép đánh giá độc lập mới.

## Kết quả validation

| Task | Cấu hình | Accuracy | Macro F1 | Δ Accuracy (điểm %) | Δ Macro F1 (điểm %) |
| --- | --- | ---: | ---: | ---: | ---: |
| Sentiment | baseline | 91,4719% | 75,2966% | 0 | 0 |
| Sentiment | sqrt_balanced | 91,3455% | 75,9336% | −0,1263 | +0,6370 |
| Sentiment | balanced | 91,2824% | 77,5003% | −0,1895 | +2,2037 |
| Sentiment | minority_x2 | 91,2824% | 74,9305% | −0,1895 | −0,3661 |
| Topic | baseline | 87,9975% | 75,4173% | 0 | 0 |
| Topic | sqrt_balanced | 87,8080% | 76,8397% | −0,1895 | +1,4224 |
| Topic | balanced | 86,7340% | 76,2587% | −1,2634 | +0,8414 |
| Topic | minority_x2 | 87,9975% | 76,0656% | 0 | +0,6483 |

Ứng viên đứng đầu: **Sentiment balanced**, **Topic sqrt_balanced**. Ghép hai
ứng viên chỉ để khảo sát: hai nhãn cùng đúng 1294/1583 = 81,7435%, thấp hơn
baseline 1296/1583 = 81,8699%. Tăng Macro F1 từng task không bảo đảm tăng tỷ lệ
cả hai nhãn cùng đúng.

## Lợi ích và tổn thất từng lớp

Các delta dưới tính bằng **điểm phần trăm**, trên cùng validation; support giữ nguyên.

| Task/lớp | Δ Precision | Δ Recall | Δ F1 |
| --- | ---: | ---: | ---: |
| Sentiment negative | +0,9292 | −0,9929 | −0,0083 |
| Sentiment neutral | −18,7970 | +13,6986 | +6,5499 |
| Sentiment positive | +0,8588 | −0,7453 | +0,0695 |
| Topic lecturer | +1,3257 | −1,4770 | −0,0583 |
| Topic curriculum | −1,1279 | +1,4981 | +0,0638 |
| Topic facility | −1,2520 | 0 | −0,6393 |
| Topic other | −9,8311 | +10,5263 | +6,3235 |

Neutral Recall tăng 27,3973% → 41,0959%, F1 tăng 39,6040% → 46,1538%, nhưng
Precision giảm 71,4286% → 52,6316%. Other Recall tăng 29,4737% → 40%, F1 tăng
41,1765% → 47,5%, nhưng Precision giảm 68,2927% → 58,4615%.
Macro Precision cũng giảm: Sentiment −5,6697 điểm %, Topic −2,7213 điểm %.

So với baseline, validation Sentiment có **10 ca sai thành đúng, 13 ca đúng
thành sai**; Topic có **18 ca sai thành đúng, 21 ca đúng thành sai**. JSON lưu
đủ ID, nhãn trước/sau, cả các lần sai sang một nhãn sai khác; không chỉ lưu tổng.

## 39 ca đã biết

Nhãn kỳ vọng vẫn do trợ lý đề xuất, chưa có người rà độc lập. Null không tính
vào mẫu số; không ép câu thiếu ngữ cảnh hoặc ngoài miền thành neutral/other.

| Phép chấm | Baseline | Ghép ứng viên đứng đầu |
| --- | ---: | ---: |
| Sentiment có kỳ vọng | 21/30 | 21/30 |
| Topic có kỳ vọng | 29/29 | 28/29 |
| Đủ hai kỳ vọng, cả hai đúng | 18/25 | 18/25 |

`known-019` đổi Sentiment negative → neutral nhưng kỳ vọng positive, nên vẫn
sai; Topic lecturer → other là một ca đúng thành sai. Một số câu không có kỳ
vọng đổi nhãn, được ghi lại nhưng không gọi là cải thiện. Trọng số lớp chưa
chứng minh đã giải quyết phủ định, không dấu, emoji, vector 0 hoặc ngoài miền.

## Artifact và tái lập

Chạy từ `.local-tools/integration-p0` bằng môi trường khóa hiện có:

```powershell
./.venv/Scripts/python.exe -B reports/ct2_class_weights.py verify
```

Run chính thức tại `.local-tools/ct2-class-weights/run-2/`:

- `config.json`: cấu hình và counts trước fit.
- `candidates/<strategy>/`: hai pipeline + metadata hợp đồng 1.0 mỗi cấu hình.
- `research-selected/`: ghép hai ứng viên đứng đầu, chưa đưa vào demo.
- `results.json`: đủ metrics, matrix, nhãn từng câu, delta, hồi quy và known-case groups.
- `receipt.json`: runtime, hash runner, baseline receipt và mọi payload.
- `summary.md`: bảng so sánh tự sinh từ kết quả.

CLI `run` từ chối output đã có và output ngoài nhánh thư mục nghiên cứu. Muốn
chạy lại chọn `--output .local-tools/ct2-class-weights/<tên-run-mới>`; không ghi đè
run-2. `verify` không fit: kiểm checksum, runtime, tham số/vocabulary/IDF, metadata,
readiness qua ModelService, dự đoán/metrics/delta/xếp hạng và bộ ghép tải lại.
Không đặt `SFAI_MODEL_DIR` sang thư mục này để tự triển khai.

Run-1 được giữ làm lịch sử review, cùng runner cũ trong
`.local-tools/ct2-class-weights/runner-run-1.py`. Review phát hiện lỗi so hòa
dây chuyền ở trường hợp điểm sát nhau; regression test thất bại trước sửa,
đạt sau sửa. Run-2 dùng runner đã sửa và receipt mới; các kết quả thực nghiệm
được đối chiếu với run-1, không thay số liệu để cải thiện kết luận.

Kết quả và log kiểm chứng ở `reports/evidence/ct2/`. Dữ liệu/model/snapshot chỉ
lưu local; trạng thái quyền phân phối nguồn vẫn unknown. Bộ đánh giá mới cuối
kỳ chưa được thu thập/rà nhãn độc lập; validation có thể lạc quan do thử cấu hình.

Kiểm chứng cuối: **261 tests đạt, không skip**, 14 cảnh báo thư viện đã biết;
`pip check` đạt. Replay tiến trình mới kiểm đủ sáu artifact và bộ ghép đứng đầu.
Replay CT1 cuối khớp đủ 49 đầu vào và kết quả cũ. Review độc lập phát hiện một
lỗi xếp hạng ở ngưỡng hòa; đã tái hiện bằng test thất bại, sửa và chạy lại suite
đạt. Không còn phát hiện Critical/Important/Minor chưa xử lý trong phần CT2.

**Đề xuất:** giữ baseline đang phục vụ, dùng hai ứng viên và các tổn thất trên
làm mốc nghiên cứu cho CT tiếp theo. Chỉ chọn thay bản demo sau khi cân nhắc
đánh đổi và đánh giá phù hợp; CT2 không tự nhận là đã tăng chất lượng độc lập.
