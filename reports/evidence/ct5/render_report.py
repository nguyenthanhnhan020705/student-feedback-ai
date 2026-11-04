"""Render CT5 documentation/figure from recorded, unmodified research payloads."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT/'.local-tools/ct5-selective-prediction/run-1'
OUT = Path(__file__).resolve().parent


def read(name):
    return json.loads((RUN/name).read_text(encoding='utf-8'))


def pct(value):
    return 'null' if value is None else f'{100*value:.4f}%'


def table(lines, header):
    lines.extend(['', '| ' + ' | '.join(header) + ' |', '| ' + ' | '.join(['---']*len(header)) + ' |'])


def row(lines, values):
    lines.append('| ' + ' | '.join(map(str, values)) + ' |')


def main():
    metrics, full = read('metrics.json'), read('ungated-full-validation.json')
    config, partition, thresholds = read('config.json'), read('partition.json'), read('thresholds.json')
    lines = ['# CT5 mốc A — Selective prediction offline, 2026-11-01', '',
        '**Trạng thái:** engineering_complete_independent_evaluation_pending. Chưa có policy triển khai; '
        '`recommended_policy=null`, `needs_coverage_risk_decision`. Hai model demo và API/UI 1.0 giữ nguyên.', '',
        'Công cụ chỉ đọc hai cặp frozen: original và CT4 research-selected '
        '(sentiment ct3parent_aug100, topic ct3parent_aug25). Không train/calibrate, không thêm dữ liệu '
        'hoặc cấu hình ngoài 5 policies đã chốt cho mỗi pair. SVM margin không phải xác suất confidence.', '',
        '## Dữ liệu và phép đo', '',
        f"Validation 1583 câu chia theo group hash cố định: threshold-development {partition['counts']['threshold_development']}, "
        f"policy-audit {partition['counts']['policy_audit']}; group counts {partition['group_counts']}. "
        'Cả hai đã lộ từ CT1–CT4, không là final/holdout độc lập mới. Train chỉ đọc để kiểm overlap; '
        'runner không đọc test để suy luận hoặc chọn threshold.', '',
        "group_key=normalize_text(unaccent(text)); SHA256('ct5-v1|42|'+group_key); byte đầu <128 là development. "
        'Cùng group luôn cùng phía; không đổi seed/chia lại sau xem điểm. Không có group validation nhiều nhãn '
        f"trong run này; overlap train/selected augmentation sau bỏ dấu: {partition['overlap_audit']['overlap_validation_rows']} "
        'validation rows. Chi tiết IDs/nhãn tại partition.json; không lọc/relabel, chưa chứng nhận hết near-duplicate.', '',
        '## Coverage–risk trên cùng policy-audit IDs', '',
        'N=tổng input, A=nhận cả cặp, C=nhận và cả hai đúng, E=nhận nhưng sai ít nhất một nhãn. '
        'Coverage=A/N; accepted accuracy=C/A; selective risk=E/A; correct-and-answered=C/N. '
        'Rejected không tính thành đúng. Tất cả 791 audit rows có đủ hai nhãn; mẫu số so sánh giữ nguyên.']
    table(lines, ['Pair/policy', 'N', 'A', 'C', 'E', 'Coverage', 'Accepted accuracy', 'Selective risk', 'C/N', 'E/N', 'Rejected correct', 'Rejected wrong'])
    for pair, datasets in metrics.items():
        for policy, m in datasets['policy_audit'].items():
            j = m['joint']
            row(lines, [f'{pair}/{policy}', m['input_count'], m['accepted_pair_count'], j['correct_answered'], j['wrong_answered'],
                pct(m['pair_coverage']), pct(j['accepted_accuracy']), pct(j['selective_risk']), pct(j['correct_and_answered_rate']),
                pct(j['answered_wrong_rate']), j['rejected_correct'], j['rejected_wrong']])
    lines += ['', 'Original q10: accepted accuracy tăng từ 82,5537% lên 89,9213%, '
        'nhưng coverage còn 80,2781% và C/N giảm còn 72,1871%. Q20 tiếp tục giảm risk bằng cách bỏ nhiều input hơn. '
        'Không gọi đây là tăng độ chính xác toàn hệ thống. Không chọn policy chỉ vì accepted accuracy cao nhất.', '',
        '![Coverage–risk development](../../reports/evidence/ct5/coverage-risk.png)', '',
        '## Model effect khác gating effect', '',
        'Trên cùng 791 audit IDs, always-answer original đúng 653, CT4 đúng 649: model effect là giảm 4 câu '
        '(−0,5057 điểm %). CT4 q10 trả đúng 574/791; chênh CT4 ungated→gated là bỏ 75 câu vốn đúng, '
        'không phải classifier sửa nhãn. Mỗi pair giữ nguyên raw predictions qua cả 5 policies.', '',
        '## Ungated full validation — bảng riêng, không so sai mẫu số']
    table(lines, ['Pair', 'N', 'Sentiment Accuracy', 'Macro F1', 'Topic Accuracy', 'Macro F1', 'Joint C/N'])
    for pair, m in full.items():
        s, t = m['tasks']['sentiment']['ungated_metrics'], m['tasks']['topic']['ungated_metrics']
        row(lines, [pair, m['input_count'], pct(s['accuracy']), pct(s['macro_f1']), pct(t['accuracy']), pct(t['macro_f1']),
                    f"{m['joint']['correct_answered']}/{m['joint']['n_labeled']} = {pct(m['joint']['correct_and_answered_rate'])}"])
    lines += ['', 'Khớp baseline 1296/1583 và CT4 1292/1583 đã lưu. Không dùng bảng 1583 để '
        'so trực tiếp gate trên 791 như cùng mẫu số.', '', '## Ngưỡng và diagnostics', '',
        'Gap=top1_score−top2_score theo classes_ thật. Ngưỡng quantile method=linear lấy riêng mỗi task/model '
        'trên rows nonzero của development; không dùng audit/known/stress/test. Nhận task khi vector hoàn chỉnh '
        'nonzero và gap≥threshold. Nhận pair khi cả hai task nhận. Word rỗng nhưng char còn tín hiệu không bị '
        'reject chỉ vì word. Không có ngưỡng chung cho min hai margin khác thang đo.']
    table(lines, ['Pair/policy', 'Sentiment threshold', 'Topic threshold'])
    for pair, policies in thresholds.items():
        for policy, values in policies.items(): row(lines, [f'{pair}/{policy}', values['sentiment'], values['topic']])
    lines += ['', 'Luôn lưu nnz toàn vector, nnz từng nhánh, scores/classes, gap, threshold, raw_prediction, '
        'accepted từng task/pair và reason. Pair reject thì labels_for_display=null cho cả hai; không trả '
        'nửa kết quả. Model lỗi/score sai shape/nonfinite/predict không khớp class columns là error, không '
        'ngụy trang thành abstention. Zero-vector và low-margin chỉ là lý do kỹ thuật, không chứng minh ngoài miền.', '',
        '## Per-task và pair-accepted audit metrics']
    table(lines, ['Pair/policy', 'Audit rejection reasons (có thể trùng trên cùng input)'])
    for pair, datasets in metrics.items():
        for policy, m in datasets['policy_audit'].items():
            row(lines, [f'{pair}/{policy}', json.dumps(m['reason_counts'], ensure_ascii=False)])
    table(lines, ['Pair/policy/task', 'Task coverage', 'Task accepted labeled N', 'Task Accuracy', 'Task Macro F1', 'Pair accepted labeled N', 'Pair Accuracy', 'Pair Macro F1'])
    for pair, datasets in metrics.items():
        for policy, m in datasets['policy_audit'].items():
            for task, values in m['tasks'].items():
                a, p = values['accepted_metrics'], values['pair_accepted_metrics']
                row(lines, [f'{pair}/{policy}/{task}', pct(values['coverage']), a['n_rows'], pct(a['accuracy']), pct(a['macro_f1']),
                            p['n_rows'], pct(p['accuracy']), pct(p['macro_f1'])])
    lines += ['', 'Per-class dưới đây trên **pair-accepted subset**, support thay đổi theo policy; không '
        'so như một tập cố định. JSON metrics.json có đầy đủ cả task-accepted và pair-accepted P/R/F1/support, '
        'confusion matrix và canonical label order, kể cả lớp support=0.']
    table(lines, ['Pair/policy/task/class', 'Precision', 'Recall', 'F1', 'Support'])
    for pair, datasets in metrics.items():
        for policy, m in datasets['policy_audit'].items():
            for task, values in m['tasks'].items():
                for c in values['pair_accepted_metrics']['per_class']:
                    row(lines, [f"{pair}/{policy}/{task}/{c['label']}", pct(c['precision']), pct(c['recall']), pct(c['f1']), c['support']])
    lines += ['', '## Development — chỉ mô tả, không gọi là audit/final']
    table(lines, ['Pair/policy', 'N', 'Coverage', 'Accepted accuracy', 'Risk', 'C/N'])
    for pair, datasets in metrics.items():
        for policy, m in datasets['threshold_development'].items():
            j = m['joint']
            row(lines, [f'{pair}/{policy}', m['input_count'], pct(m['pair_coverage']), pct(j['accepted_accuracy']), pct(j['selective_risk']), pct(j['correct_and_answered_rate'])])
    lines += ['', '## Known và synthetic stress — tách riêng', '',
        'Known: 39 câu đã lộ, kỳ vọng assistant_proposed chưa human-reviewed. Joint chỉ chấm 25 câu có '
        'đủ hai nhãn; sentiment 30, topic 29. Coverage vẫn tính trên 39 input. C/N dưới đây dùng N có '
        'đủ hai nhãn, không lấy 39 làm mẫu số correctness. Null không tự ép thành neutral/other.', '',
        'Stress: 1583 validation sources bỏ dấu, nhãn kế thừa weak supervision; sáu overlap sau bỏ dấu '
        'với train và validation đã lộ làm giới hạn tính độc lập. Không chọn ngưỡng bằng stress/known.']
    table(lines, ['Dataset/pair/policy', 'Input N', 'Joint labeled N', 'Coverage', 'Accepted labeled accuracy', 'Risk', 'C/N labeled'])
    for dataset in ['known','stress_unaccented_validation']:
        for pair, datasets in metrics.items():
            for policy, m in datasets[dataset].items():
                j = m['joint']
                row(lines, [f'{dataset}/{pair}/{policy}', m['input_count'], j['n_labeled'], pct(m['pair_coverage']), pct(j['accepted_accuracy']), pct(j['selective_risk']), pct(j['correct_and_answered_rate'])])
    lines += ['', 'Known groups giữ riêng trong metrics.json; ví dụ các ca không có ground truth vẫn '
        'được báo coverage và đầu ra, không coi là phép đo OOD accuracy. Với CT4 q10, ca known thuộc '
        'nhóm out_of_domain vẫn được nhận, 1/3 ambiguous_topic được nhận và ca conflicting_emoji '
        'được nhận. Đây là nhóm assistant-proposed, không là human-reviewed answerability; minh họa '
        'gate không bảo đảm hiểu/ngăn ngoài miền. Không thêm blacklist hoặc đổi threshold sau xem chúng.']
    table(lines, ['Known group/pair/policy', 'Input N', 'Joint labeled N', 'Pair coverage', 'Correct answered'])
    for pair, datasets in metrics.items():
        for policy, m in datasets['known'].items():
            for group, g in m['groups'].items():
                row(lines, [f'{group}/{pair}/{policy}', g['input_count'], g['joint']['n_labeled'], pct(g['pair_coverage']), g['joint']['correct_answered']])
    lines += ['', '## Bằng chứng và bảo toàn', '',
        'Run: `.local-tools/ct5-selective-prediction/run-1/`. Config ghi trước scoring. Receipt ct5.1 '
        'bind runtime, source, model/control/data hashes và toàn bộ payload; kiểm semantics '
        'not_deployed/offline_research_only/null recommendation. Fresh replay tính lại partition, '
        'thresholds, features/scores/predictions, decisions và metrics; không fit. Extra payload, kể cả '
        'nested receipt.json, bị từ chối. Receipt không phải chữ ký mật mã chống người cố tình sửa cả code/biên bản.', '',
        'Chạy từ integration-p0:', '', '```powershell',
        './.venv/Scripts/python.exe -B reports/evidence/ct5/no_fit.py verify',
        "$env:TV2_RUN_REAL_DATA='1'", './.venv/Scripts/python.exe -B -m pytest -q -p no:cacheprovider',
        './.venv/Scripts/python.exe -B -m pip check', '```', '',
        'No-fit launcher cấm Pipeline/FeatureUnion/TfidfVectorizer fit/fit_transform và LinearSVC.fit '
        'trong tiến trình run/replay. Không ghi đè run cũ; muốn chạy lại chọn --output fresh-run khác. '
        'Full-suite có thể dùng test lịch sử cho hồi quy, runner CT5 không dùng test để chọn ngưỡng.']
    for name in ['full-suite.txt','pip-check.txt','replay.txt']:
        p = OUT/name
        data = p.read_bytes() if p.exists() else b''
        text = data.decode('utf-16' if data.startswith((b'\xff\xfe', b'\xfe\xff')) else 'utf-8', errors='replace')
        summaries = [line for line in text.splitlines() if 'passed' in line or 'broken requirements' in line or '"verified"' in line]
        lines += ['', f"{name}: {summaries[-1] if summaries else 'pending — xem log sau khi tiến trình kết thúc.'}"]
    preservation = OUT/'preservation.json'
    if preservation.exists():
        data = json.loads(preservation.read_text(encoding='utf-8'))
        lines += ['', f"Preservation: {data['matched']}/{data['total']} preexisting hashes khớp; "
                  f"restored originals: {data['restored']}; refreshed browser outputs lưu riêng trong evidence CT5/browser."]
    lines += ['', 'Review độc lập: xem reports/evidence/ct5/review.md; không suy ra review đạt chỉ từ '
        'việc script/report tồn tại. Minors cũ ngoài CT5: CT3 receipt-semantics và Backend lone-surrogate '
        'error-detail field vẫn được giữ nguyên, không sửa control. Minor phòng vệ CT5 còn hoãn: finite '
        'score cực lớn có thể làm phép trừ gap overflow thành infinity; helper chưa chặn ngay sau trừ. '
        'Run hiện có mọi gap finite; threshold-development từ chối nonfinite và JSON allow_nan=False '
        'ngăn hoàn thành receipt có infinity. Không tuyên bố helper hỗ trợ mọi score float cực trị.', '', '### Frozen model/control hashes', '',
        'Hash đầy đủ còn có trong config.json và receipt.json; toàn bộ giữ local.']
    table(lines, ['Source', 'SHA-256'])
    for pair, models in config['models'].items():
        for name, sha in models.items(): row(lines, [f'{pair}/{name}', sha])
    for name, sha in config['control_receipts'].items(): row(lines, [f'{name}/receipt.json', sha])
    lines += ['', '## Đánh giá còn chờ', '',
        'Không có human-reviewed answerability hoặc final độc lập. Semantic false reject, unsafe '
        'accept và precision of abstention chưa thể nghiệm thu; giữ null, không suy ra từ rejected_correct '
        'hay low-margin. Xem ct5-data-requirements.md về dữ liệu, người rà, group split và đóng băng final. '
        'Không cần một policy tốt hơn để hoàn tất kỹ thuật; chưa có bằng chứng CT5 làm tăng tổng số câu đúng.', '',
        '## Đề xuất mốc B để duyệt riêng — chưa triển khai', '',
        'API 1.0 chỉ trả hai nhãn chuỗi; giữ nguyên. Đề xuất version mới `/api/v2/predict` với '
        '`contract_version="2.0"`, `status="answered"|"abstained"`, và `prediction` là object '
        'hai nhãn hoặc null cho cả cặp. HTTP 200 cho quyết định phân tích hợp lệ; không dùng 422/503 '
        'để biểu diễn abstention. Không trả margin dưới tên confidence.', '',
        'Ví dụ **minh họa schema, không phải response API đã triển khai**:', '',
        '```json', '{"contract_version":"2.0","status":"abstained","prediction":null,',
        ' "message":"Hệ thống chưa đủ cơ sở để kết luận cả cảm xúc và chủ đề. Bạn có thể nêu rõ nội dung và đối tượng được nhận xét hơn."}',
        '```', '',
        'Trước tích hợp: người dùng chốt coverage/risk và schema, bổ sung đánh giá độc lập; thiết kế '
        'migration giữ endpoint v1, tests v2 answered/abstained/error, UI thông báo không kết luận và '
        'giữ input, tests Unicode/timeout/recovery và parity với policy frozen. Không tự promote CT4 '
        'hoặc chọn q10/q20 làm mặc định. Không triển khai mốc B/Phase6, commit/push/merge hay công bố '
        'dataset/model. Quyền nguồn vẫn unknown; trusted local artifacts only.', '']
    (ROOT/'docs/quality/ct5-report.md').write_text('\n'.join(lines), encoding='utf-8')

    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.6))
    for pair, datasets in metrics.items():
        points = list(datasets['policy_audit'].items())
        x = [100*m['pair_coverage'] for _,m in points]
        risk = [100*m['joint']['selective_risk'] for _,m in points]
        correct = [100*m['joint']['correct_and_answered_rate'] for _,m in points]
        axes[0].plot(x, risk, 'o-', label=pair)
        axes[1].plot(x, correct, 'o-', label=pair)
        for (name,_),xx,yy in zip(points,x,risk):
            if name.startswith('zero_plus'): axes[0].annotate(name[-3:],(xx,yy),xytext=(3,4),textcoords='offset points',fontsize=8)
    for ax in axes:
        ax.set_xlabel('Pair coverage A/N (%)'); ax.grid(alpha=.25); ax.legend()
    axes[0].set_ylabel('Selective risk E/A (%)')
    axes[1].set_ylabel('Correct and answered C/N (%)')
    fig.suptitle('CT5 development: same 791 exposed policy-audit inputs; no policy selected')
    fig.tight_layout()
    fig.savefig(OUT/'coverage-risk.png', dpi=160)
    plt.close(fig)
    print('Rendered report and coverage-risk figure from frozen run-1')


if __name__ == '__main__': main()
