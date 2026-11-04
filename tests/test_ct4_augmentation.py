"""CT4 weak-label train augmentation: transformations, leakage, lifecycle and replay."""
import copy
import hashlib
import json
import unicodedata

import numpy as np
import pandas as pd
import pytest

from reports.ct4_augmentation import (unaccent, augment_train, select_candidate,
    fit_candidate, comparison, percentage_change, collision_report)


def frame():
    texts = ['ĐẸP quá 42! 🙂', 'Bình thường', 'Tệ quá', 'khong dau',
             'má', 'mà', 'ma', 'Nội dung tốt']
    return pd.DataFrame([dict(id=f'train:{i}', text=t, split='train',
        sentiment=['positive', 'neutral', 'negative'][i % 3],
        topic=['lecturer', 'curriculum', 'facility', 'other'][i % 4])
        for i, t in enumerate(texts)])


def test_unicode_preserved_deterministic_idempotent():
    text = '  ĐẸP đấy! 42 🙂\t\n'
    assert unaccent(text) == '  DEP day! 42 🙂\t\n'
    assert unaccent(unicodedata.normalize('NFD', text)) == unaccent(text)
    assert unaccent(unaccent(text)) == unaccent(text)
    assert unaccent('already unaccented!?') == 'already unaccented!?'
    with pytest.raises(TypeError):
        unaccent(None)


def test_hash_subsets_nested_lineage_and_source_unchanged():
    data = frame()
    original = data.copy(deep=True)
    eligible = [r.id for r in data.itertuples() if unaccent(r.text) != r.text]
    expected = sorted(eligible, key=lambda rid: hashlib.sha256(f'ct4-v1|42|{rid}'.encode()).hexdigest())
    prior = set()
    for ratio in (.25, .5, 1.):
        augmented, added = augment_train(data, ratio)
        assert [r['parent_id'] for r in added] == expected[:int(ratio * len(expected))]
        assert prior <= set(r['parent_id'] for r in added)
        prior = set(r['parent_id'] for r in added)
        assert len(augmented) == len(data) + len(added)
        for row in added:
            source = data.set_index('id').loc[row['parent_id']]
            assert row['id'] != row['parent_id'] and row['seed'] == 42
            assert row['method'] == 'unaccent' and row['version'] == 'ct4-v1'
            assert row['text'] == unaccent(source.text)
            assert row['sentiment'] == source.sentiment and row['topic'] == source.topic
    pd.testing.assert_frame_equal(data, original)
    for invalid in (0, .3, -1):
        with pytest.raises(ValueError):
            augment_train(data, invalid)
    data['split'] = 'validation'
    with pytest.raises(ValueError):
        augment_train(data, 1.)


def test_collisions_conflicts_and_overlap_are_reported_not_filtered():
    data = frame()
    augmented, added = augment_train(data, 1.)
    report = collision_report(data, added, data.iloc[[6]],
        [dict(id='known', text='má', sentiment=None, topic=None)])
    assert report['transformed_collisions']
    assert report['conflicting_labels']
    assert report['overlap_unaccented']['validation']
    assert report['overlap_unaccented']['known_cases']
    assert len(augmented) == len(data) + len(added)


def test_global_tie_bands_controls_first_and_percent_units():
    values = {'original': dict(macro_f1=.75, accuracy=.9),
              'ct2': dict(macro_f1=.7499992, accuracy=.91),
              'original_aug25': dict(macro_f1=.7499984, accuracy=.99)}
    assert select_candidate(values) == 'ct2'
    assert select_candidate({k: dict(macro_f1=.75, accuracy=.9) for k in values}) == 'original'
    assert percentage_change(.8, .84)['delta_percentage_points'] == pytest.approx(4)
    assert percentage_change(.8, .84)['relative_change_percent'] == pytest.approx(5)
    assert percentage_change(0, .1)['relative_change_percent'] is None


