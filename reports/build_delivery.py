"""Build editable delivery documents from frozen metrics and actual evidence."""
import json
from pathlib import Path
from docx import Document
from docx.shared import Inches, Pt
from pptx import Presentation
from pptx.util import Inches as SlideInches, Pt as SlidePt

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'reports'


def read_json(path):
    return json.loads((ROOT / path).read_text(encoding='utf-8'))


def main():
    doc = Document()
    doc.styles['Normal'].font.name = 'Calibri'
    doc.styles['Normal'].font.size = Pt(11)
    doc.add_heading('Student Feedback AI', 0)
    doc.add_paragraph('Cơ sở và Ứng dụng Trí tuệ nhân tạo — Báo cáo P0, 29/10/2026')
    doc.add_paragraph('Bản kỹ thuật nội bộ. Leader bổ sung tên nhóm, tên thành viên và thông tin nộp bài trước khi nộp. Quyền sử dụng/phân phối UIT-VSFC và model dẫn xuất chưa được xác nhận; tài liệu này không chứng nhận quyền công bố.')
    sections = [
        ('1. Goal and Motivation', [
            'Mục tiêu là hỗ trợ đọc phản hồi sinh viên tiếng Việt thông qua một nhãn cảm xúc và một nhãn chủ đề cho mỗi câu. Sản phẩm là demo học phần, không thay thế đánh giá của con người.',
            'P0 gồm dữ liệu và EDA, so sánh ba thuật toán cho mỗi nhiệm vụ, lưu/tải pipeline, API và giao diện phân tích một câu. CSV, export và Dashboard thuộc P1 chưa triển khai. Không đặt thêm ngưỡng Accuracy/F1 đạt hoặc SLA ngoài đặc tả đã duyệt.'
        ]),
        ('2. Background', [
            'TF-IDF biểu diễn văn bản bằng trọng số từ/ngữ đoạn dựa trên tần suất trong câu và độ phổ biến trong tập huấn luyện. Bigram giữ một phần quan hệ từ liền kề nhưng không biểu diễn đầy đủ ngữ cảnh hoặc ý mỉa mai.',
            'Multinomial Naive Bayes là baseline xác suất cho đặc trưng không âm; Logistic Regression học ranh giới tuyến tính; Linear SVM tối ưu biên phân tách tuyến tính. LinearSVC không cung cấp xác suất đã hiệu chuẩn, vì vậy UI không hiển thị confidence.',
            'Accuracy đo tỷ lệ đúng toàn bộ; Macro Precision/Recall/F1 lấy trung bình ngang nhau giữa các lớp. Với dữ liệu mất cân bằng, cần đọc cả macro và chỉ số từng lớp, không dùng riêng Accuracy.'
        ]),
        ('3. Proposed Model', [
            'Hai pipeline độc lập: raw text → normalize_text → TF-IDF → classifier. Sentiment có negative/neutral/positive; Topic có lecturer/curriculum/facility/other. Hai pipeline trả nhãn chuỗi chuẩn.',
            'FastAPI phục vụ HTML/CSS/JavaScript và API cùng origin. GET /api/health phân biệt live/ready; POST /api/predict chỉ trả hai nhãn khi cả hai artifact hợp lệ. ModelService kiểm metadata, SHA-256, phiên bản Python/gói và classes trước suy luận.',
            'UI đếm Unicode code point, tối đa 5000, một request tại một thời điểm và timeout 10000 ms. Lỗi input/model/inference lần lượt dùng 422/503/500 theo hợp đồng. Nội dung nhập được giữ khi gặp lỗi.'
        ]),
        ('4. Technique / Method', [
            'UIT-VSFC: train 11426, validation 1583, test 3166. Bản nguồn được nhận diện bằng revision và SHA-256 từng file trong reports/data/source.json. Mã số nguồn chỉ ánh xạ một lần tại loader; raw text và thứ tự được giữ nguyên.',
            'Chuẩn hóa Unicode NFC, lowercase, gộp whitespace và strip nằm trong pipeline. Giữ dấu tiếng Việt, phủ định, chữ số và dấu câu. Chỉ fit trên train; validation dùng chọn mô hình; test dùng đánh giá các cấu hình đã đóng băng, không dùng để chỉnh tham số.',
            'TF-IDF unigram/bigram, min_df=2, max_df=1.0, sublinear_tf=True, norm=l2. NB alpha=1; LR C=1, max_iter=2000; LinearSVC C=1, max_iter=5000; random_state=42 khi áp dụng. Hòa Macro F1 trong 1e-6 thì so Accuracy, rồi thứ tự NB/LR/SVM.',
            'Một nhóm trùng gồm hai dòng trong train được giữ theo report-only. Không phát hiện text chuẩn hóa giao nhau giữa split; điều đó không loại trừ near-duplicate hoặc mọi nguồn rò rỉ. Lớp neutral chiếm khoảng 4,01% train; lecturer khoảng 71,47%.',
            'Các thí nghiệm gốc được giữ nguyên. Lần tích hợp kiểm tra artifact thật và môi trường mới, không huấn luyện lại để cải thiện điểm test. Log fixture/unit được phân biệt với kiểm tra artifact và trình duyệt thật.'
        ]),
        ('5. Result', [
            'Các bảng dưới đọc trực tiếp comparison.json đã lưu cho hai nhiệm vụ. Winner của cả hai là Linear SVM theo validation Macro F1. Đây là số đo local, không phải điểm bảo đảm cho phản hồi từ đơn vị khác.'
        ]),
    ]
    for heading, paragraphs in sections:
        doc.add_heading(heading, 1)
        for paragraph in paragraphs:
            doc.add_paragraph(paragraph)
    summaries = []
    for task in ('sentiment', 'topic'):
        data = read_json(f'reports/metrics/{task}/comparison.json')
        doc.add_heading(task.title(), 2)
        table = doc.add_table(rows=1, cols=6)
        table.style = 'Light Shading Accent 1'
        for cell, value in zip(table.rows[0].cells, ['Split', 'Model', 'Accuracy', 'Macro P', 'Macro R', 'Macro F1']):
            cell.text = value
        for split in ('validation', 'test'):
            for model, metrics in data[split].items():
                values = [split, model] + [f'{metrics[key]:.6f}' for key in ('accuracy', 'macro_precision', 'macro_recall', 'macro_f1')]
                for cell, value in zip(table.add_row().cells, values):
                    cell.text = value
        winner = data['selection']['algorithm']
        measured = data['test'][winner]
        summaries.append((task, measured))
        doc.add_paragraph(f'Winner: {winner}; Accuracy {measured["accuracy"]:.2%}; Macro F1 {measured["macro_f1"]:.2%}.')
        per_class = doc.add_table(rows=1, cols=5)
        per_class.style = 'Light Shading Accent 1'
        for cell, value in zip(per_class.rows[0].cells, ['Label', 'Precision', 'Recall', 'F1', 'Support']):
            cell.text = value
        for row in measured['per_class']:
            values = [row['label'], f'{row["precision"]:.4f}', f'{row["recall"]:.4f}', f'{row["f1"]:.4f}', str(row['support'])]
            for cell, value in zip(per_class.add_row().cells, values):
                cell.text = value
        doc.add_picture(str(OUT / 'figures' / task / 'confusion_matrix.png'), width=Inches(5.8))
    doc.add_heading('Kiểm chứng ứng dụng', 2)
    for name in ('chrome', 'msedge'):
        screenshot = OUT / 'evidence/frontend' / f'{name}-real-prediction.png'
        evidence = OUT / 'evidence/frontend' / f'{name}-real-prediction.json'
        if screenshot.exists() and evidence.exists():
            browser = json.loads(evidence.read_text(encoding='utf-8'))
            doc.add_paragraph(f'{name} {browser["version"]}: ảnh chạy thật; đầu vào là câu tự viết, không lấy từ corpus. Phản hồi: {browser["response"]}.')
            doc.add_picture(str(screenshot), width=Inches(6))
    for path in (OUT / 'evidence/phase-6').glob('*pytest*.txt'):
        lines = path.read_text(encoding='utf-8', errors='replace').splitlines()
        summary = [line for line in lines if 'passed' in line or 'failed' in line]
        if summary:
            doc.add_paragraph(f'{path.name}: {summary[-1]}')
    doc.add_heading('6. Conclusion & Future Work', 1)
    doc.add_paragraph('Hai baseline đã có kết quả đo và artifact tải lại. Sentiment còn hạn chế rõ ở neutral (Recall 17,96%, F1 27,78%); Topic còn yếu ở other (Recall 30,82%, F1 40,66%). Các cặp nhầm curriculum/lecturer cho thấy giao thoa từ vựng; nguyên nhân ngữ cảnh/gán nhãn là giả thuyết, chưa phải kết luận nhân quả.')
    doc.add_paragraph('Cần đánh giá trên dữ liệu mới được phép sử dụng, khảo sát nhãn ít mẫu và phản hồi đa chủ đề trong một nghiên cứu tiếp theo. Không điều chỉnh baseline đã đóng băng theo test hiện tại. P1 chỉ làm khi leader cho phép; PhoBERT/ABSA/cloud ngoài phạm vi bản này.')
    doc.add_paragraph('Điều kiện bên ngoài còn mở: quyền dữ liệu/model, tên thành viên và lịch nộp/thuyết trình; review/merge và nghiệm thu của leader. Xem docs/acceptance.md. Không coi hoàn thành kỹ thuật là đã được phép phân phối.')
    doc.add_heading('Tài liệu tham khảo và truy vết', 1)
    for text in [
        'Nguyen et al. (2018), UIT-VSFC: Vietnamese Students’ Feedback Corpus for Sentiment Analysis, KSE, pp. 19–24. DOI: 10.1109/KSE.2018.8573337.',
        'Nguồn: https://github.com/kietnv/uit-vsfc ; https://huggingface.co/datasets/uitnlp/vietnamese_students_feedback (license unknown tại lần kiểm tra 29/10/2026).',
        'Đặc tả: docs/specs/*.md. Thí nghiệm: notebooks/01_eda.ipynb, 02_sentiment.ipynb, 03_topic.ipynb; docs/sentiment/report.md và docs/topic/report.md.',
        'Bằng chứng: reports/data/manifest.json; reports/metrics/{sentiment,topic}/; reports/evidence/phase-6/; reports/evidence/frontend/.',
        'Đóng góp: reports/contributions.md. Hướng dẫn: docs/development.md. Kịch bản demo: reports/demo-script.md.'
    ]:
        doc.add_paragraph(text)
    doc.save(OUT / 'final-report.docx')

    presentation = Presentation()
    presentation.slide_width = SlideInches(13.333)
    presentation.slide_height = SlideInches(7.5)
    def slide(title, lines):
        item = presentation.slides.add_slide(presentation.slide_layouts[1])
        item.shapes.title.text = title
        frame = item.placeholders[1].text_frame
        frame.clear()
        for i, line in enumerate(lines):
            paragraph = frame.paragraphs[0] if i == 0 else frame.add_paragraph()
            paragraph.text = line
            paragraph.font.size = SlidePt(24)
        return item
    slide('Student Feedback AI — P0', ['Phân tích cảm xúc và chủ đề phản hồi sinh viên tiếng Việt', 'Đồ án Cơ sở và Ứng dụng Trí tuệ nhân tạo', 'Bản nội bộ 29/10/2026 — leader bổ sung tên nhóm/thành viên'])
    slide('Bài toán và phạm vi', ['Một câu → một nhãn cảm xúc + một nhãn chủ đề', 'Hai pipeline thực; kết quả hỗ trợ con người', 'P0: EDA, ML, API/UI, kiểm thử và báo cáo', 'CSV/Dashboard thuộc P1 chưa triển khai'])
    slide('Dữ liệu và nguồn', ['UIT-VSFC: 11.426 train / 1.583 validation / 3.166 test', 'Raw text, nhãn và split được giữ; checksum từng file', 'Một cặp trùng trong train; không giao text chuẩn hóa giữa split', 'Giấy phép nguồn unknown: quyền sử dụng/phân phối còn chờ'])
    slide('Phương pháp', ['NFC + lowercase + whitespace trong pipeline', 'TF-IDF unigram/bigram; min_df=2', 'So sánh NB, Logistic Regression và Linear SVM', 'Fit train; chọn validation Macro F1; không tối ưu theo test'])
    slide('Kiến trúc', ['HTML/CSS/JS → FastAPI → ModelService → hai pipeline', 'Cùng origin, một server local', 'Kiểm checksum, Python/package versions và labels', 'Health tách live/ready; lỗi 422/503/500'])
    for task, measured in summaries:
        slide(f'Kết quả {task} — Linear SVM', [f'Test Accuracy: {measured["accuracy"]:.2%}', f'Test Macro F1: {measured["macro_f1"]:.2%}', 'Chọn winner theo validation, không theo điểm test', f'Chi tiết: reports/metrics/{task}/comparison.json'])
        item = presentation.slides.add_slide(presentation.slide_layouts[5])
        item.shapes.title.text = f'Confusion matrix — {task}'
        item.shapes.add_picture(str(OUT / 'figures' / task / 'confusion_matrix.png'), SlideInches(3.5), SlideInches(1.3), height=SlideInches(5.8))
    slide('Kiểm thử và demo', ['Unit/fixture tách khỏi kiểm chứng artifact thật', 'API đối chiếu với pipeline trực tiếp', 'UI: Unicode, lỗi mạng, timeout, model chưa sẵn sàng', 'Bằng chứng và phiên bản trình duyệt trong reports/evidence/'])
    screenshot = OUT / 'evidence/frontend/msedge-real-prediction.png'
    if screenshot.exists():
        item = presentation.slides.add_slide(presentation.slide_layouts[5])
        item.shapes.title.text = 'Ảnh chạy thật — trình duyệt → API → hai model'
        item.shapes.add_picture(str(screenshot), SlideInches(2.4), SlideInches(1.3), height=SlideInches(5.8))
    slide('Hạn chế và bước tiếp theo', ['Sentiment neutral Recall 17,96%; Topic other Recall 30,82%', 'Một nhãn mỗi nhiệm vụ chưa diễn đạt câu đa cảm xúc/chủ đề', 'Cần dữ liệu đánh giá ngoài miền được phép sử dụng', 'Chờ xác nhận quyền dữ liệu/model và nghiệm thu leader'])
    slide('Nguồn và đóng góp', ['UIT-VSFC — Nguyen et al., KSE 2018, DOI 10.1109/KSE.2018.8573337', 'Nguồn dữ liệu: UIT-NLP / Hugging Face', 'Chi tiết phân công và hỗ trợ tích hợp: reports/contributions.md', 'Không dùng mock làm minh chứng dự đoán thật'])
    presentation.save(OUT / 'presentation.pptx')
    # Reopen through the document libraries, not just ZIP signatures.
    reopened = Document(OUT / 'final-report.docx')
    slides = Presentation(OUT / 'presentation.pptx')
    assert len(reopened.tables) == 4 and len(slides.slides) >= 12
    print(json.dumps({'docx_paragraphs': len(reopened.paragraphs), 'tables': len(reopened.tables), 'slides': len(slides.slides)}))


if __name__ == '__main__':
    main()
