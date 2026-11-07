"""Explicit dataset import, validation, acquisition and EDA."""
from pathlib import Path
import json
import shutil
from feedback_ai.data.loader import load_dataset,inspect_data

def import_data(source,destination):
    source=Path(source);destination=Path(destination)
    if destination.exists():raise FileExistsError(destination)
    load_dataset(source)
    for split in ('train','validation','test'):
        folder=source/split
        if split=='validation' and not folder.exists():folder=source/'dev'
        for name in ('sents.txt','sentiments.txt','topics.txt'):
            target=destination/split/name;target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(folder/name,target)
    return validate(destination,destination.parent/'manifest.json')

def validate(data_dir,output):
    # Optional provenance: <data>/source.json (beside raw/) records the pinned source and per-file hashes.
    recorded=Path(data_dir).parent/'source.json'
    source=json.loads(recorded.read_text(encoding='utf-8')) if recorded.is_file() else None
    report=inspect_data(data_dir,source=source)
    output=Path(output);output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    return report

def eda(data_dir,output):
    output=Path(output)
    if output.exists():raise FileExistsError(output)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    frames=load_dataset(data_dir);output.mkdir(parents=True)
    summary={}
    for split,frame in frames.items():
        summary[split]={'rows':len(frame),'length':frame.text.str.len().describe().to_dict()}
        for task in ('sentiment','topic'):
            counts=frame[task].value_counts();counts.to_csv(output/f'{split}-{task}.csv')
            fig,ax=plt.subplots();counts.plot.bar(ax=ax);ax.set_title(f'{split}: {task}')
            fig.tight_layout();fig.savefig(output/f'{split}-{task}.png');plt.close(fig)
    (output/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    return summary

def acquire(destination):
    """Download pinned source only when explicitly invoked; no remote code execution."""
    import ast
    from urllib.request import urlopen
    import tempfile
    destination=Path(destination)
    if destination.exists():raise FileExistsError(destination)
    base='https://huggingface.co/datasets/uitnlp/vietnamese_students_feedback/resolve/7b56c6cb1c9c8523249f407044c838660df3811a'
    with urlopen(base+'/vietnamese_students_feedback.py',timeout=90) as response:script=response.read()
    tree=ast.parse(script.decode('utf-8'))
    assignment=next(n for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='_URLS' for t in n.targets))
    with tempfile.TemporaryDirectory() as temp:
        root=Path(temp)
        for key,node in zip(assignment.value.keys,assignment.value.values):
            split={'TRAIN':'train','VALIDATION':'validation','TEST':'test'}[key.attr]
            for name,url in ast.literal_eval(node).items():
                name={'sentences':'sents.txt','sentiments':'sentiments.txt','topics':'topics.txt'}[name]
                with urlopen(url.replace('down load','download'),timeout=90) as response:raw=response.read()
                if raw.lstrip().lower().startswith((b'<!doctype',b'<html')):raise ValueError('Received HTML, not dataset')
                file=root/split/name;file.parent.mkdir(parents=True,exist_ok=True);file.write_bytes(raw)
        return import_data(root,destination)