@pytest.mark.parametrize('combined', [False, True])
def test_clone_parameters_weights_and_train_only_vocabulary(combined):
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.pipeline import Pipeline, FeatureUnion
    from sklearn.svm import LinearSVC
    from ml.preprocessing import normalize_text
    data = pd.concat([frame(), frame().assign(id=lambda x: x.id + 'copy')])
    word = TfidfVectorizer(min_df=1, preprocessor=normalize_text, lowercase=False)
    features = FeatureUnion([('word', word), ('char', TfidfVectorizer(analyzer='char_wb', ngram_range=(3, 5)))]) if combined else word
    weights = {'negative': 2., 'neutral': 1., 'positive': 1.}
    parent = Pipeline([('features', features), ('clf', LinearSVC(class_weight=weights, random_state=42))]).fit(data.text, data.sentiment)
    before = copy.deepcopy(parent.predict(['ĐẸP quá', 'validationonlyword']))
    candidate = fit_candidate(parent, data, 'sentiment')
    assert candidate is not parent and candidate.steps[-1][1] is not parent.steps[-1][1]
    assert candidate.steps[-1][1].class_weight == weights
    assert np.array_equal(parent.predict(['ĐẸP quá', 'validationonlyword']), before)
    branch = candidate.steps[0][1].transformer_list[0][1] if combined else candidate.steps[0][1]
    assert 'validationonlyword' not in branch.vocabulary_


from test_ct2_class_weights import small_project


@pytest.fixture(scope='module')
def lifecycle(tmp_path_factory):
    # Build accented train BEFORE freezing controls; no test split exists.
    from datetime import datetime,timezone
    from importlib.metadata import version
    import platform
    import joblib
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.pipeline import Pipeline
    from sklearn.svm import LinearSVC
    from ml.preprocessing import normalize_text
    from ml.train_sentiment import TFIDF_PARAMS,CLF_PARAMS
    from ml.data import load_split
    from reports.ct_evaluation import create_baseline,evaluate,LABELS,ROOT
    root=tmp_path_factory.mktemp('ct4')/'project'
    for directory in ['models','data/raw/train','data/raw/dev','reports/data','reports/quality',
                      'docs/quality','reports/metrics/sentiment','reports/metrics/topic']:
        (root/directory).mkdir(parents=True,exist_ok=True)
    texts=[f'{s} {t} bài giảng tiếng Việt lặp lại' for s in LABELS['sentiment'] for t in LABELS['topic']]*2
    sentiments=[str(i) for i in range(3) for _ in range(4)]*2
    topics=[str(i) for _ in range(3) for i in range(4)]*2
    for split in ('train','dev'):
        for name,values in [('sents',texts),('sentiments',sentiments),('topics',topics)]:
            (root/f'data/raw/{split}/{name}.txt').write_text('\n'.join(values)+'\n',encoding='utf-8')
    for name in ['source','manifest']:
        (root/f'reports/data/{name}.json').write_text('{}',encoding='utf-8')
    (root/'docs/quality/ct1-protocol.md').write_text('Fixture protocol',encoding='utf-8')
    (root/'reports/ct_evaluation.py').write_bytes((ROOT/'reports/ct_evaluation.py').read_bytes())
    cases=[dict(id='known',text='positive lecturer bài giảng',group='clear',sentiment='positive',topic='lecturer'),
           dict(id='unknown',text='?',group='ambiguous',sentiment=None,topic=None)]
    (root/'reports/quality/known-cases.json').write_text(json.dumps(dict(cases=cases)),encoding='utf-8')
    train=load_split(root/'data/raw','train')
    pipes={t:Pipeline([('tfidf',TfidfVectorizer(preprocessor=normalize_text,**TFIDF_PARAMS)),
                      ('clf',LinearSVC(**CLF_PARAMS['linear_svm']))]).fit(train.text.tolist(),train[t].tolist()) for t in LABELS}
    actual=evaluate(root,pipes,cases)
    for task,pipe in pipes.items():
        artifact=root/f'models/{task}_pipeline.joblib'
        joblib.dump(pipe,artifact)
        metadata=dict(contract_version='1.0',task=task,algorithm='linear_svm',artifact_filename=artifact.name,
            artifact_sha256=hashlib.sha256(artifact.read_bytes()).hexdigest(),labels=LABELS[task],
            python_version=platform.python_version(),package_versions={p:version(p) for p in ['numpy','scipy','pandas','scikit-learn','joblib']},
            dataset_manifest_sha256=hashlib.sha256(b'{}').hexdigest(),preprocessing=dict(name='ml.preprocessing.normalize_text',version='1.0'),
            parameters=dict(tfidf={**TFIDF_PARAMS,'preprocessor':'ml.preprocessing.normalize_text'},classifier=dict(name='linear_svm',**CLF_PARAMS['linear_svm'])),
            selection=dict(algorithm='linear_svm',metric='macro_f1',validation_metrics=actual['metrics'][task]),
            trained_at=datetime.now(timezone.utc).isoformat())
        (root/f'models/{task}_metadata.json').write_text(json.dumps(metadata),encoding='utf-8')
        (root/f'reports/metrics/{task}/comparison.json').write_text(json.dumps(dict(selection=dict(algorithm='linear_svm'),
            validation=dict(linear_svm=actual['metrics'][task]),test=dict(linear_svm={'status':'historical fixture only'}))),encoding='utf-8')
    create_baseline(root,root/'reports/evidence/ct1/baseline-v2',root/'.local-tools/ct1-baseline-v2')
    from reports.ct2_class_weights import run_experiment as run2
    from reports.ct3_word_char import run_experiment as run3
    ct2 = root / '.local-tools/ct2-class-weights/run-2'
    ct3 = root / '.local-tools/ct3-word-char/run-1'
    run2(root, ct2)
    run3(root, ct3, ct2)
    return root, ct3


