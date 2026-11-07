from sklearn.metrics import accuracy_score, confusion_matrix, precision_recall_fscore_support
from feedback_ai.common.labels import SENTIMENT_LABELS, TOPIC_LABELS
LABELS={"sentiment":list(SENTIMENT_LABELS),"topic":list(TOPIC_LABELS)}
def score_labels(truth, predictions, labels):
    if (not truth or len(truth) != len(predictions)
            or any(x not in labels for x in truth)
            or any(x not in labels for x in predictions)):
        raise ValueError('Nonempty aligned canonical labels required')
    p, r, f, support = precision_recall_fscore_support(
        truth, predictions, labels=labels, zero_division=0)
    mp, mr, mf, _ = precision_recall_fscore_support(
        truth, predictions, labels=labels, average='macro', zero_division=0)
    return dict(accuracy=float(accuracy_score(truth, predictions)),
        macro_precision=float(mp), macro_recall=float(mr), macro_f1=float(mf),
        per_class=[dict(label=label, precision=float(p[i]), recall=float(r[i]),
                        f1=float(f[i]), support=int(support[i])) for i, label in enumerate(labels)],
        confusion_matrix=confusion_matrix(truth, predictions, labels=labels).tolist(),
        label_order=labels, n_rows=len(truth))

def score_cases(cases, predictions):
    if len(cases) != len(predictions) or len({c['id'] for c in cases}) != len(cases):
        raise ValueError('Case/prediction alignment or duplicate case ID')
    rows = []
    for case, pred in zip(cases, predictions):
        row = {**case, 'predicted': pred}
        for task in LABELS:
            expected = case[task]
            if (pred.get(task) not in LABELS[task]
                    or expected is not None and expected not in LABELS[task]):
                raise ValueError(f'Invalid {task} label in {case["id"]}')
            row[task + '_correct'] = None if expected is None else pred[task] == expected
        row['joint_correct'] = (None if any(row[t + '_correct'] is None for t in LABELS)
                                else all(row[t + '_correct'] for t in LABELS))
        rows.append(row)

    def counts(items):
        result = {}
        for task in [*LABELS, 'joint']:
            scored = [r[task + '_correct'] for r in items if r[task + '_correct'] is not None]
            result[task] = dict(scored=len(scored), correct=sum(scored),
                               accuracy=sum(scored) / len(scored) if scored else None)
        return result

    return {**counts(rows), 'rows': rows,
            'groups': {g: counts([r for r in rows if r['group'] == g])
                       for g in sorted({r['group'] for r in rows})},
            'status': 'exploratory_assistant_proposed_labels_not_human_reviewed'}