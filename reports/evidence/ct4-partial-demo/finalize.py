"""Verify preexisting bytes, retain browser refreshes and render local demo report."""
from pathlib import Path
import hashlib
import json
import shutil

ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path):return json.loads(path.read_text(encoding='utf-8'))
def pct(v):return 'null' if v is None else f'{100*v:.4f}%'


def log_summary(name):
    p=OUT/name
    if not p.exists():return 'pending'
    data=p.read_bytes()
    text=data.decode('utf-16' if data.startswith((b'\xff\xfe',b'\xfe\xff')) else 'utf-8',errors='replace')
    summaries=[line for line in text.splitlines() if 'passed' in line or 'broken requirements' in line or '"verified"' in line]
    return summaries[-1] if summaries else 'pending'


def main():
    original=read(OUT/'preexisting.json')
    browser=[n for n in original if ((n.startswith('reports/evidence/frontend/') and n.endswith(('.png','.json')))
        or (n.startswith('reports/evidence/phase-4/') and n.endswith('-mobile-mock.png')))]
    restored=[]
    # Separate from actual new-demo screenshots: preserve historical test refreshes.
    for name in browser:
        source=ROOT/name
        dest=OUT/'baseline-browser-refresh'/source.name
        dest.parent.mkdir(exist_ok=True)
        shutil.copyfile(source,dest)
        if sha(source)!=original[name]:
            backup=ROOT/'.local-tools/ct4-partial-demo-backup'/name
            if source.resolve()!=source or not source.is_relative_to(ROOT) or sha(backup)!=original[name]:
                raise ValueError('Cannot safely restore original evidence '+name)
            shutil.copyfile(backup,source);restored.append(name)
    changed=[n for n,h in original.items() if not (ROOT/n).is_file() or sha(ROOT/n)!=h]
    preservation=dict(total=len(original),matched=len(original)-len(changed),changed=changed,restored=restored)
    (OUT/'preservation.json').write_text(json.dumps(preservation,indent=2),encoding='utf-8')
    if changed:raise ValueError('Original source/evidence changed: '+str(changed))
    v=read(OUT/'verification.json')
    for name,h in v['source_hashes'].items():
        if sha(ROOT/name)!=h:raise ValueError('Demo source changed since no-fit verification: '+name)
    lines=['# Demo CT4 — trả kết quả riêng từng phần, 2026-11-01','',
        'User đã yêu cầu áp dụng CT4 và xác định cảm xúc/chủ đề riêng. Đây là demo thử local, '
        'không nghiệm thu production hoặc đánh giá độc lập mới. Phủ định và nhiều đối tượng chưa xử lý riêng.','',
        '## Mở demo','',
        '[Bản CT4 mới](http://127.0.0.1:8001/) dùng app demo_v2; [baseline](http://127.0.0.1:8000/) '
        'giữ nguyên khi server cũ đang chạy. Chạy từ integration-p0:','',
        '```powershell','./.venv/Scripts/python.exe -B -m uvicorn demo_v2.main:app --host 127.0.0.1 --port 8001','```','',
        'Không chép đè models/ hay backend/frontend cũ. CT4 pair tải read-only từ '
        '`.local-tools/ct4-augmentation/run-1/research-selected/`; hai model này có metadata, checksum '
        'và runtime được kiểm. Cấu hình q10 lấy từ CT5 run-1, có kiểm receipt/config/threshold/model hashes. '
        'Dữ liệu/model/nguồn vẫn local, license unknown; không publish.','',
        '## Hành vi','',
        'Mỗi task chỉ trả nhãn khi vector hoàn chỉnh có đặc trưng và gap≥ngưỡng q10 riêng của task. '
        'Word rỗng/char có tín hiệu không bị reject riêng vì word. Gap không finite là lỗi; không '
        'biến thành nhãn. CT5 helper cũ giữ nguyên, lớp policy mới chặn finite-gap trước khi xuất kết quả.','',
        'q10 là lựa chọn demo tạm thời của người triển khai; các known examples đã được xem trước '
        'khi chọn cấu hình thử. Không chọn lại threshold, train hay calibrate. Chưa có chính sách '
        'production hoặc bằng chứng semantic/OOD mới; không coi SVM margin là xác suất confidence.','',
        'Trung tính/Khác chỉ hiển thị khi model thực sự trả nhãn và task được nhận. Thiếu căn cứ dùng '
        'status riêng, label=null và “Chưa đủ thông tin”, không ép thành neutral/other.','',
        '| Câu thử thực | Cảm xúc | Chủ đề |','| --- | --- | --- |']
    names={'positive':'Tích cực','negative':'Tiêu cực','neutral':'Trung tính','lecturer':'Giảng viên',
           'curriculum':'Chương trình đào tạo','facility':'Cơ sở vật chất','other':'Khác',None:'Chưa đủ thông tin'}
    for example in v['samples']:
        value=example['response']
        lines.append(f"| {example['text']} | {names[value['sentiment']['label']]} | {names[value['topic']['label']]} |")
    lines += ['', 'Các câu trên là chẩn đoán đã lộ, không ground truth độc lập. Câu phủ định vẫn có '
        'thể bị kết luận tiêu cực với margin cao; câu ngoài miền vẫn có thể được nhận. Gate không '
        'chứng minh mô hình hiểu đúng hoặc nhận ra ngoài miền. Không sửa luật riêng cho ví dụ.','',
        '![Kết quả riêng từng phần trên Chrome](../../reports/evidence/ct4-partial-demo/browser/chrome-partial.png)','',
        '## API 2.0 trong app thử nghiệm','',
        '`POST /api/v2/predict` nhận raw text strict, tối đa5000 code points, không blank/extra fields '
        'hoặc lone surrogate. HTTP200 cho complete/partial/insufficient; mỗi task answered hoặc '
        'insufficient_information, label canonical hoặc null. Không xuất nhãn thô bị giữ lại hay '
        'confidence/margin. Model thiếu/sai503, inference error500 không trả nửa kết quả, input sai422. '
        'GET /api/health báo model=ct4. V1 vẫn chạy ứng dụng cũ, không đổi hợp đồng.','',
        'Ví dụ response thật cho “Tốt”:','', '```json',
        json.dumps(v['samples'][0]['response'],ensure_ascii=False,indent=2),'```','',
        '## Coverage và chất lượng có điều kiện','',
        'Bảng dưới cùng 791 policy-audit IDs từ validation đã lộ CT1–CT5; ngưỡng chỉ lấy từ 792 '
        'development IDs. Không là final mù. Correct/N không tính từ chối thành đúng.','',
        '| Task | Input N | Accepted N | Coverage | Accepted accuracy | Accepted Macro F1 | Correct-and-answered / N |',
        '| --- | ---: | ---: | ---: | ---: | ---: | ---: |']
    audit=v['metrics']['policy_audit']
    for task,m in audit['tasks'].items():
        a=m['accepted_metrics'];correct=sum(a['confusion_matrix'][i][i] for i in range(len(a['label_order'])))
        lines.append(f"| {task} | {audit['input_count']} | {m['accepted_count']} | {pct(m['coverage'])} | {pct(a['accuracy'])} | {pct(a['macro_f1'])} | {pct(correct/audit['input_count'])} |")
    j=audit['joint']
    lines += ['', f"Cả hai task được nhận: {audit['accepted_pair_count']}/{audit['input_count']} = {pct(audit['pair_coverage'])}; "
        f"accepted joint accuracy {pct(j['accepted_accuracy'])}, selective risk {pct(j['selective_risk'])}, "
        f"joint correct-and-answered {j['correct_answered']}/{j['n_labeled']} = {pct(j['correct_and_answered_rate'])}. "
        'Khớp CT5 q10 cũ cho pair-accepted; điểm khác biệt giao diện là nay vẫn trả task được nhận '
        'khi task kia không đủ căn cứ. Không lấy trung bình Accuracy hai task làm joint.','',
        f"Trên full validation1583: {v['full_status_counts']}; xem verification.json để biết metrics "
        'tách full/development/audit, confusion matrix/per-class/support. Chưa đánh giá test để chọn '
        'policy, chưa có answerability/final được hai người rà; false reject/unsafe accept chưa nghiệm thu.','',
        '## Kiểm chứng và bảo toàn','',
        'RED module thiếu rồi API GREEN34; RED browser HTTP500 khi frontend chưa có; GREEN63 '
        'tests API/browser trên Chrome/Edge, 1 cảnh báo Starlette/httpx đã biết. No-fit verifier '
        'chạy với các fit APIs bị cấm, so API/service và metrics cũ trên cùng IDs.','']
    for name in ['full-suite-final.txt','pip-check.txt','frozen-ct5-replay.txt']:
        lines.append(f'- {name}: {log_summary(name)}')
    lines += ['', f"Preservation: {preservation['matched']}/{preservation['total']} preexisting hashes khớp; "
        f"restored={restored}. Cả CT1–CT5 và source/model cũ giữ nguyên. Browser outputs mới tại evidence/ct4-partial-demo/browser, "
        'refresh baseline giữ riêng, không gán mock làm bằng chứng thật.','',
        'Review độc lập và kết luận cuối tại reports/evidence/ct4-partial-demo/review.md; không suy ra '
        'đã review chỉ từ report tồn tại. Hai vấn đề readiness/stale result đã có regression RED17 '
        'fail→GREEN84 tests; final full suite sau sửa là bằng chứng toàn bộ mới nhất. Không '
        'commit/push/merge/Phase6 hoặc dọn worktree.','']
    (ROOT/'docs/quality/ct4-partial-demo.md').write_text('\n'.join(lines),encoding='utf-8')
    print(json.dumps(dict(preserved=preservation['matched'],total=preservation['total'],changed=changed)))


if __name__=='__main__':main()
