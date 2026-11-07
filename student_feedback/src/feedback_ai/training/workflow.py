"""Train fresh candidates; serving is never a training destination."""
from datetime import datetime, timezone
from importlib.metadata import version
import json
import platform
from pathlib import Path
import joblib
from feedback_ai.common.hashing import digest
from feedback_ai.data.loader import load_dataset
from feedback_ai.evaluation.topic import verify_dataset_manifest

def fresh_output(path):
    path=Path(path).resolve()
    if 'serving' in path.parts: raise ValueError('Cannot write training output into serving')
    if path.exists(): raise FileExistsError(path)
    return path

def train(task, data_dir, output_dir, manifest):
    out=fresh_output(output_dir)
    if task not in ('sentiment','topic'): raise ValueError('Unknown task')
    manifest_hash=verify_dataset_manifest(data_dir,manifest)
    from feedback_ai.training import sentiment,topic
    from feedback_ai.evaluation import sentiment as se,topic as te
    from feedback_ai.common.labels import SENTIMENT_LABELS,TOPIC_LABELS
    module=sentiment if task=='sentiment' else topic
    evaluator=se if task=='sentiment' else te
    frames=load_dataset(data_dir)
    models=module.train_models(frames['train'])
    selected=module.select_model(models,frames['validation'])
    winner=selected['algorithm']
    validation=evaluator.evaluate_models(models,frames['validation'])
    test=evaluator.evaluate_models(models,frames['test'])
    out.mkdir(parents=True)
    artifact=out/f'{task}_pipeline.joblib'
    joblib.dump(models[winner],artifact)
    if task=='topic': parameters=topic.pipeline_parameters(models[winner])
    else: parameters={'tfidf':sentiment.TFIDF_PARAMS,'classifier':{'name':winner,**sentiment.CLF_PARAMS[winner]}}
    metadata=dict(contract_version='1.0',task=task,algorithm=winner,artifact_filename=artifact.name,
        artifact_sha256=digest(artifact),labels=list(SENTIMENT_LABELS if task=='sentiment' else TOPIC_LABELS),
        python_version=platform.python_version(),package_versions={p:version(p) for p in ('numpy','scipy','pandas','scikit-learn','joblib')},
        dataset_manifest_sha256=manifest_hash,preprocessing={'name':'feedback_ai.data.preprocessing.normalize_text','version':'1.0'},
        parameters=parameters,selection=selected,trained_at=datetime.now(timezone.utc).isoformat())
    result={'task':task,'selection':selected,'validation':validation,'test':test,'metadata':metadata}
    (out/f'{task}_metadata.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2),encoding='utf-8')
    (out/'comparison.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    if task=='sentiment':sentiment._save_confusion_matrix(test[winner],out/'confusion_matrix.png',f'{task}: {winner}')
    else:te.save_confusion_figure(test[winner],out/'confusion_matrix.png')
    return result

def evaluate(task, artifact, data_dir, output_dir):
    out=fresh_output(output_dir)
    if task not in ('sentiment','topic'):raise ValueError('Unknown task')
    artifact=Path(artifact)
    metadata=json.loads((artifact.parent/f'{task}_metadata.json').read_text(encoding='utf-8'))
    if digest(artifact)!=metadata['artifact_sha256']:raise ValueError('Artifact checksum mismatch')
    pipeline=joblib.load(artifact)
    from feedback_ai.evaluation.metrics import score_labels,LABELS
    frame=load_dataset(data_dir)['test']
    predicted=[str(x) for x in pipeline.predict(frame.text.tolist())]
    metrics=score_labels(frame[task].tolist(),predicted,LABELS[task])
    errors=[{'id':r.id,'text':r.text,'expected':getattr(r,task),'predicted':p} for r,p in zip(frame.itertuples(),predicted) if getattr(r,task)!=p]
    out.mkdir(parents=True)
    for name,payload in [('metrics',metrics),('errors',errors)]:
        (out/f'{name}.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
    return metrics
