"""Train-only combined features, fair control selection and honest percentages."""
import copy

import numpy as np
import pandas as pd
import pytest

from reports.ct3_word_char import build_candidate, select_candidate, percentage_change


def frame(split='train'):
    return pd.DataFrame([
        dict(id=f'{split}:{i}', text=text, sentiment=label, topic='lecturer', split=split)
        for i, (text, label) in enumerate([
            ('bad poor course', 'negative'), ('bad poor teacher', 'negative'),
            ('ordinary normal course', 'neutral'), ('ordinary normal teacher', 'neutral'),
            ('great excellent course', 'positive'), ('great excellent teacher', 'positive')])])


def test_combined_pipeline_preserves_raw_normalization_and_train_only_vocabulary():
    from ml.preprocessing import normalize_text
    data = frame()
    candidate = build_candidate('sentiment', data, .5, 'none', {'sentiment': 'balanced'})
    features = candidate.named_steps['features']
    branches = dict(features.transformer_list)
    assert set(branches) == {'word', 'char'}
    assert branches['word'].preprocessor is normalize_text
    assert branches['char'].preprocessor is normalize_text
    assert branches['char'].analyzer == 'char_wb'
    assert branches['char'].ngram_range == (3, 5)
    assert features.transformer_weights == {'word': 1.0, 'char': .5}
    assert candidate.steps[-1][1].class_weight is None
    before = copy.deepcopy([(v.vocabulary_, v.idf_) for v in branches.values()])
    candidate.predict(['validationonlyword zzqqrr'])
    for v, (vocab, idf) in zip(branches.values(), before):
        assert v.vocabulary_ == vocab
        assert np.array_equal(v.idf_, idf)
        assert 'zzq' not in v.vocabulary_
    a = features.transform(['GREAT   COURSE'])
    b = features.transform(['great course'])
    assert (a != b).nnz == 0
    # Characters recover part of a misspelled word despite zero word features.
    assert branches['word'].transform(['teache']).nnz == 0
    assert branches['char'].transform(['teache']).nnz > 0


def test_ct2_weights_use_train_counts():
    data = frame()
    data = pd.concat([data, data[data.sentiment == 'negative']], ignore_index=True)
    model = build_candidate('sentiment', data, 1, 'ct2', {'sentiment': 'balanced'})
    assert model.steps[-1][1].class_weight == {
        'negative': 8 / 12, 'neutral': 8 / 6, 'positive': 8 / 6}


@pytest.mark.parametrize('mutation', ['validation', 'empty', 'missing_class', 'unknown', 'blank'])
def test_rejects_invalid_training_frame(mutation):
    data = frame()
    if mutation == 'validation':
        data['split'] = 'validation'
    elif mutation == 'empty':
        data = data.iloc[:0]
    elif mutation == 'missing_class':
        data = data[data.sentiment != 'neutral']
    elif mutation == 'unknown':
        data.loc[0, 'sentiment'] = 'unknown'
    else:
        data.loc[0, 'text'] = ' '
    with pytest.raises(ValueError):
        build_candidate('sentiment', data, 1, 'none', {'sentiment': 'balanced'})


def test_ranking_uses_global_bands_and_prefers_controls_in_ties():
    values = {'baseline': dict(macro_f1=.75, accuracy=.90),
              'ct2': dict(macro_f1=.7499992, accuracy=.91),
              'char_0.5_none': dict(macro_f1=.7499984, accuracy=.99)}
    assert select_candidate(values) == 'ct2'
    values = {k: dict(macro_f1=.75, accuracy=.9) for k in values}
    assert select_candidate(values) == 'baseline'


def test_percentages_distinguish_percentage_points_and_relative_change():
    assert percentage_change(.8, .84) == pytest.approx({
        'before_percent': 80, 'after_percent': 84, 'delta_percentage_points': 4,
        'relative_change_percent': 5})
    assert percentage_change(0, .1)['relative_change_percent'] is None


# Reuse the real serialized fixture: all canonical classes, no test split.
from test_ct2_class_weights import small_project


@pytest.fixture
def controls(small_project):
    from reports.ct2_class_weights import run_experiment
    root, baseline, snapshot = small_project
    ct2 = root / '.local-tools/ct2-class-weights/run-2'
    run_experiment(root, ct2)
    return root, ct2


@pytest.mark.parametrize('destination', ['models', 'root', 'existing', 'overlap'])
def test_refuses_unsafe_outputs_before_loading_controls(tmp_path, destination):
    from reports.ct3_word_char import run_experiment
    root = tmp_path / 'project'
    root.mkdir()
    output = {'models': root / 'models', 'root': root,
              'existing': root / '.local-tools/ct3-word-char/existing',
              'overlap': root / '.local-tools/ct3-word-char'}[destination]
    if destination == 'existing':
        output.mkdir(parents=True)
        (output / 'keep.txt').write_text('original')
    with pytest.raises((ValueError, FileExistsError), match='output|research|exist'):
        run_experiment(root, output)
    if destination == 'existing':
        assert (output / 'keep.txt').read_text() == 'original'


def test_real_lifecycle_no_test_data_and_replay_never_fits(controls, monkeypatch):
    from reports.ct3_word_char import run_experiment, verify_experiment
    from reports.ct_evaluation import read, verify_inventory
    from sklearn.svm import LinearSVC
    root, ct2 = controls
    output = root / '.local-tools/ct3-word-char/run'
    run_experiment(root, output, ct2)
    results = read(output / 'results.json')
    assert len(results['candidates']) == 6
    assert results['selection'] == {'sentiment': 'baseline', 'topic': 'baseline'}
    assert results['promotion'] == 'not_deployed'
    assert results['research_selected']['evaluation']['joint']['accuracy'] == 1
    assert results['research_selected']['percent_vs_original']['joint']['delta_percentage_points'] == 0
    assert not (root / 'data/raw/test').exists()
    def forbidden(*args, **kwargs):
        raise AssertionError('Replay must not fit')
    monkeypatch.setattr(LinearSVC, 'fit', forbidden)
    result = verify_experiment(root, output, ct2)
    assert result['verified'] and result['candidates'] == 12
    verify_inventory(root, read(root / 'reports/evidence/ct1/baseline-v2/inventory.json'))


@pytest.mark.parametrize('tamper', ['results', 'artifact', 'metadata', 'config', 'ct2', 'missing_receipt'])
def test_replay_refuses_corrupt_or_incomplete_runs(controls, tamper):
    from reports.ct3_word_char import run_experiment, verify_experiment
    root, ct2 = controls
    output = root / '.local-tools/ct3-word-char/run'
    run_experiment(root, output, ct2)
    if tamper == 'missing_receipt':
        (output / 'receipt.json').unlink()
    else:
        paths = {'results': output / 'results.json', 'config': output / 'config.json',
                 'artifact': output / 'candidates/char_0.5_none/sentiment_pipeline.joblib',
                 'metadata': output / 'candidates/char_0.5_none/sentiment_metadata.json',
                 'ct2': ct2 / 'results.json'}
        paths[tamper].write_bytes(b'changed')
    with pytest.raises((ValueError, FileNotFoundError)):
        verify_experiment(root, output, ct2)