def test_nonempty_augmented_pipeline_vocabulary_and_manifest_binding(tmp_path):
    from reports.ct4_augmentation import _check_vocabulary, _manifest, _parameters
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.pipeline import Pipeline, FeatureUnion
    from sklearn.svm import LinearSVC
    from ml.preprocessing import normalize_text
    data=pd.concat([frame(),frame().assign(id=lambda x:x.id+'again')],ignore_index=True)
    augmented,added=augment_train(data,1.)
    assert added and len(augmented)>len(data)
    parent=Pipeline([('features',FeatureUnion([
        ('word',TfidfVectorizer(preprocessor=normalize_text,lowercase=False,min_df=2)),
        ('char',TfidfVectorizer(analyzer='char_wb',ngram_range=(3,5),min_df=2))])),
        ('clf',LinearSVC(class_weight={'negative':2,'neutral':1,'positive':1},random_state=42))])
    candidate=fit_candidate(parent,augmented,'sentiment')
    _check_vocabulary(candidate,augmented,{})
    assert _parameters(candidate)==_parameters(parent)
    manifest=_manifest(data,augmented,added,1.,'a'*64)
    assert manifest['source_groups']==len(data) and manifest['training_rows']==len(augmented)
    assert manifest['source_manifest_sha256']=='a'*64
    assert manifest['label_status']=='inherited_weak_supervision_not_human_reviewed'
    with pytest.raises(ValueError,match='Vocabulary|IDF'):
        _check_vocabulary(candidate,data,{})


def test_real_lifecycle_no_test_data_fresh_reload_and_no_fit_replay(lifecycle, monkeypatch):
    from reports.ct4_augmentation import run_experiment, verify_experiment
    from reports.ct_evaluation import read, verify_inventory
    from sklearn.svm import LinearSVC
    from sklearn.pipeline import Pipeline
    root, ct3 = lifecycle
    output = root / '.local-tools/ct4-augmentation/lifecycle'
    result = run_experiment(root, output, ct3)
    assert result['promotion'] == 'not_deployed'
    stored = read(output / 'results.json')
    for ratio in (25,50,100):
        manifest=read(output/f'augmentation/{ratio}.json')
        assert manifest['added_rows'] > 0
        assert manifest['training_rows'] > manifest['source_groups']
    assert len(stored['candidates']) == 6
    assert stored['selection'] == {'sentiment':'original','topic':'original'}
    assert stored['research_selected']['evaluation']['joint']['accuracy'] == 1
    assert 'stress' in stored['candidates']['original_aug25']
    assert not (root / 'data/raw/test').exists()
    def forbidden(*args, **kwargs):
        raise AssertionError('Replay must not fit')
    monkeypatch.setattr(LinearSVC, 'fit', forbidden)
    monkeypatch.setattr(Pipeline, 'fit', forbidden)
    assert verify_experiment(root, output, ct3)['verified']
    verify_inventory(root, read(root / 'reports/evidence/ct1/baseline-v2/inventory.json'))


