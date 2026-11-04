"""Preserve original evidence and replay frozen controls without fitting."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
BACKUP = ROOT / '.local-tools/ct4-multilabel-backup'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def preserve():
    inventory = json.loads((OUT / 'preexisting.json').read_text(encoding='utf-8'))
    restored, changed, snapshots = [], [], {}
    for name, expected in inventory.items():
        original = ROOT / name
        if original.is_file() and digest(original) == expected:
            continue
        # Only browser evidence which tests legitimately refresh may be restored.
        browser = (name.startswith('reports/evidence/frontend/')
                   or name.startswith('reports/evidence/phase-4/')
                   or name.startswith('reports/evidence/ct4-partial-demo/browser/'))
        backup = BACKUP / name
        if (browser and original.suffix in ('.png', '.json') and original.is_file()
                and original.resolve() == original and backup.is_file()
                and digest(backup) == expected):
            target = OUT / 'historical-browser-refresh' / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(original, target)
            snapshots[target.relative_to(OUT).as_posix()] = digest(target)
            shutil.copyfile(backup, original)
            restored.append(name)
        else:
            changed.append(name)
    result = dict(total=len(inventory), matched=len(inventory)-len(changed),
                  changed=changed, restored_verified_browser_bytes=restored,
                  refreshed_evidence=snapshots)
    (OUT / 'preservation.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k != 'refreshed_evidence'}, indent=2))
    if changed:
        raise RuntimeError('Unexpected original changes; not restored: '+repr(changed))


def replay():
    modules = ('ct_evaluation', 'ct2_class_weights', 'ct3_word_char',
               'ct4_augmentation', 'ct5_selective_prediction')
    results = []
    for module in modules:
        # Fresh interpreter per historical control. These assignments cannot fit.
        code = """
import sys,runpy
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
def forbidden(*args,**kwargs): raise AssertionError('No-fit historical replay')
for cls in (Pipeline,FeatureUnion,TfidfVectorizer,LinearSVC,LogisticRegression,MultinomialNB):
    cls.fit=forbidden
    if hasattr(cls,'fit_transform'): cls.fit_transform=forbidden
sys.argv=[sys.argv[1],'verify']
runpy.run_module('reports.'+sys.argv[0],run_name='__main__')
"""
        completed = subprocess.run([sys.executable, '-B', '-c', code, module], cwd=ROOT,
                                   capture_output=True, text=True, encoding='utf-8', errors='replace')
        (OUT / f'replay-{module}.txt').write_text(completed.stdout+completed.stderr, encoding='utf-8')
        results.append(dict(module=module, exit_code=completed.returncode, fit=False))
        print(json.dumps(results[-1]), flush=True)
        if completed.returncode:
            raise RuntimeError('Historical replay failed: '+module)
    (OUT / 'historical-replay.json').write_text(json.dumps(results, indent=2), encoding='utf-8')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=('preserve', 'replay'))
    args = parser.parse_args()
    preserve() if args.action == 'preserve' else replay()
