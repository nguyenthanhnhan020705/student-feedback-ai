"""Finite train-only unaccented augmentation; trusted local research artifacts only."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import copy
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import platform
import shutil
import sys
from time import perf_counter
import unicodedata
import warnings

import joblib
import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.pipeline import FeatureUnion, Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from ml.preprocessing import normalize_text
from reports.ct_evaluation import LABELS, digest, read, write_new_json, verify_inventory, score_labels, score_cases
from reports.ct2_class_weights import compare_results
from reports.ct3_word_char import percentage_change

RATIOS = (.25, .5, 1.)
VARIANTS = {f'{parent}_aug{int(ratio*100)}': dict(parent=parent, ratio=ratio)
            for parent in ('original', 'ct3parent') for ratio in RATIOS}
ORDER = ('original', 'ct2', 'ct3', *VARIANTS)


def unaccent(text):
    if not isinstance(text, str):
        raise TypeError('text must be str')
    decomposed = unicodedata.normalize('NFD', unicodedata.normalize('NFC', text))
    return unicodedata.normalize('NFC', ''.join(c for c in decomposed if not unicodedata.combining(c)).translate(str.maketrans({'đ': 'd', 'Đ': 'D'})))


def augment_train(frame, ratio):
    if (ratio not in RATIOS or frame.empty or not frame.split.eq('train').all()
            or not frame.id.is_unique or any(not isinstance(t, str) or not t.strip() for t in frame.text)
            or any(set(frame[t]) != set(LABELS[t]) for t in LABELS)):
        raise ValueError('Require allowed ratio and nonempty unique train with canonical labels')
    rows = frame.to_dict('records')
    eligible = [r for r in rows if unaccent(r['text']) != r['text']]
    eligible.sort(key=lambda r: hashlib.sha256(f'ct4-v1|42|{r["id"]}'.encode()).hexdigest())
    added = [{**r, 'id': f'ct4-v1:{r["id"]}', 'parent_id': r['id'],
              'text': unaccent(r['text']), 'method': 'unaccent', 'version': 'ct4-v1', 'seed': 42}
             for r in eligible[:math.floor(ratio * len(eligible))]]
    if set(r['id'] for r in added) & set(frame.id):
        raise ValueError('Augmentation IDs collide with original source IDs')
    return pd.DataFrame(rows + [{k: r[k] for k in frame.columns} for r in added], columns=frame.columns), added


def collision_report(train, added, validation, cases):
    transformed = defaultdict(list)
    for row in train.to_dict('records'):
        transformed[normalize_text(unaccent(row['text']))].append(row)
    collisions = [dict(text_sha256=hashlib.sha256(text.encode()).hexdigest(),
                       ids=[r['id'] for r in rows], labels=[{t:r[t] for t in LABELS} for r in rows])
                  for text, rows in sorted(transformed.items()) if len(rows) > 1]
    conflicts = [r for r in collisions if any(len({x[t] for x in r['labels']}) > 1 for t in LABELS)]
    source = train.to_dict('records')
    def overlaps(transform):
        indexes = defaultdict(list)
        for row in source + added:
            indexes[transform(row['text'])].append(row['id'])
        return {name: [dict(id=r['id'], train_ids=indexes[transform(r['text'])])
                       for r in rows if transform(r['text']) in indexes]
                for name, rows in [('validation', validation.to_dict('records')), ('known_cases', cases)]}
    return dict(source_groups=len(train), already_unaccented=sum(unaccent(t)==t for t in train.text),
        augmented_rows=len(added), transformed_collisions=collisions, conflicting_labels=conflicts,
        overlap_normalized=overlaps(normalize_text),
        overlap_unaccented=overlaps(lambda text: normalize_text(unaccent(text))),
        policy='report_only_no_filter_or_relabel', near_duplicates='not_certified')


def select_candidate(metrics):
    if not metrics or set(metrics) - set(ORDER):
        raise ValueError('Unknown/empty candidate set')
    if any(type(m[k]) not in (int,float) or not math.isfinite(m[k]) or not 0 <= m[k] <= 1
           for m in metrics.values() for k in ('macro_f1','accuracy')):
        raise ValueError('Invalid scores')
    top = max(m['macro_f1'] for m in metrics.values())
    eligible = [n for n in ORDER if n in metrics and top-metrics[n]['macro_f1'] <= 1e-6]
    acc = max(metrics[n]['accuracy'] for n in eligible)
    return next(n for n in eligible if acc-metrics[n]['accuracy'] <= 1e-6)


def fit_candidate(parent, train, task):
    if (task not in LABELS or train.empty or not train.split.eq('train').all()
            or set(train[task]) != set(LABELS[task])):
        raise ValueError('Only complete canonical train may be fitted')
    return clone(parent).fit(train.text.tolist(), train[task].tolist())


def _joint_transitions(before, after, validation):
    old, new = before['prediction_rows'], after['prediction_rows']
    if [r['id'] for r in old] != validation.id.tolist() or [r['id'] for r in new] != validation.id.tolist():
        raise ValueError('Joint alignment mismatch')
    truths = validation.to_dict('records')
    improved, regressed, changed = [], [], []
    for a,b,truth in zip(old,new,truths):
        oa = all(a[t]==truth[t] for t in LABELS)
        nb = all(b[t]==truth[t] for t in LABELS)
        if not oa and nb: improved.append(truth['id'])
        if oa and not nb: regressed.append(truth['id'])
        if any(a[t]!=b[t] for t in LABELS): changed.append(dict(id=truth['id'],before=a,after=b))
    return dict(improved=improved,regressed=regressed,changed=changed,scored=len(truths))


def comparison(before, after, validation):
    return dict(delta=compare_results(before,after,validation),
        joint_transitions=_joint_transitions(before,after,validation),
        percent={**{t:{k:percentage_change(before['metrics'][t][k],after['metrics'][t][k])
                       for k in ('accuracy','macro_precision','macro_recall','macro_f1')} for t in LABELS},
                 'joint':percentage_change(before['joint']['accuracy'],after['joint']['accuracy'])})


def _locations(root, output, ct3_output):
    root = Path(root).resolve()
    # Reject redirected research roots (junctions included), not merely symlink leafs.
    expected = root / '.local-tools' / 'ct4-augmentation'
    if expected.resolve() != expected or (root/'.local-tools').resolve() != root/'.local-tools':
        raise ValueError('Research path redirects outside declared root')
    output = Path(output).resolve()
    ct3 = Path(ct3_output or root/'.local-tools/ct3-word-char/run-1').resolve()
    if output == expected or not output.is_relative_to(expected):
        raise ValueError('Use a fresh research output below .local-tools/ct4-augmentation/')
    if output.is_relative_to(ct3) or ct3.is_relative_to(output):
        raise ValueError('Output path overlaps frozen control')
    return root, output, ct3


def _models(directory):
    from backend.model_service import ModelService
    service = ModelService(directory)
    if not service.loaded:
        raise ValueError(f'Research model metadata/readiness invalid: {service.status}')
    return {t:getattr(service,t+'_model') for t in LABELS}


def _controls(root, ct3):
    from reports.ct3_word_char import verify_experiment
    ct2 = root/'.local-tools/ct2-class-weights/run-2'
    verify_experiment(root,ct3,ct2)
    result=read(ct3/'results.json')
    directories={'original':root/'models','ct2':ct2/'research-selected','ct3':ct3/'research-selected'}
    evaluations={'original':result['baseline'],'ct2':result['ct2'],
                 'ct3':result['research_selected']['evaluation']}
    return directories,evaluations


def _parameters(model):
    def encode(value):
        if value is normalize_text: return 'ml.preprocessing.normalize_text'
        if isinstance(value,type): return value.__module__+'.'+value.__qualname__
        if isinstance(value,dict): return {k:encode(v) for k,v in value.items()}
        if isinstance(value,(tuple,list)): return [encode(v) for v in value]
        if callable(value): raise ValueError('Unexpected callable parameter')
        return value
    features=model.steps[0][1]
    if isinstance(features,FeatureUnion):
        vectorizers={name:encode(v.get_params(deep=False)) for name,v in features.transformer_list}
        feature=dict(type='FeatureUnion',branches=vectorizers,weights=features.transformer_weights,
                     n_jobs=features.n_jobs,verbose=features.verbose)
    elif isinstance(features,TfidfVectorizer):
        feature=dict(type='TfidfVectorizer',parameters=encode(features.get_params(deep=False)))
    else: raise ValueError('Unsupported feature representation')
    return dict(steps=[name for name,_ in model.steps],tfidf=feature,
                classifier={'name':'linear_svm',**encode(model.steps[-1][1].get_params(deep=False))})


def _check_vocabulary(model, train, cache):
    features=model.steps[0][1]
    branches=features.transformer_list if isinstance(features,FeatureUnion) else [('word',features)]
    for _,vectorizer in branches:
        key=json.dumps(_parameters(Pipeline([('tfidf',vectorizer),('clf',model.steps[-1][1])]))['tfidf'],sort_keys=True)
        # Cache only within one exact training frame/ratio in caller.
        if key not in cache:
            counts=Counter()
            analyzer=vectorizer.build_analyzer()
            for text in train.text: counts.update(set(analyzer(text)))
            n=len(train)
            minimum=vectorizer.min_df if isinstance(vectorizer.min_df,int) else vectorizer.min_df*n
            maximum=vectorizer.max_df if isinstance(vectorizer.max_df,int) else vectorizer.max_df*n
            cache[key]={term:df for term,df in counts.items() if minimum <= df <= maximum}
        counts=cache[key]
        if set(vectorizer.vocabulary_) != set(counts):
            raise ValueError('Vocabulary differs from augmented train-only document frequencies')
        expected=np.empty(len(counts))
        for term,index in vectorizer.vocabulary_.items(): expected[index]=np.log((1+len(train))/(1+counts[term]))+1
        if not np.allclose(vectorizer.idf_,expected,rtol=0,atol=1e-14):
            raise ValueError('IDF differs from augmented train-only frequencies')


def _evaluate(frame,pipes,cases):
    started=perf_counter()
    predictions={t:[str(x) for x in pipes[t].predict(frame.text.tolist())] for t in LABELS}
    elapsed=perf_counter()-started
    metrics={t:score_labels(frame[t].tolist(),predictions[t],LABELS[t]) for t in LABELS}
    rows=[dict(id=rid,**{t:predictions[t][i] for t in LABELS}) for i,rid in enumerate(frame.id)]
    cp={t:list(pipes[t].predict([c['text'] for c in cases])) for t in LABELS}
    known=score_cases(cases,[{t:str(cp[t][i]) for t in LABELS} for i in range(len(cases))])
    correct=sum(all(predictions[t][i]==frame[t].iloc[i] for t in LABELS) for i in range(len(frame)))
    return dict(split='validation',metrics=metrics,prediction_rows=rows,known_cases=known,
                joint=dict(correct=correct,n_rows=len(frame),accuracy=correct/len(frame))),elapsed


def _stress(frame,pipes):
    transformed=frame.copy()
    transformed['text']=transformed.text.map(unaccent)
    predictions={t:[str(x) for x in pipes[t].predict(transformed.text.tolist())] for t in LABELS}
    metrics={t:score_labels(transformed[t].tolist(),predictions[t],LABELS[t]) for t in LABELS}
    correct=sum(all(predictions[t][i]==transformed[t].iloc[i] for t in LABELS) for i in range(len(frame)))
    return dict(status='synthetic_same_source_groups_weak_inherited_labels_not_for_selection',
        source_groups=len(frame),changed_rows=sum(a!=b for a,b in zip(frame.text,transformed.text)),
        metrics=metrics,prediction_rows=[dict(id=rid,**{t:predictions[t][i] for t in LABELS}) for i,rid in enumerate(frame.id)],
        joint=dict(correct=correct,n_rows=len(frame),accuracy=correct/len(frame)))


def _counts(frame):
    return {t:{label:int(sum(frame[t]==label)) for label in labels} for t,labels in LABELS.items()}


def _manifest(train,augmented,added,ratio,source_hash):
    return dict(schema_version='ct4-training.1',source_manifest_sha256=source_hash,
        transform='NFC/NFD/remove_combining_marks/d-stroke_to_d/NFC',version='ct4-v1',seed=42,ratio=ratio,
        source_groups=len(train),training_rows=len(augmented),added_rows=len(added),
        eligible_rows=sum(unaccent(t)!=t for t in train.text),source_counts=_counts(train),
        training_counts=_counts(augmented),label_status='inherited_weak_supervision_not_human_reviewed',
        added=added,training_sha256=hashlib.sha256(json.dumps(augmented.to_dict('records'),ensure_ascii=False,sort_keys=True).encode()).hexdigest())


def _config(root,train,dirs):
    from importlib.metadata import version
    return dict(schema_version='ct4.1',variants=VARIANTS,seed=42,
        selection='global_macro_f1_band_then_global_accuracy_band_1e-6_oldest_control_first',
        fit_split='train',selection_split='validation',stress='unaccented_validation_not_for_selection',
        test='no_inference_or_selection',promotion='not_deployed',deployment='research_only',
        source_groups=len(train),source_counts=_counts(train),class_weights='exact_parent_values_not_recomputed',
        python=platform.python_version(),packages={p:version(p) for p in ['numpy','scipy','pandas','scikit-learn','joblib']},
        original_manifest_sha256=digest(root/'reports/data/manifest.json'),
        source_train={p.name:digest(p) for p in sorted((root/'data/raw/train').glob('*.txt'))},
        parents={name:{f'{t}_{suffix}':digest(directory/f'{t}_{suffix}') for t in LABELS for suffix in ('pipeline.joblib','metadata.json')}
                 for name,directory in dirs.items()})


def _sources(dirs,output,selection):
    return {t:(dirs[name] if name in dirs else output/'candidates'/name) for t,name in selection.items()}


def _pair(dirs,output,selection):
    return {t:_models(directory)[t] for t,directory in _sources(dirs,output,selection).items()}


def _selection(results,only=False):
    return {t:select_candidate({**({} if only else {n:e['metrics'][t] for n,e in results['controls'].items()}),
                               **{n:r['evaluation']['metrics'][t] for n,r in results['candidates'].items()}}) for t in LABELS}


def _comparison_set(controls,actual,validation):
    return {f'vs_{name}':comparison(before,actual,validation) for name,before in controls.items()}


def _save(root,directory,task,model,parent_dir,variant,metrics,manifest_hash):
    directory.mkdir(parents=True,exist_ok=True)
    path=directory/f'{task}_pipeline.joblib'
    joblib.dump(model,path)
    metadata=copy.deepcopy(read(parent_dir/f'{task}_metadata.json'))
    metadata.update(artifact_sha256=digest(path),trained_at=datetime.now(timezone.utc).isoformat(),
                    dataset_manifest_sha256=manifest_hash,parameters=_parameters(model))
    metadata['selection']['validation_metrics']=metrics
    metadata['ct4']=dict(variant=variant,original_source_manifest_sha256=digest(root/'reports/data/manifest.json'),
        augmented_manifest_sha256=manifest_hash,fit_split='train',deployment='research_only',
        label_status='inherited_weak_supervision_not_human_reviewed')
    write_new_json(directory/f'{task}_metadata.json',metadata)


def _check_metadata(root,directory,task,model,parent,variant,metrics,manifest_hash):
    metadata=read(directory/f'{task}_metadata.json')
    if (_parameters(model)!=_parameters(parent) or metadata['parameters']!=_parameters(model)
            or metadata['dataset_manifest_sha256']!=manifest_hash
            or metadata['selection']['validation_metrics']!=metrics
            or metadata.get('ct4')!=dict(variant=variant,original_source_manifest_sha256=digest(root/'reports/data/manifest.json'),
                augmented_manifest_sha256=manifest_hash,fit_split='train',deployment='research_only',
                label_status='inherited_weak_supervision_not_human_reviewed')):
        raise ValueError('Augmented metadata/parent parameters mismatch')


def _summary(results):
    lines=['# CT4 validation research results','',
           '| Pair | Sentiment Accuracy | Sentiment Macro F1 | Topic Accuracy | Topic Macro F1 | Joint |',
           '| --- | ---: | ---: | ---: | ---: | ---: |']
    entries={**results['controls'],**{n:r['evaluation'] for n,r in results['candidates'].items()},
             **{n:results[n]['evaluation'] for n in ('ct4_selected','research_selected')}}
    for name,e in entries.items():
        lines.append(f'| {name} | {e["metrics"]["sentiment"]["accuracy"]:.4%} | {e["metrics"]["sentiment"]["macro_f1"]:.4%} | {e["metrics"]["topic"]["accuracy"]:.4%} | {e["metrics"]["topic"]["macro_f1"]:.4%} | {e["joint"]["correct"]}/{e["joint"]["n_rows"]} ({e["joint"]["accuracy"]:.4%}) |')
    lines+=['',f'All-control selection: {results["selection"]}',f'CT4-only selection: {results["ct4_selection"]}',
            '', 'Selection uses original validation Macro F1; stress/known cases are separate diagnostics.',
            'No serving model replacement; validation is repeatedly exposed, not an independent final test.','']
    return '\n'.join(lines)


def run_experiment(root,output,ct3_output=None):
    root,output,ct3=_locations(root,output,ct3_output)
    if output.exists(): raise FileExistsError('Research output already exists')
    dirs,controls=_controls(root,ct3)
    from ml.data import load_split
    train=load_split(root/'data/raw','train')
    validation=load_split(root/'data/raw','validation')
    cases=read(root/'reports/quality/known-cases.json')['cases']
    output.mkdir(parents=True,exist_ok=False)
    config=_config(root,train,dirs)
    write_new_json(output/'config.json',config)
    parents={n:_models(d) for n,d in dirs.items()}
    results=dict(config=config,controls=controls,control_stress={n:_stress(validation,p) for n,p in parents.items()},
                 candidates={},promotion='not_deployed')
    datasets={}
    for ratio in RATIOS:
        augmented,added=augment_train(train,ratio)
        manifest=_manifest(train,augmented,added,ratio,config['original_manifest_sha256'])
        path=output/f'augmentation/{int(ratio*100)}.json'
        write_new_json(path,manifest)
        write_new_json(output/f'augmentation/collisions-{int(ratio*100)}.json',collision_report(train,added,validation,cases))
        datasets[ratio]=(augmented,digest(path))
    for name,settings in VARIANTS.items():
        parent_name='original' if settings['parent']=='original' else 'ct3'
        augmented,manifest_hash=datasets[settings['ratio']]
        models,fit={},{}
        for task in LABELS:
            started=perf_counter()
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter('always')
                models[task]=fit_candidate(parents[parent_name][task],augmented,task)
            fit[task]=dict(seconds=perf_counter()-started,warnings=[dict(category=w.category.__name__,message=str(w.message)) for w in caught],
                parent=parent_name,parent_class_weight=parents[parent_name][task].steps[-1][1].class_weight)
        actual,seconds=_evaluate(validation,models,cases)
        directory=output/'candidates'/name
        for task in LABELS: _save(root,directory,task,models[task],dirs[parent_name],name,actual['metrics'][task],manifest_hash)
        loaded=_models(directory)
        cache={}
        for task in LABELS:
            _check_metadata(root,directory,task,loaded[task],parents[parent_name][task],name,actual['metrics'][task],manifest_hash)
            _check_vocabulary(loaded[task],augmented,cache)
        if _evaluate(validation,loaded,cases)[0]!=actual: raise ValueError('Serialization changes predictions')
        results['candidates'][name]=dict(evaluation=actual,stress=_stress(validation,loaded),fit=fit,
            inference_seconds=seconds,artifact_bytes={t:(directory/f'{t}_pipeline.joblib').stat().st_size for t in LABELS},
            comparisons=_comparison_set(controls,actual,validation))
        print(f'Fitted and checked {name}',flush=True)
    results['selection']=_selection(results)
    results['ct4_selection']=_selection(results,True)
    for key,selection in [('research_selected',results['selection']),('ct4_selected',results['ct4_selection'])]:
        pair=_pair(dirs,output,selection)
        actual,seconds=_evaluate(validation,pair,cases)
        results[key]=dict(evaluation=actual,stress=_stress(validation,pair),inference_seconds=seconds,
                          comparisons=_comparison_set(controls,actual,validation))
        directory=output/key.replace('_','-')
        directory.mkdir()
        for task,source in _sources(dirs,output,selection).items():
            for suffix in ('pipeline.joblib','metadata.json'): shutil.copyfile(source/f'{task}_{suffix}',directory/f'{task}_{suffix}')
    write_new_json(output/'results.json',results)
    (output/'summary.md').write_text(_summary(results),encoding='utf-8')
    _controls(root,ct3)
    payload={p.relative_to(output).as_posix():digest(p) for p in sorted(output.rglob('*')) if p.is_file()}
    write_new_json(output/'receipt.json',dict(schema_version='ct4.1',promotion='not_deployed',deployment='research_only',
        completed_at=datetime.now(timezone.utc).isoformat(),code_sha256=digest(Path(__file__)),
        ct3_receipt_sha256=digest(ct3/'receipt.json'),payload=payload,
        selection=results['selection'],ct4_selection=results['ct4_selection']))
    return dict(output=str(output),selection=results['selection'],ct4_selection=results['ct4_selection'],promotion='not_deployed')


def verify_experiment(root,output,ct3_output=None):
    root,output,ct3=_locations(root,output,ct3_output)
    receipt=read(output/'receipt.json')
    if (receipt.get('schema_version')!='ct4.1' or receipt.get('promotion')!='not_deployed'
            or receipt.get('deployment')!='research_only' or receipt['code_sha256']!=digest(Path(__file__))
            or receipt['ct3_receipt_sha256']!=digest(ct3/'receipt.json')):
        raise ValueError('Receipt semantics/runner/parent changed')
    payload=receipt['payload']
    for name in payload:
        path=Path(name)
        if path.is_absolute() or '..' in path.parts or not (output/path).resolve().is_relative_to(output):
            raise ValueError('Unsafe receipt payload path')
    actual_payload={p.relative_to(output).as_posix() for p in output.rglob('*') if p.is_file() and p!=output/'receipt.json'}
    if set(payload)!=actual_payload: raise ValueError('Receipt payload membership differs')
    verify_inventory(output,payload)
    dirs,controls=_controls(root,ct3)
    from ml.data import load_split
    train=load_split(root/'data/raw','train')
    validation=load_split(root/'data/raw','validation')
    cases=read(root/'reports/quality/known-cases.json')['cases']
    config=_config(root,train,dirs)
    results=read(output/'results.json')
    if (read(output/'config.json')!=config or results['config']!=config or results['controls']!=controls
            or set(results['candidates'])!=set(VARIANTS) or results['promotion']!='not_deployed'):
        raise ValueError('Configuration or controls differ')
    parents={n:_models(d) for n,d in dirs.items()}
    if results['control_stress']!={n:_stress(validation,p) for n,p in parents.items()}: raise ValueError('Control stress differs')
    datasets={}
    for ratio in RATIOS:
        augmented,added=augment_train(train,ratio)
        path=output/f'augmentation/{int(ratio*100)}.json'
        if read(path)!=_manifest(train,augmented,added,ratio,config['original_manifest_sha256']): raise ValueError('Augmentation provenance differs')
        if read(output/f'augmentation/collisions-{int(ratio*100)}.json')!=collision_report(train,added,validation,cases): raise ValueError('Collision report differs')
        datasets[ratio]=(augmented,digest(path),{})
    for name,settings in VARIANTS.items():
        directory=output/'candidates'/name
        models=_models(directory)
        actual,_=_evaluate(validation,models,cases)
        stored=results['candidates'][name]
        parent_name='original' if settings['parent']=='original' else 'ct3'
        augmented,manifest_hash,cache=datasets[settings['ratio']]
        for task in LABELS:
            _check_metadata(root,directory,task,models[task],parents[parent_name][task],name,actual['metrics'][task],manifest_hash)
            _check_vocabulary(models[task],augmented,cache)
            fit=stored['fit'][task]
            if (fit['parent']!=parent_name or fit['parent_class_weight']!=parents[parent_name][task].steps[-1][1].class_weight
                    or not isinstance(fit['seconds'],(int,float)) or not math.isfinite(fit['seconds']) or fit['seconds']<0
                    or not isinstance(fit['warnings'],list)):
                raise ValueError('Fit provenance differs')
        if (stored['evaluation']!=actual or stored['stress']!=_stress(validation,models)
                or stored['comparisons']!=_comparison_set(controls,actual,validation)
                or stored['artifact_bytes']!={t:(directory/f'{t}_pipeline.joblib').stat().st_size for t in LABELS}):
            raise ValueError('Replayed metrics/stress/regressions differ')
    for field,only in [('selection',False),('ct4_selection',True)]:
        if results[field]!=_selection(results,only) or receipt[field]!=results[field]: raise ValueError('Selection differs')
    for key,selection in [('research_selected',results['selection']),('ct4_selected',results['ct4_selection'])]:
        models=_pair(dirs,output,selection)
        actual,_=_evaluate(validation,models,cases)
        stored=results[key]
        if stored['evaluation']!=actual or stored['stress']!=_stress(validation,models) or stored['comparisons']!=_comparison_set(controls,actual,validation):
            raise ValueError('Combined selection results differ')
        directory=output/key.replace('_','-')
        for task,source in _sources(dirs,output,selection).items():
            for suffix in ('pipeline.joblib','metadata.json'):
                filename=f'{task}_{suffix}'
                if digest(source/filename)!=digest(directory/filename): raise ValueError('Combined artifact differs')
        if _evaluate(validation,_models(directory),cases)[0]!=actual: raise ValueError('Combined reload differs')
    if (output/'summary.md').read_text(encoding='utf-8')!=_summary(results): raise ValueError('Summary differs')
    return dict(verified=True,candidates=12,selection=results['selection'],ct4_selection=results['ct4_selection'],promotion='not_deployed')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=('run','verify'))
    parser.add_argument('--output',type=Path,default=ROOT/'.local-tools/ct4-augmentation/run-1')
    args=parser.parse_args()
    print(json.dumps((run_experiment if args.action=='run' else verify_experiment)(ROOT,args.output),ensure_ascii=False,indent=2))


if __name__=='__main__': main()
