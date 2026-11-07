"""One-time migration helper: record the legacy demo_v3 app's responses for a fixed corpus.

Usage (run with the project's Python, pointing at the old checkout explicitly):
    python tools/capture_baseline.py --legacy-root <old-checkout> --output tests/parity/baseline.json
The recorded file is committed so parity tests need no access to the legacy source.
"""
import argparse, base64, io, json, os, sys
from pathlib import Path

PREDICT = [
    'Thầy giảng bài rõ ràng và phòng học thì nóng.', 'Thầy và cô đều giảng dễ hiểu.',
    'Chương trình có quá nhiều lý thuyết.', 'Phòng học có máy chiếu.', 'Tốt.', '🙂🙂🙂',
    'Giảng viên không nhiệt tình.', 'Thầy dạy hay, "tuyệt vời" nhưng chương trình nặng.',
    'Cơ sở vật chất cũ kỹ, wifi yếu.', 'x' * 5000,
    '', '   ', 'x' * 5001, '\ud800',
]
ROWS = ['Giảng viên nhiệt tình nhưng phòng học nóng.', 'Chương trình học quá nặng.', 'Tốt.', '🙂']
CSV = 'id,phản hồi\n1,"Thầy dạy hay\nnhưng phòng nóng"\n2,Tốt\n3,Tốt\n4,\n'.encode('utf-8')


def run(root):
    # Legacy code owns the top-level `reports`/`ml` names; hide this project's editable shims.
    sys.meta_path[:] = [f for f in sys.meta_path if 'editable' not in repr(f).lower()]
    sys.path[:] = [x for x in sys.path if not x.lower().endswith(('student_feedback\src', 'student_feedback/src'))]
    for name in [m for m in sys.modules if m.split('.')[0] in ('reports', 'ml', 'feedback_ai')]: del sys.modules[name]
    sys.path.insert(0, str(root)); os.chdir(root)
    from fastapi.testclient import TestClient
    from demo_v3.main import create_app
    import openpyxl
    client = TestClient(create_app())
    cases = [dict(kind='health', response=client.get('/api/health').json())]
    for text in PREDICT:
        try:
            r = client.post('/api/v3/predict', json={'text': text})
        except Exception as exc:  # unencodable request bodies are recorded as client errors
            cases.append(dict(kind='predict', text=text, client_error=type(exc).__name__)); continue
        cases.append(dict(kind='predict', text=text, status=r.status_code, body=r.json()))
    for raw in (b'{', b'[]', b'{"text":"a","x":1}', b'{"text":1}', b'{"text":"\xff"}'):
        r = client.post('/api/v3/predict', content=raw, headers={'content-type': 'application/json'})
        cases.append(dict(kind='predict_raw', raw=base64.b64encode(raw).decode(), status=r.status_code, body=r.json()))
    for text in ROWS + ['', ' ', 'x' * 5001]:
        r = client.post('/api/v3/analyze-row', json={'text': text})
        cases.append(dict(kind='analyze_row', text=text, status=r.status_code, body=r.json()))
    r = client.post('/api/v3/import?filename=a.csv', content=CSV)
    cases.append(dict(kind='import', filename='a.csv', raw=base64.b64encode(CSV).decode(), status=r.status_code, body=r.json()))
    r = client.post('/api/v3/import?filename=a.pdf', content=b'x')
    cases.append(dict(kind='import', filename='a.pdf', raw=base64.b64encode(b'x').decode(), status=r.status_code, body=r.json()))
    rows = [dict(id='r1', source_row=2, text='=SUM(1)\x01', status='ok', sentiment='mixed', topics=['lecturer', 'facility'],
                 aspects={'lecturer': 'positive', 'facility': 'negative'}, error=''),
            dict(id='r2', source_row=3, text='', status='invalid', error='Dòng trống')]
    r = client.post('/api/v3/export', json=dict(name='phiên', rows=rows))
    book = openpyxl.load_workbook(io.BytesIO(r.content))
    sheets = {ws.title: [[(c.value, c.data_type) for c in row] for row in ws.iter_rows()] for ws in book.worksheets}
    cases.append(dict(kind='export', request=dict(name='phiên', rows=rows), status=r.status_code,
                      disposition=r.headers.get('content-disposition'), sheets=sheets))
    return cases


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--legacy-root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True); args = parser.parse_args()
    output = args.output.resolve(); cases = run(args.legacy_root.resolve())
    output.write_text(json.dumps(cases, ensure_ascii=True, indent=1), encoding='utf-8'); print(len(cases), 'cases ->', output)
