"""Import only the trusted frozen serving payload; verify every copied byte."""
import json
import shutil
from pathlib import Path
from feedback_ai.common.hashing import digest

def verify_manifest(path):
    path=Path(path).resolve()
    manifest=json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(manifest.get('files'),dict) or not manifest['files']:
        raise ValueError('Invalid bundle manifest')
    for name,checksum in manifest['files'].items():
        item=(path.parent/name).resolve()
        if not item.is_relative_to(path.parent) or not item.is_file() or digest(item)!=checksum:
            raise ValueError('Missing, redirected or modified bundle file: '+name)
    required={'ct4/receipt.json','ct5/receipt.json','ct5/config.json','ct5/thresholds.json'}
    required.update('ct4/research-selected/'+t+'_'+s for t in ('sentiment','topic') for s in ('pipeline.joblib','metadata.json'))
    if not required.issubset(manifest['files']):
        raise ValueError('Incomplete serving bundle')
    return manifest

def import_bundle(source_root, destination):
    source_root=Path(source_root).resolve(); destination=Path(destination).resolve()
    if destination.exists():raise FileExistsError(destination)
    files={}
    for family,folder,names in (
        ('ct4','ct4-augmentation/run-1',['receipt.json']+['research-selected/'+t+'_'+s for t in ('sentiment','topic') for s in ('pipeline.joblib','metadata.json')]),
        ('ct5','ct5-selective-prediction/run-1',['receipt.json','config.json','thresholds.json'])):
        for name in names:
            source=source_root/'.local-tools'/folder/name
            if not source.is_file():raise FileNotFoundError(source)
            files[family+'/'+name]=source
    destination.mkdir(parents=True)
    hashes={}
    for name,source in files.items():
        target=destination/name;target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(source,target);hashes[name]=digest(source)
    manifest=destination/'manifest.json'
    manifest.write_text(json.dumps({'schema':'feedback-bundle.1','files':hashes},indent=2),encoding='utf-8')
    verify_manifest(manifest)
    return manifest

def load_bundle(manifest):
    from feedback_ai.inference.frozen import FrozenModels
    return FrozenModels(Path(manifest).parent)