@pytest.mark.parametrize('destination', ['live','root','existing','overlap','symlink'])
def test_path_refusal_precedes_loading_writing_and_fit(tmp_path, destination):
    from reports.ct4_augmentation import run_experiment
    root = tmp_path / 'project'
    root.mkdir()
    output = root / '.local-tools/ct4-augmentation/run'
    if destination == 'live': output = root / 'models'
    elif destination == 'root': output = root
    elif destination == 'existing': output.mkdir(parents=True)
    elif destination == 'overlap': output = root / '.local-tools/ct4-augmentation'
    else:
        external = tmp_path / 'external'
        external.mkdir()
        (root / '.local-tools').mkdir()
        try:
            (root / '.local-tools/ct4-augmentation').symlink_to(external, target_is_directory=True)
        except OSError:
            # Windows junction gives the same resolved-path contract without symlink privilege.
            import subprocess
            subprocess.run(['cmd','/c','mklink','/J',str(root / '.local-tools/ct4-augmentation'),str(external)],check=True,capture_output=True)
    with pytest.raises((ValueError,FileExistsError), match='output|research|exist|path'):
        run_experiment(root,output)


@pytest.mark.parametrize('tamper', ['results','artifact','metadata','config','data','parent','missing_receipt','schema','promotion','escape','nested_receipt'])
def test_tamper_and_receipt_semantics(lifecycle, tmp_path, tamper):
    from reports.ct4_augmentation import run_experiment, verify_experiment
    root, ct3 = lifecycle
    # Copy controls to isolate deliberate corruption from sibling cases.
    import shutil
    copied = tmp_path / 'project'
    shutil.copytree(root, copied)
    ct3 = copied / '.local-tools/ct3-word-char/run-1'
    output = copied / '.local-tools/ct4-augmentation/tamper'
    run_experiment(copied,output,ct3)
    if tamper == 'missing_receipt': (output/'receipt.json').unlink()
    elif tamper == 'nested_receipt':
        (output/'extra').mkdir()
        (output/'extra/receipt.json').write_text('{}')
    elif tamper in ('schema','promotion','escape'):
        receipt=json.loads((output/'receipt.json').read_text())
        if tamper=='schema': receipt['schema_version']='wrong'
        elif tamper=='promotion': receipt['promotion']='deployed'
        else: receipt['payload']['../outside']='0'*64
        (output/'receipt.json').write_text(json.dumps(receipt))
    else:
        path={'results':output/'results.json','config':output/'config.json',
              'artifact':output/'candidates/original_aug25/sentiment_pipeline.joblib',
              'metadata':output/'candidates/original_aug25/sentiment_metadata.json',
              'data':output/'augmentation/25.json', 'parent':ct3/'results.json'}[tamper]
        path.write_bytes(b'tampered')
    with pytest.raises((ValueError,FileNotFoundError)):
        verify_experiment(copied,output,ct3)


def test_joint_counts_transitions_and_null_cases():
    from reports.ct_evaluation import score_cases
    from reports.ct4_augmentation import _joint_transitions
    validation=frame().iloc[:2]
    truth=validation.to_dict('records')
    before=[{k:r[k] for k in ('id','sentiment','topic')} for r in truth]
    after=copy.deepcopy(before)
    after[0]['sentiment']='negative'
    result=_joint_transitions({'prediction_rows':before},{'prediction_rows':after},validation)
    assert result['regressed']==[truth[0]['id']] and not result['improved']
    with pytest.raises(ValueError):
        _joint_transitions({'prediction_rows':before[::-1]},{'prediction_rows':after},validation)
    cases=[dict(id='null',text='?',group='unknown',sentiment=None,topic=None)]
    scored=score_cases(cases,[dict(sentiment='neutral',topic='other')])
    assert scored['joint']['scored']==0 and scored['sentiment']['accuracy'] is None
