# Additional trained baselines for reporting

Four pipelines: nb (MultinomialNB) and logistic_regression for sentiment and topic.
Each joblib contains fitted TF-IDF and classifier and accepts raw text.
Use the project environment with student_feedback/src on PYTHONPATH.

Fit: original train only, 11,426 rows, project baseline parameters, no augmentation.
Evaluation: validation only. Test was not used. CSV/JSON contain measured results.
Metadata records parameters, data hashes, versions, artifact hash and training time.
Every saved model was reloaded and reproduced all validation predictions.

Original sentiment_pipeline.joblib and topic_pipeline.joblib remain serving Linear SVM artifacts.
Serving manifests and original artifacts are unchanged; new files are for reporting only.
Existing SVM uses experimental features/augmentation: these fresh baselines are not a controlled same-feature comparison or recovered historical candidates.

## Thư mục theo thuật toán

- `linear_svm/`: bản sao mô hình Linear SVM đã chọn, gồm cảm xúc và chủ đề.
- `multinomial_naive_bayes/`: mô hình Naive Bayes cho cảm xúc và chủ đề.
- `logistic_regression/`: mô hình Logistic Regression cho cảm xúc và chủ đề.

Các file SVM ở thư mục gốc vẫn phục vụ web theo manifest hiện tại. Thư mục linear_svm là bản sao phục vụ báo cáo tại thời điểm sắp xếp, không tự đồng bộ khi huấn luyện lại. Các file baseline_models_validation.csv/json là kết quả chung cho hai thuật toán baseline.
