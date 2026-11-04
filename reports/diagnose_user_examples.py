"""Read-only model/API diagnosis; never fit or replace baseline artifacts."""
from pathlib import Path
import sys
import json
import hashlib
from collections import Counter
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from backend.model_service import model_service
from ml.data import load_split

EXAMPLES = [
    'Giảng viên giảng bài dễ hiểu, nhiệt tình và luôn giải đáp thắc mắc của sinh viên.',
    'Giảng viên giảng bài khó hiểu, thường xuyên đi trễ và không giải đáp câu hỏi.',
    'Giảng viên sử dụng slide và viết bảng trong giờ học.',
    'Chương trình đào tạo hợp lý, nội dung môn học thiết thực và có nhiều bài thực hành hữu ích.',
    'Chương trình đào tạo quá nặng lý thuyết, nội dung trùng lặp và thiếu thực hành.',
    'Chương trình học gồm các môn đại cương và các môn chuyên ngành.',
    'Phòng học sạch sẽ, máy lạnh hoạt động tốt và máy chiếu rất rõ nét.',
    'Phòng học nóng, bàn ghế hư hỏng và máy chiếu thường xuyên không hoạt động.',
    'Phòng học có bàn ghế, bảng và một máy chiếu.',
    'Tôi rất vui và hài lòng với những trải nghiệm của mình tại trường.',
    'Tôi cảm thấy thất vọng và không hài lòng với trải nghiệm của mình tại trường.',
    'Tôi hiện là sinh viên năm thứ hai của trường.',
    'Giảng viên giảng bài không dễ hiểu.',
    'Cơ sở vật chất không tệ như tôi nghĩ.',
    'Máy chiếu thật tuyệt vời, buổi nào cũng hỏng.',
    'Giảng viên rất nhiệt tình nhưng giảng bài khó hiểu.',
    'Giảng viên giảng rất hay nhưng phòng học quá nóng.',
    'Nhà trường nên bổ sung thêm các buổi thực hành.',
    'giang vien giang bai rat de hieu va nhiet tinh',
    'Giảng viên giảng bài rất dễ hiểu và nhiệt tình.',
    'thầy dạy ok lắm, dễ hỉu, nhiệt tình nữa :))',
    'Phòng học sạch đẹp quá 😍',
    'Phòng học sạch đẹp quá',
    'Phòng học sạch đẹp quá 😡',
    '😍', '😡',
    'Món phở hôm nay rất ngon.',
    'abcxyz qwerty 123456', 'Tốt.',
    'Giảng viên giảng bài dễ hiểu.',
    'Cơ sở vật chất tệ như tôi nghĩ.',
    'Không có ý kiến.', 'Em không có ý kiến gì.',
    'Không có góp ý.', 'Bình thường.',
    'Học phí quá cao.', 'Thủ tục đăng ký học phần phức tạp.',
    'Em muốn được tư vấn về học bổng.',
    'Các hoạt động ngoại khóa rất bổ ích.',
]


