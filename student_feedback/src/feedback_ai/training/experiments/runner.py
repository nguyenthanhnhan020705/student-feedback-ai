"""Reproducible experiment runs, independent of historical output directories."""
import json
from pathlib import Path
import joblib
from feedback_ai.common.hashing import digest
from feedback_ai.common.labels import SENTIMENT_LABELS, TOPIC_LABELS
from feedback_ai.data.loader import load_dataset, inspect_data
from feedback_ai.evaluation.metrics import score_labels
from feedback_ai.training.workflow import fresh_output

def run_experiment(name, config, output_dir):
    from feedback_ai.training import sentiment,topic
    from feedback_ai.training.experiments import class_weights, word_char, augmentation, selective
    from feedback_ai.inference.signals import extract_signals
    if name not in ('baseline','class_weights','word_char','augmentation','selective'):
        raise ValueError('Unknown experiment')
    out=fresh_output(output_dir)
    data=load_dataset(config['data_dir']);train=data['train'];validation=data['validation']
    labels={'sentiment':list(SENTIMENT_LABELS),'topic':list(TOPIC_LABELS)}
    base={};models={};scores={};selection={}
    # CT2-CT4 compare frozen model inputs supplied explicitly, never hidden legacy paths.
    for task in labels:
        if name=='baseline':
            module=sentiment if task=='sentiment' else topic
            candidates=module.train_models(train)
            selection[task]=module.select_model(candidates,validation)['algorithm']
        else:
            path=Path(config['models'][task]);expected=config['model_sha256'][task]
            if digest(path)!=expected:raise ValueError('Control model checksum mismatch')
            base[task]=joblib.load(path)
            candidates={'baseline':base[task]}
            if name=='class_weights':
                for strategy in class_weights.STRATEGIES:
                    candidates[strategy]=class_weights.fit_candidate(base[task],train,task,strategy)[0]
            elif name=='word_char':
                for variant,params in word_char.VARIANTS.items():
                    candidates[variant]=word_char.build_candidate(task,train,ct2_selection=config['ct2_selection'],**params)
                ct2path=Path(config['ct2_models'][task])
                if digest(ct2path)!=config['ct2_sha256'][task]:raise ValueError('CT2 checksum mismatch')
                candidates['ct2']=joblib.load(ct2path)
            elif name=='augmentation':
                # Exact parent controls supplied by configuration; no retraining of controls.
                candidates={'original':base[task]}
                for control in ('ct2','ct3'):
                    cp=Path(config[control+'_models'][task])
                    if digest(cp)!=config[control+'_sha256'][task]:raise ValueError('Control checksum mismatch')
                    candidates[control]=joblib.load(cp)
                for parent_key,parent in [('original',base[task]),('ct3parent',candidates['ct3'])]:
                    for ratio in augmentation.RATIOS:
                        augmented,_=augmentation.augment_train(train,ratio)
                        candidates[f'{parent_key}_aug{int(ratio*100)}']=augmentation.fit_candidate(parent,augmented,task)
        models[task]=candidates
        scores[task]={key:score_labels(validation[task].tolist(),[str(x) for x in model.predict(validation.text.tolist())],labels[task]) for key,model in candidates.items()}
        if name in ('class_weights','word_char','augmentation'):
            selector={'class_weights':class_weights,'word_char':word_char,'augmentation':augmentation}[name]
            selection[task]=selector.select_candidate(scores[task])
    result={'experiment':name,'config':config,'validation':scores,'selection':selection,
            'dataset':inspect_data(config['data_dir']),'promotion':'not_deployed'}
    if name=='selective':
        partition=selective.partition_validation(validation)
        signals={t:extract_signals(base[t],validation.text.tolist(),t) for t in labels}
        indices=[i for i,row in enumerate(partition['rows']) if row['subset']=='threshold_development']
        thresholds=selective.fit_thresholds(signals,indices)
        audit=[i for i,row in enumerate(partition['rows']) if row['subset']=='policy_audit']
        rows=validation.to_dict('records')
        result.update(partition=partition,thresholds=thresholds,policies={})
        for policy in selective.POLICIES:
            if policy in thresholds and any(v is None for v in thresholds[policy].values()):
                result['policies'][policy]={'status':'insufficient_threshold_data'};continue
            decisions=selective.apply_policy([rows[i] for i in audit],{t:[signals[t][i] for i in audit] for t in labels},policy,thresholds)
            result['policies'][policy]=selective.summarize(decisions)
    out.mkdir(parents=True)
    for task,winner in selection.items():joblib.dump(models[task][winner],out/f'{task}_pipeline.joblib')
    (out/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    return result
