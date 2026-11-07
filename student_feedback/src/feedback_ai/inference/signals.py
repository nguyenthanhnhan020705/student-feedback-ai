import numpy as np
from scipy import sparse
from sklearn.pipeline import Pipeline, FeatureUnion
from feedback_ai.inference.policy import LABELS
def _nnz(matrix):
    if sparse.issparse(matrix):
        result = matrix.tocsr(copy=True)
        result.eliminate_zeros()
        if not np.isfinite(result.data).all():
            raise ValueError('Nonfinite feature values')
        return result.getnnz(axis=1).astype(int).tolist()
    array = np.asarray(matrix)
    if array.ndim != 2 or not np.isfinite(array).all():
        raise ValueError('Invalid feature matrix')
    return np.count_nonzero(array, axis=1).astype(int).tolist()
def extract_signals(pipeline, texts, task):
    """Use actual multiclass columns and the complete pre-classifier transform."""
    if task not in LABELS or not isinstance(pipeline, Pipeline) or len(pipeline.steps) < 2:
        raise ValueError('Expected task and fitted feature/classifier pipeline')
    if not isinstance(texts, list) or any(not isinstance(t, str) or not t.strip() for t in texts):
        raise ValueError('Expected nonblank raw strings')
    classes = list(pipeline.classes_)
    if (len(classes) != len(LABELS[task]) or set(classes) != set(LABELS[task])):
        raise ValueError('Invalid classifier classes')
    if not texts:
        return []
    transform = pipeline[:-1]
    features = transform.transform(texts)
    counts = _nnz(features)
    clf = pipeline.steps[-1][1]
    scores = np.asarray(clf.decision_function(features))
    if scores.shape != (len(texts), len(classes)) or not np.isfinite(scores).all():
        raise ValueError('Invalid/nonfinite score shape')
    predicted = list(pipeline.predict(texts))
    expected = [classes[i] for i in scores.argmax(axis=1)]
    if predicted != expected:
        raise ValueError('Prediction does not agree with actual class score columns')
    branches = {}
    # CT3 features use a FeatureUnion as the final feature transformer.
    last = pipeline.steps[-2][1]
    if isinstance(last, FeatureUnion):
        inputs = pipeline[:-2].transform(texts) if len(pipeline.steps) > 2 else texts
        weights = last.transformer_weights or {}
        for name, branch in last.transformer_list:
            if branch == 'drop':
                continue
            values = inputs if branch == 'passthrough' else branch.transform(inputs)
            branches[name] = _nnz(values * weights.get(name, 1.))
    else:
        branches[pipeline.steps[-2][0]] = counts
    ordered = np.sort(scores, axis=1)
    gaps = ordered[:, -1] - ordered[:, -2]
    return [dict(prediction=str(predicted[i]), classes=classes,
                 scores=scores[i].tolist(), gap=float(gaps[i]), nnz=counts[i],
                 branch_nnz={name: values[i] for name, values in branches.items()})
            for i in range(len(texts))]
