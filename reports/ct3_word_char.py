"""CT3 offline word/character experiments; never promote or overwrite models/."""
from __future__ import annotations

import argparse
import copy
import json
import math
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import shutil
import sys
from time import perf_counter
import warnings

import joblib
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import FeatureUnion, Pipeline
from sklearn.svm import LinearSVC

from ml.preprocessing import normalize_text
from ml.train_sentiment import TFIDF_PARAMS, CLF_PARAMS
from reports.ct_evaluation import (
    LABELS, digest, read, write_new_json, verify_inventory, evaluate,
)
from reports.ct2_class_weights import class_weights, compare_results

CHAR_WEIGHTS = (.5, 1., 2.)
VARIANTS = {f'char_{weight:g}_{weighting}': dict(char_weight=weight, weighting=weighting)
            for weight in CHAR_WEIGHTS for weighting in ('none', 'ct2')}
ORDER = ('baseline', 'ct2', *VARIANTS)


def _pipeline(task, train, char_weight, weighting, ct2_selection):
    if (task not in LABELS or train.empty or not train['split'].eq('train').all()
            or any(not isinstance(t, str) or not t.strip() for t in train.text)
            or set(train[task]) != set(LABELS[task])):
        raise ValueError('Nonempty train with raw text and all canonical classes required')
    if char_weight not in CHAR_WEIGHTS or weighting not in ('none', 'ct2'):
        raise ValueError('Unknown CT3 fixed configuration')
    strategy = ct2_selection[task]
    weights = (None if weighting == 'none' or strategy == 'baseline'
               else class_weights(task, train[task].tolist(), strategy))
    features = FeatureUnion([
        ('word', TfidfVectorizer(preprocessor=normalize_text, **TFIDF_PARAMS)),
        ('char', TfidfVectorizer(analyzer='char_wb', ngram_range=(3, 5), min_df=2,
            sublinear_tf=True, lowercase=False, preprocessor=normalize_text)),
    ], transformer_weights={'word': 1., 'char': float(char_weight)})
    params = {**CLF_PARAMS['linear_svm'], 'class_weight': weights}
    return Pipeline([('features', features), ('clf', LinearSVC(**params))])


def build_candidate(task, train, char_weight, weighting, ct2_selection):
    return _pipeline(task, train, char_weight, weighting, ct2_selection).fit(
        train.text.tolist(), train[task].tolist())


def select_candidate(metrics):
    if not metrics or set(metrics) - set(ORDER):
        raise ValueError('Unknown/empty candidate set')
    if any(type(m[k]) not in (int, float) or not math.isfinite(m[k])
           or not 0 <= m[k] <= 1 for m in metrics.values() for k in ('macro_f1', 'accuracy')):
        raise ValueError('Invalid selection scores')
    best_f1 = max(m['macro_f1'] for m in metrics.values())
    eligible = [n for n in ORDER if n in metrics and best_f1 - metrics[n]['macro_f1'] <= 1e-6]
    best_acc = max(metrics[n]['accuracy'] for n in eligible)
    return next(n for n in eligible if best_acc - metrics[n]['accuracy'] <= 1e-6)


def percentage_change(before, after):
    return dict(before_percent=100 * before, after_percent=100 * after,
        delta_percentage_points=100 * (after - before),
        relative_change_percent=100 * (after / before - 1) if before else None)


def _percent_comparison(before, after):
    return {**{task: {key: percentage_change(before['metrics'][task][key], after['metrics'][task][key])
                      for key in ('accuracy', 'macro_f1')} for task in LABELS},
            'joint': percentage_change(before['joint']['accuracy'], after['joint']['accuracy'])}


def _locations(root, output, ct2_output):
    root, output = Path(root).resolve(), Path(output).resolve()
    research = root / '.local-tools/ct3-word-char'
    ct2 = Path(ct2_output or root / '.local-tools/ct2-class-weights/run-2').resolve()
    if output == research or not output.is_relative_to(research):
        raise ValueError('Use a fresh research output below .local-tools/ct3-word-char/')
    if output.is_relative_to(ct2) or ct2.is_relative_to(output):
        raise ValueError('Research output overlaps CT2 controls')
    return root, output, ct2


def _models(directory):
    from backend.model_service import ModelService
    service = ModelService(directory)
    if not service.loaded:
        raise ValueError(f'Research models invalid: {service.status}')
    return {task: getattr(service, task + '_model') for task in LABELS}


