# Kiến trúc

```text
src/feedback_ai/
  api/         app factory (create_app), schemas, routes/batch.py  → /api/health, /api/v3/*
  services/    AnalysisService (phân tích 1 phản hồi), aspects (cảm xúc theo chủ đề)
  inference/   bundle (manifest + checksum), frozen/model_loader (nạp bundle), detector + ontology (luật bằng chứng),
               signals/policy (selective prediction), sentiment/topic (suy luận)
  io/          imports (CSV/XLSX → bảng), exports (workbook 3 sheet)
  data/        loader (UIT-VSFC), preprocessing (normalize_text), workflow (import/validate/eda/acquire)
  training/    sentiment, topic, workflow (train/evaluate), experiments/ (CT1–CT5)
  evaluation/  metrics, sentiment, topic (so sánh, confusion matrix)
  common/      hashing, json_io, labels
  resources/   rules.json (đóng gói cùng package)    web/  HTML/CSS/JS + mau-phan-hoi.xlsx
src/ml, src/reports   shim tối thiểu để pickle cũ tìm thấy `ml.preprocessing.normalize_text` và `reports.ct4_augmentation`
```

## Nguyên tắc

- **Một project root.** `Settings.from_root(root)` cho `data/`, `artifacts/`, `outputs/`. Không phụ thuộc cwd, không tìm repo cha.
- **Serving ≠ training.** Server chỉ đọc `artifacts/serving` (bundle đóng băng + `manifest.json` với checksum SHA-256 từng file).
  Huấn luyện/thí nghiệm ghi vào thư mục mới, bị từ chối nếu thư mục đã tồn tại hoặc nằm trong `serving`.
- **Thiếu model vẫn chạy.** App factory nạp một lần; lỗi nạp chỉ làm `ready=false` và `predict` trả 503, giao diện vẫn phục vụ.
- **Shim chỉ để giải mã pickle.** Mã mới import `feedback_ai`; shim không phải kiến trúc chính.
- **Web:** 3 tab (một phản hồi / dán danh sách / nhập file), phiên làm việc nằm trong trình duyệt, gọi `analyze-row` tuần tự để có tiến trình
  và cô lập lỗi từng dòng; xuất Excel từ kết quả phiên. Không có server-side persistence.

## Hợp đồng ứng dụng (giữ nguyên bản cũ)

`/api/v3/predict` → `{contract_version:"3.0", sentiment, topic[, topics]}`; 422 `INVALID_INPUT`, 503 `MODEL_NOT_READY`, 500 `INFERENCE_ERROR`.
Giới hạn: 5000 code point/phản hồi, 500 dòng/đợt, 5 MiB/file, XLSX giải nén ≤ 25 MiB. Đối chiếu hành vi bản cũ: `tests/parity`.
