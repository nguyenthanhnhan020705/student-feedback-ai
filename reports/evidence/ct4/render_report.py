"""Render the CT4 handoff from verified local JSON; never run fitting."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
RUN=ROOT/'.local-tools/ct4-augmentation/run-1'
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
R=read(RUN/'results.json')
lines=['# CT4 — Augmentation không dấu chỉ từ train, 2026-10-31','',
       'Thí nghiệm offline đã chạy hữu hạn 6 cặp / 12 lần fit. Hai model demo trong models/ giữ nguyên. CT5 và Phase 6 không triển khai.',
       '', '## Phương pháp và nguồn','',
       'Chỉ biến đổi train: NFC → NFD → bỏ combining marks → đ/Đ thành d/D → NFC. Giữ dấu câu, chữ số, emoji, khoảng trắng và case; normalizer chính thức vẫn nằm trong pipeline. Không đổi loader/corpus/split.',
       'Chọn floor(25/50/100% số nguồn đủ điều kiện) theo SHA-256 ct4-v1|42|<source-id>; các subset lồng nhau. Thêm tối đa một biến thể/source, không bỏ câu gốc. Nhãn kế thừa là weak supervision, có thể mơ hồ/đổi nghĩa sau bỏ dấu; chưa được người rà từng biến thể.',
       'Clone hai parent cố định: Original và research-selected CT3 (Sentiment char_2_none, Topic CT2 sqrt_balanced). Giữ mọi tham số và class_weight đúng parent, không tính lại trọng số theo augmented rows. Không thêm cấu hình/seed sau xem điểm.',
       'Xếp từng task chỉ theo validation nguyên bản: Macro F1 cao nhất, dải hòa toàn cục 1e-6 rồi Accuracy cùng dung sai, còn hòa Original → CT2 → CT3 → thứ tự ứng viên. Stress/known cases không tham gia chọn. Không suy luận test trong runner; test lịch sử chỉ xuất hiện trong toàn suite hồi quy, không dùng chọn CT4.',
       '', '## Số dòng và collisions','',
       '| Ratio | Source groups | Eligible | Added rows | Training rows |',
       '| --- | ---: | ---: | ---: | ---: |']
for ratio in (25,50,100):
    m=read(RUN/f'augmentation/{ratio}.json')
    c=read(RUN/f'augmentation/collisions-{ratio}.json')
    lines.append(f'| {ratio}% | {m["source_groups"]} | {m["eligible_rows"]} | {m["added_rows"]} | {m["training_rows"]} |')
lines+=['','Không coi các dòng thêm là quan sát độc lập. Mỗi augmentation ID có parent_id, method/version/seed và nhãn nguồn. Các manifest đầy đủ chứa text chỉ lưu trong thư mục nghiên cứu local; không công bố dataset/model.','']
for ratio in (25,50,100):
    c=read(RUN/f'augmentation/collisions-{ratio}.json')
    lines.append(f'- {ratio}%: {c["already_unaccented"]} nguồn vốn không dấu; {len(c["transformed_collisions"])} nhóm nguồn trùng sau bỏ dấu, {len(c["conflicting_labels"])} nhóm có nhãn mâu thuẫn. Overlap normalized validation/known: {len(c["overlap_normalized"]["validation"])}/{len(c["overlap_normalized"]["known_cases"])}; sau bỏ dấu: {len(c["overlap_unaccented"]["validation"])}/{len(c["overlap_unaccented"]["known_cases"])} source IDs đánh giá.')
lines+=['','Collisions/overlap chỉ báo cáo, không xóa/chọn train theo validation hoặc đổi nhãn. Exact overlap không chứng nhận hết near-duplicates. Xem collisions-*.json local để biết ID/nhãn và hash text; bất đồng nhãn/overlap là giới hạn khi diễn giải robustness.','',
        '## Validation nguyên bản — cùng 1.583 source groups','',
        '| Pair | Sentiment Accuracy | Macro P | Macro R | Macro F1 | Topic Accuracy | Macro P | Macro R | Macro F1 | Joint |',
        '| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |']
audit_path=ROOT/'reports/evidence/ct4/stress-overlap-label-audit.json'
if audit_path.exists():
    audit=read(audit_path)
    lines[lines.index('## Validation nguyên bản — cùng 1.583 source groups'):lines.index('## Validation nguyên bản — cùng 1.583 source groups')]=[
        f'Rà nhãn sáu overlap sau bỏ dấu: {audit["conflicting_validation_groups"]} nhóm có bất đồng train/validation, giữ nguyên mọi nhãn; xem stress-overlap-label-audit.json. Dù nhãn khớp, các source overlap làm giới hạn tính độc lập của synthetic stress.','']
entries={**R['controls'],**{n:v['evaluation'] for n,v in R['candidates'].items()},
         'CT4-only':R['ct4_selected']['evaluation'],'best through CT4':R['research_selected']['evaluation']}
for name,e in entries.items():
    values=[f'{100*e["metrics"][t][k]:.4f}%' for t in ('sentiment','topic') for k in ('accuracy','macro_precision','macro_recall','macro_f1')]
    j=e['joint']
    lines.append('| '+name+' | '+' | '.join(values)+f' | {j["correct"]}/{j["n_rows"]} = {100*j["accuracy"]:.4f}% |')
lines+=['',f'CT4-only selection: `{R["ct4_selection"]}`.',f'Best through CT4 selection: `{R["selection"]}`.',
        'Hai lựa chọn là ghép theo Macro F1 từng task; joint tính lại bằng hai pipeline thật trên cùng ID, không lấy trung bình Accuracy.','',
        '## Accuracy/joint so Original và CT3','',
        '| Pair | Metric | vs Original (điểm %) | vs Original (% tương đối) | vs CT3 (điểm %) | vs CT3 (% tương đối) |',
        '| --- | --- | ---: | ---: | ---: | ---: |']
for name,key in [('CT4-only','ct4_selected'),('best through CT4','research_selected')]:
    item=R[key]
    for metric in ('sentiment','topic','joint'):
        changes=[]
        for control in ('original','ct3'):
            x=item['comparisons']['vs_'+control]['percent']
            p=x['joint'] if metric=='joint' else x[metric]['accuracy']
            changes.extend([f'{p["delta_percentage_points"]:+.4f}',f'{p["relative_change_percent"]:+.4f}' if p['relative_change_percent'] is not None else 'N/A'])
        lines.append(f'| {name} | {metric} | '+' | '.join(changes)+' |')
joint=R['research_selected']['comparisons']['vs_original']['percent']['joint']['delta_percentage_points']
lines+=['',f'Kết luận đo trên validation: joint best through CT4 {"tăng" if joint>0 else "giảm" if joint<0 else "không đổi"} {abs(joint):.4f} điểm % so Original. Macro F1 là chỉ số cân bằng lớp riêng, không được diễn đạt thành phần trăm trả đúng tổng thể.',
        'Model phục vụ không thay: mức thay đổi chất lượng đã triển khai là 0%. Validation đã được dùng nhiều lần, chưa chứng minh khả năng tổng quát trên phản hồi mới độc lập.','',
        '## Từng lớp, confusion matrix và hồi quy','']
for name,key in [('CT4-only','ct4_selected'),('best through CT4','research_selected')]:
    item=R[key]
    lines += [f'### {name}','']
    for task,metrics in item['evaluation']['metrics'].items():
        lines += ['| Task/lớp | Precision | Recall | F1 | Support |','| --- | ---: | ---: | ---: | ---: |']
        for row in metrics['per_class']:
            lines.append(f'| {task}/{row["label"]} | {100*row["precision"]:.4f}% | {100*row["recall"]:.4f}% | {100*row["f1"]:.4f}% | {row["support"]} |')
        lines+=['',f'{task} matrix (hàng thật, cột dự đoán, thứ tự {metrics["label_order"]}): `{metrics["confusion_matrix"]}`.','']
    for control in ('original','ct3'):
        diff=item['comparisons']['vs_'+control]
        for task in ('sentiment','topic'):
            change=diff['delta']['validation'][task]
            lines.append(f'- vs {control}, {task}: sai→đúng {len(change["improved"])}, đúng→sai {len(change["regressed"])}, thay nhãn {len(change["changed"])} (giữ cả sai→sai).')
        change=diff['joint_transitions']
        lines.append(f'- vs {control}, joint: sai→đúng {len(change["improved"])}, đúng→sai {len(change["regressed"])}, thay ít nhất một nhãn {len(change["changed"])}.')
    lines+=['']
lines+=['### Đánh đổi từng lớp của best through CT4','',
        '| Task/lớp | Δ Precision vs Original (điểm %) | Δ Recall vs Original | Δ F1 vs Original | Δ Precision vs CT3 | Δ Recall vs CT3 | Δ F1 vs CT3 |',
        '| --- | ---: | ---: | ---: | ---: | ---: | ---: |']
for task in ('sentiment','topic'):
    a=R['research_selected']['comparisons']['vs_original']['delta']['metrics'][task]['per_class']
    b=R['research_selected']['comparisons']['vs_ct3']['delta']['metrics'][task]['per_class']
    for old,new in zip(a,b):
        values=[f'{100*row[k]:+.4f}' for row in (old,new) for k in ('precision','recall','f1')]
        lines.append(f'| {task}/{old["label"]} | '+' | '.join(values)+' |')
lines+=['','Neutral/other có thay đổi Recall/F1 đi kèm Precision và các lớp còn lại như bảng; không coi Macro F1 tăng là mọi lớp đều tăng.','',
        'results.json chứa đầy đủ metrics/per-class/matrix/prediction rows và mọi changed/improved/regressed IDs cho cả 6 cặp, mỗi cặp ghép, so Original/CT2/CT3.','',
        '## Stress không dấu và known cases — tách riêng','',
        '| Pair | Stress sentiment Accuracy | Stress topic Accuracy | Stress joint | Known sentiment | Known topic | Known joint |',
        '| --- | ---: | ---: | ---: | ---: | ---: | ---: |']
for name in ('original','ct2','ct3','CT4-only','best through CT4'):
    stress=R['control_stress'][name] if name in R['controls'] else R['ct4_selected' if name=='CT4-only' else 'research_selected']['stress']
    e=entries[name]
    known=e['known_cases']
    columns=[f'{100*stress["metrics"][t]["accuracy"]:.4f}%' for t in ('sentiment','topic')]
    columns+=[f'{stress["joint"]["correct"]}/{stress["joint"]["n_rows"]}']
    columns+=[f'{known[t]["correct"]}/{known[t]["scored"]}' for t in ('sentiment','topic','joint')]
    lines.append('| '+name+' | '+' | '.join(columns)+' |')
lines+=['','Stress dùng đúng source groups validation, chỉ bỏ dấu và kế thừa nhãn weak supervision; không là tập độc lập. Known cases là 39 câu đã lộ, nhãn assistant_proposed chưa human-reviewed, null bị loại mẫu số từng task/joint. Không gộp stress/known với validation thành benchmark chung.','',
        '## Chi phí và artifact','',
        '| Candidate | Fit sentiment (s) | Fit topic (s) | Eval validation pair (s) | Model bytes sentiment/topic | Fit warnings |',
        '| --- | ---: | ---: | ---: | --- | ---: |']
for name,item in R['candidates'].items():
    lines.append(f'| {name} | {item["fit"]["sentiment"]["seconds"]:.3f} | {item["fit"]["topic"]["seconds"]:.3f} | {item["inference_seconds"]:.3f} | {item["artifact_bytes"]["sentiment"]}/{item["artifact_bytes"]["topic"]} | {sum(len(v["warnings"]) for v in item["fit"].values())} |')
lines+=['','Thời gian là đo local gồm overhead Python, không SLA/benchmark nhiều lần. Cấu hình không tăng class weight theo số dòng thêm; kết quả không cô lập việc tăng dữ liệu khỏi độ lặp của source groups.','',
        '## Tái lập và trạng thái kiểm chứng','',
        'Run chính thức: `.local-tools/ct4-augmentation/run-1/`. Chạy `./.venv/Scripts/python.exe -B reports/ct4_augmentation.py verify` từ bản tích hợp; verify không fit. Run từ chối output cũ/live, symlink/junction ngoài research và overlap với controls.',
        'Replay tái tạo subset/biến đổi/manifest/collisions, kiểm receipt schema_version/promotion/deployment và chính xác tập payload/path/checksum, nguồn/runtime/parent hashes, metadata/readiness, train-only vocabulary/IDF mỗi nhánh, params/class_weight, metrics/ranking/delta/stress/ghép thật.',
        'Bằng chứng RED/GREEN, replay, full suite, pip check và preservation tại reports/evidence/ct4/. Review độc lập do agent khác thực hiện sau implementation; kết quả cuối ghi ở review.md và ct4-progress.md, không suy ra đã review từ sự tồn tại của report này.',
        'Giữ quyền nguồn license unknown; chỉ local, không công bố/phân phối. Chưa có tập đánh giá mới gán nhãn độc lập; exact overlaps/collisions và nhãn kế thừa giới hạn suy luận. CT3 minor receipt semantics cũ và Backend lone-surrogate field minor giữ nguyên, không sửa để làm vô hiệu controls.','']
(ROOT/'docs/quality/ct4-report.md').write_text('\n'.join(lines),encoding='utf-8')
print('Rendered docs/quality/ct4-report.md')