def _parameters(pipeline):
    def vectorizer_params(vectorizer):
        params = vectorizer.get_params(deep=False)
        params['preprocessor'] = 'ml.preprocessing.normalize_text' if params['preprocessor'] is normalize_text else 'invalid'
        params['dtype'] = np.dtype(params['dtype']).name
        return params
    features = pipeline.named_steps['features']
    params = dict(tfidf={
        'representation': 'word_char_feature_union',
        'branches': {name: vectorizer_params(v) for name, v in features.transformer_list},
        'transformer_weights': features.transformer_weights,
    }, classifier={'name': 'linear_svm', **pipeline.named_steps['clf'].get_params(deep=False)})
    # Canonical JSON representation for tuples and persisted metadata.
    return json.loads(json.dumps(params, allow_nan=False))


def _save_model(root, directory, task, pipeline, variant, metrics):
    directory.mkdir(parents=True, exist_ok=True)
    artifact = directory / f'{task}_pipeline.joblib'
    joblib.dump(pipeline, artifact)
    metadata = copy.deepcopy(read(root / f'models/{task}_metadata.json'))
    metadata.update(artifact_sha256=digest(artifact), trained_at=datetime.now(timezone.utc).isoformat(),
                    parameters=_parameters(pipeline))
    metadata['selection']['validation_metrics'] = metrics
    metadata['ct3'] = dict(variant=variant, fit_split='train', deployment='research_only')
    write_new_json(directory / f'{task}_metadata.json', metadata)


def _check_model(root, directory, task, model, train, variant, ct2_selection, feature_cache):
    from sklearn.utils.validation import check_is_fitted
    if (not isinstance(model, Pipeline) or list(model.named_steps) != ['features', 'clf']
            or not isinstance(model.named_steps['features'], FeatureUnion)
            or not isinstance(model.named_steps['clf'], LinearSVC)):
        raise ValueError('Unexpected combined pipeline structure')
    expected = _pipeline(task, train, **VARIANTS[variant], ct2_selection=ct2_selection)
    if _parameters(model) != _parameters(expected):
        raise ValueError('Candidate effective parameters differ from fixed configuration')
    metadata = read(directory / f'{task}_metadata.json')
    if (metadata['parameters'] != _parameters(model)
            or metadata.get('ct3') != dict(variant=variant, fit_split='train', deployment='research_only')):
        raise ValueError('Candidate metadata/configuration mismatch')
    check_is_fitted(model.named_steps['clf'])
    for name, vectorizer in model.named_steps['features'].transformer_list:
        # Independently derive expected vocabulary/IDF from train document frequencies.
        # This replay never calls fit; parameters are validated before cache use.
        if name not in feature_cache:
            analyzer = vectorizer.build_analyzer()
            counts = Counter()
            for text in train.text:
                counts.update(set(analyzer(text)))
            feature_cache[name] = {term: count for term, count in counts.items() if count >= 2}
        counts = feature_cache[name]
        if set(vectorizer.vocabulary_) != set(counts):
            raise ValueError('Vocabulary is not derived only from train')
        expected_idf = np.empty(len(counts))
        for term, index in vectorizer.vocabulary_.items():
            expected_idf[index] = np.log((1 + len(train)) / (1 + counts[term])) + 1
        if not np.allclose(vectorizer.idf_, expected_idf, rtol=0, atol=1e-14):
            raise ValueError('IDF is not derived only from train')


def _controls(root, ct2_output):
    from reports.ct2_class_weights import verify_experiment
    verify_experiment(root, ct2_output)
    results = read(ct2_output / 'results.json')
    return results['baseline'], results['research_selected']['evaluation'], results['selection']


def _configuration(train, ct2_selection):
    return dict(schema_version='ct3.1', variants=VARIANTS, fit_split='train',
        evaluation_split='validation', test='no_inference_or_selection',
        ct2_selection=ct2_selection, train_rows=len(train), seed=42,
        char_analyzer='char_wb', char_ngram_range=[3, 5], min_df=2,
        selection='global_macro_f1_band_then_global_accuracy_band_1e-6_control_first',
        promotion='not_deployed')


def _selection(results, ct3_only=False):
    return {task: select_candidate({
        **({} if ct3_only else {name: results[name]['metrics'][task] for name in ('baseline', 'ct2')}),
        **{name: item['evaluation']['metrics'][task] for name, item in results['candidates'].items()}
    }) for task in LABELS}


def _combined(root, output, ct2_output, selection):
    sources = {'baseline': root / 'models', 'ct2': ct2_output / 'research-selected'}
    return {task: _models(sources[name] if name in sources else output / 'candidates' / name)[task]
            for task, name in selection.items()}


