"""Local acquisition of the exact UIT-NLP source, without executing its script."""
from pathlib import Path
from urllib.request import urlopen
from datetime import datetime, timezone
import ast
import hashlib
import json

REVISION = '7b56c6cb1c9c8523249f407044c838660df3811a'
BASE = f'https://huggingface.co/datasets/uitnlp/vietnamese_students_feedback/resolve/{REVISION}'
ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / 'reports/evidence/data'
RAW = ROOT / 'data/raw'
EVIDENCE.mkdir(parents=True, exist_ok=True)

def fetch(url):
    with urlopen(url, timeout=90) as response:
        return response.read()

script = fetch(BASE + '/vietnamese_students_feedback.py')
(EVIDENCE / 'uitnlp-loader-source.py.txt').write_bytes(script)
(EVIDENCE / 'uitnlp-dataset-card.md').write_bytes(fetch(BASE + '/README.md'))
tree = ast.parse(script.decode('utf-8'))
assignment = next(node for node in tree.body if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == '_URLS' for target in node.targets))
files = []
for key, split_node in zip(assignment.value.keys, assignment.value.values):
    split = {'TRAIN': 'train', 'VALIDATION': 'dev', 'TEST': 'test'}[key.attr]
    mapping = ast.literal_eval(split_node)
    for source_name, source_url in mapping.items():
        filename = {'sentences': 'sents.txt', 'sentiments': 'sentiments.txt', 'topics': 'topics.txt'}[source_name]
        # Correct a typo in the source loader's query; retain both URLs in evidence.
        url = source_url.replace('down load', 'download')
        path = RAW / split / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        content = fetch(url)
        if content.lstrip().startswith((b'<!DOCTYPE', b'<html')):
            raise ValueError(f'HTML received instead of dataset: {split}/{filename}')
        path.write_bytes(content)
        files.append({'path': path.relative_to(RAW).as_posix(), 'source_url': source_url,
                      'download_url': url, 'sha256': hashlib.sha256(content).hexdigest(),
                      'file_bytes': len(content)})
        print(f'{split}/{filename}: {len(content)} bytes', flush=True)
source = {'url': 'https://huggingface.co/datasets/uitnlp/vietnamese_students_feedback',
          'revision': REVISION, 'retrieved_at': datetime.now(timezone.utc).isoformat(),
          'permission_evidence': 'reports/evidence/data/uitnlp-dataset-card.md',
          'license_status': 'unknown', 'approval_status': 'pending_leader_review',
          'source_loader_sha256': hashlib.sha256(script).hexdigest(),
          'acquisition': 'Exact bytes from Google Drive URLs in pinned UIT-NLP loader; no remote code execution',
          'files': files}
(ROOT / 'reports/data/source.json').write_text(json.dumps(source, indent=2) + '\n', encoding='utf-8')