def main():
    assert model_service.loaded, model_service.status
    artifacts = list((ROOT / 'models').glob('*'))
    before = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
              for p in artifacts if p.is_file()}
    result = {'note': 'Diagnostic probes, not training or an independent quality benchmark.',
              'examples': [], 'heldout': {}}
    for text in EXAMPLES:
        direct = model_service.predict(text)
        request = urllib.request.Request('http://127.0.0.1:8000/api/predict',
            data=json.dumps({'text': text}).encode(),
            headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(request, timeout=15) as response:
            api = json.load(response)
        features = {}
        for task in ('sentiment', 'topic'):
            pipeline = getattr(model_service, task + '_model')
            vectorizer = pipeline.named_steps['tfidf']
            vector = vectorizer.transform([text])
            features[task] = {'nonzero': vector.nnz,
                'known_terms': vectorizer.get_feature_names_out()[vector.indices].tolist(),
                'decision_scores': dict(zip(pipeline.classes_.tolist(),
                    pipeline.decision_function([text])[0].tolist()))}
        matches = all(api[k] == v for k, v in direct.items())
        assert matches, (text, direct, api)
        result['examples'].append({'text': text, **direct, 'api_matches': matches,
                                   'features': features})
        print(json.dumps({'text': text, **direct,
                          'nonzero': features['sentiment']['nonzero']}, ensure_ascii=False))
    frame = load_split(ROOT / 'data/raw', 'test')
    for task, rare in [('sentiment', 'neutral'), ('topic', 'other')]:
        pipeline = getattr(model_service, task + '_model')
        predictions = pipeline.predict(frame.text.tolist())
        actual = frame[task].to_numpy()
        result['heldout'][task] = {
            'classes': pipeline.classes_.tolist(),
            'predicted_counts': dict(Counter(predictions)),
            'rare_label': rare,
            'rare_true_count': int(sum(actual == rare)),
            'rare_correct': int(sum((actual == rare) & (predictions == rare))),
            'correct_example_ids': frame.loc[(actual == rare) & (predictions == rare), 'id'].head(5).tolist(),
        }
    after = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
             for p in artifacts if p.is_file()}
    assert before == after
    result['mechanism_checks'] = {}
    for task in ('sentiment', 'topic'):
        pipeline = getattr(model_service, task + '_model')
        v = pipeline.named_steps['tfidf']
        variants = v.transform(['Phòng học sạch đẹp quá', 'Phòng học sạch đẹp quá 😍', 'Phòng học sạch đẹp quá 😡'])
        identical = (variants[0] != variants[1]).nnz == 0 and (variants[0] != variants[2]).nnz == 0
        assert identical
        zero = v.transform(['abcxyz qwerty 123456'])
        assert zero.nnz == 0
        scores = pipeline.decision_function(['abcxyz qwerty 123456'])[0]
        intercept = pipeline.steps[-1][1].intercept_
        assert (scores == intercept).all()
        result['mechanism_checks'][task] = {'emoji_variants_identical_vectors': identical,
            'unknown_input_zero_vector': True, 'unknown_scores_equal_classifier_intercept': True}
    result['artifact_hashes_unchanged'] = before
    output = ROOT / 'reports/evidence/user-feedback-diagnosis'
    output.mkdir(parents=True, exist_ok=True)
    (output / 'results.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(result['heldout'], ensure_ascii=False, indent=2))
    from playwright.sync_api import sync_playwright, expect
    labels = {'negative': 'Tiêu cực', 'neutral': 'Trung tính', 'positive': 'Tích cực',
              'lecturer': 'Giảng viên', 'curriculum': 'Chương trình đào tạo',
              'facility': 'Cơ sở vật chất', 'other': 'Khác'}
    browser_results = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel='chrome', headless=True)
        try:
            page = browser.new_page()
            page.goto('http://127.0.0.1:8000/')
            expect(page.locator('#health')).to_have_text('Mô hình sẵn sàng')
            expect(page.locator('#mockBanner')).to_be_hidden()
            for text in ['Không có ý kiến.', 'Bình thường.', 'Các hoạt động ngoại khóa rất bổ ích.',
                         'Giảng viên giảng bài không dễ hiểu.', 'abcxyz qwerty 123456', 'Tốt.']:
                page.locator('#text').fill(text)
                with page.expect_response('**/api/predict') as response:
                    page.locator('#go').click()
                data = response.value.json()
                expected = [labels[data['sentiment']], labels[data['topic']]]
                expect(page.locator('#out .res b')).to_have_text(expected)
                browser_results.append({'text': text, 'api': data, 'displayed': expected})
            (output / 'browser.json').write_text(json.dumps({'browser': browser.version,
                'mock': False, 'cases': browser_results}, ensure_ascii=False, indent=2), encoding='utf-8')
            print('Browser: 6 actual UI/API comparisons passed; no prediction-quality assertion.')
        finally:
            browser.close()


if __name__ == '__main__':
    main()