def _comparison(before_original, before_ct2, actual, validation):
    return dict(evaluation=actual,
        delta_vs_original=compare_results(before_original, actual, validation),
        delta_vs_ct2=compare_results(before_ct2, actual, validation),
        percent_vs_original=_percent_comparison(before_original, actual),
        percent_vs_ct2=_percent_comparison(before_ct2, actual))


def _summary(results):
    lines = ['# CT3 — validation development comparison', '',
        'No test inference. Serving models unchanged. Deltas are percentage points.', '',
        '| Task | Variant | Accuracy | Macro F1 | Delta Accuracy vs original (pp) | Delta F1 vs original (pp) |',
        '| --- | --- | ---: | ---: | ---: | ---: |']
    evaluations = {n: results[n] for n in ('baseline', 'ct2')}
    evaluations.update({n: r['evaluation'] for n, r in results['candidates'].items()})
    for task in LABELS:
        base = results['baseline']['metrics'][task]
        for name, evaluation in evaluations.items():
            m = evaluation['metrics'][task]
            lines.append(f'| {task} | {name} | {m["accuracy"]:.4%} | {m["macro_f1"]:.4%}'
                         f' | {(m["accuracy"]-base["accuracy"])*100:+.4f}'
                         f' | {(m["macro_f1"]-base["macro_f1"])*100:+.4f} |')
    lines += ['', 'All-control selection: ' + str(results['selection']),
              'CT3-only selection: ' + str(results['ct3_selection']), '',
              '| Pair | Both correct | Joint accuracy | Delta vs original (pp) |',
              '| --- | ---: | ---: | ---: |']
    for name, evaluation in [('original', results['baseline']), ('ct2', results['ct2']),
            ('ct3_only', results['ct3_selected']['evaluation']),
            ('research_selected', results['research_selected']['evaluation'])]:
        joint = evaluation['joint']
        delta = (joint['accuracy'] - results['baseline']['joint']['accuracy']) * 100
        lines.append(f'| {name} | {joint["correct"]}/{joint["n_rows"]} | {joint["accuracy"]:.4%} | {delta:+.4f} |')
    lines += ['', 'Known-case labels remain provisional, assistant-authored and non-independent.',
              'See results.json for per-class deltas, every regression and relative percentage changes.',
              'This research result is not a serving deployment or independent final evaluation.', '']
    return '\n'.join(lines)


def run_experiment(root, output, ct2_output=None):
    root, output, ct2_output = _locations(root, output, ct2_output)
    if output.exists():
        raise FileExistsError(f'Research output already exists: {output}')
    baseline, ct2, ct2_selection = _controls(root, ct2_output)
    from ml.data import load_split
    train = load_split(root / 'data/raw', 'train')
    validation = load_split(root / 'data/raw', 'validation')
    cases = read(root / 'reports/quality/known-cases.json')['cases']
    output.mkdir(parents=True, exist_ok=False)
    config = _configuration(train, ct2_selection)
    write_new_json(output / 'config.json', config)
    results = dict(config=config, baseline=baseline, ct2=ct2, candidates={}, promotion='not_deployed')
    feature_cache = {}
    for variant, settings in VARIANTS.items():
        pipes, fit = {}, {}
        for task in LABELS:
            started = perf_counter()
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter('always')
                pipes[task] = build_candidate(task, train, **settings, ct2_selection=ct2_selection)
            fit[task] = dict(seconds=perf_counter()-started,
                warnings=[dict(category=w.category.__name__, message=str(w.message)) for w in caught])
        actual = evaluate(root, pipes, cases)
        directory = output / 'candidates' / variant
        for task in LABELS:
            _save_model(root, directory, task, pipes[task], variant, actual['metrics'][task])
        loaded = _models(directory)
        for task in LABELS:
            _check_model(root, directory, task, loaded[task], train, variant, ct2_selection, feature_cache)
        if evaluate(root, loaded, cases) != actual:
            raise ValueError('Serialized pipeline changes predictions')
        results['candidates'][variant] = dict(fit=fit, **_comparison(baseline, ct2, actual, validation))
        print(f'Fitted and reloaded {variant}', flush=True)
    results['selection'] = _selection(results)
    results['ct3_selection'] = _selection(results, ct3_only=True)
    for key, selection in [('research_selected', results['selection']), ('ct3_selected', results['ct3_selection'])]:
        actual = evaluate(root, _combined(root, output, ct2_output, selection), cases)
        results[key] = _comparison(baseline, ct2, actual, validation)
    selected = output / 'research-selected'
    selected.mkdir()
    for task, name in results['selection'].items():
        source = (root / 'models' if name == 'baseline' else ct2_output / 'research-selected'
                  if name == 'ct2' else output / 'candidates' / name)
        for suffix in ('pipeline.joblib', 'metadata.json'):
            shutil.copyfile(source / f'{task}_{suffix}', selected / f'{task}_{suffix}')
    if evaluate(root, _models(selected), cases) != results['research_selected']['evaluation']:
        raise ValueError('Combined selection serialization mismatch')
    write_new_json(output / 'results.json', results)
    (output / 'summary.md').write_text(_summary(results), encoding='utf-8')
    _controls(root, ct2_output)  # Frozen controls must still verify after every fit.
    payload = {p.relative_to(output).as_posix(): digest(p) for p in sorted(output.rglob('*')) if p.is_file()}
    write_new_json(output / 'receipt.json', dict(schema_version='ct3.1',
        completed_at=datetime.now(timezone.utc).isoformat(), code_sha256=digest(Path(__file__)),
        ct2_receipt_sha256=digest(ct2_output / 'receipt.json'), payload=payload,
        selection=results['selection'], ct3_selection=results['ct3_selection'], promotion='not_deployed'))
    return dict(output=str(output), selection=results['selection'], ct3_selection=results['ct3_selection'],
                promotion='not_deployed')


def verify_experiment(root, output, ct2_output=None):
    root, output, ct2_output = _locations(root, output, ct2_output)
    receipt = read(output / 'receipt.json')
    if (receipt['code_sha256'] != digest(Path(__file__))
            or receipt['ct2_receipt_sha256'] != digest(ct2_output / 'receipt.json')):
        raise ValueError('CT3 runner or CT2 evidence changed')
    verify_inventory(output, receipt['payload'])
    baseline, ct2, ct2_selection = _controls(root, ct2_output)
    from ml.data import load_split
    train = load_split(root / 'data/raw', 'train')
    validation = load_split(root / 'data/raw', 'validation')
    cases = read(root / 'reports/quality/known-cases.json')['cases']
    results = read(output / 'results.json')
    config = _configuration(train, ct2_selection)
    if (read(output / 'config.json') != config or results['config'] != config
            or results['baseline'] != baseline or results['ct2'] != ct2
            or set(results['candidates']) != set(VARIANTS) or results['promotion'] != 'not_deployed'):
        raise ValueError('Run configuration/controls differ')
    feature_cache = {}
    for variant in VARIANTS:
        directory = output / 'candidates' / variant
        pipes = _models(directory)
        for task in LABELS:
            _check_model(root, directory, task, pipes[task], train, variant, ct2_selection, feature_cache)
        actual = evaluate(root, pipes, cases)
        stored = results['candidates'][variant]
        if any(stored[key] != value for key, value in _comparison(baseline, ct2, actual, validation).items()):
            raise ValueError('Replayed metrics/regressions/percentages differ')
        for task in LABELS:
            metadata = read(directory / f'{task}_metadata.json')
            if metadata['selection']['validation_metrics'] != actual['metrics'][task]:
                raise ValueError('Metadata validation metrics differ')
    selection, ct3_selection = _selection(results), _selection(results, ct3_only=True)
    if (results['selection'] != selection or receipt['selection'] != selection
            or results['ct3_selection'] != ct3_selection or receipt['ct3_selection'] != ct3_selection):
        raise ValueError('Replayed selection differs')
    for key, choices in [('research_selected', selection), ('ct3_selected', ct3_selection)]:
        actual = evaluate(root, _combined(root, output, ct2_output, choices), cases)
        if results[key] != _comparison(baseline, ct2, actual, validation):
            raise ValueError('Combined metrics/regressions differ')
    for task, name in selection.items():
        source = (root / 'models' if name == 'baseline' else ct2_output / 'research-selected'
                  if name == 'ct2' else output / 'candidates' / name)
        for suffix in ('pipeline.joblib', 'metadata.json'):
            filename = f'{task}_{suffix}'
            if digest(source / filename) != digest(output / 'research-selected' / filename):
                raise ValueError('Combined artifact differs from selection')
    if evaluate(root, _models(output / 'research-selected'), cases) != results['research_selected']['evaluation']:
        raise ValueError('Reloaded selection differs')
    if (output / 'summary.md').read_text(encoding='utf-8') != _summary(results):
        raise ValueError('Summary differs from verified metrics')
    return dict(verified=True, candidates=len(VARIANTS)*len(LABELS), selection=selection,
                ct3_selection=ct3_selection, promotion='not_deployed')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('run', 'verify'))
    parser.add_argument('--output', type=Path, default=ROOT / '.local-tools/ct3-word-char/run-1')
    args = parser.parse_args()
    fn = run_experiment if args.action == 'run' else verify_experiment
    print(json.dumps(fn(ROOT, args.output), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
