"""Explicit one-time migration helper; never imported by serving code."""
import hashlib
import json
from pathlib import Path

SOURCE=Path(__file__).resolve().parents[2]
TARGET=Path(__file__).resolve().parents[1]

def write(name, text):
    path=TARGET/name
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(text,encoding='utf-8')

inventory={p.relative_to(SOURCE).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
           for folder in ('demo_v3','demo_v2','ml','backend') for p in (SOURCE/folder).rglob('*')
           if p.is_file() and '__pycache__' not in p.parts}
write('outputs/migration/source-hashes.json',json.dumps(inventory,indent=2))
for name in ('api/routes','services','inference','data','training/experiments','evaluation','io','common','resources','web'):
    write('src/feedback_ai/'+name+'/__init__.py','')
for name in ('feedback_ai','ml','reports'):
    write('src/'+name+'/__init__.py','')
write('.gitignore','.venv/\n__pycache__/\n.pytest_cache/\n*.egg-info/\nbuild/\ndist/\noutputs/\nartifacts/**\ndata/**\n.env\n')
write('pyproject.toml','''[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"
[project]
name = "student-feedback-ai"
version = "0.1.0"
requires-python = ">=3.13,<3.14"
dependencies = ["fastapi", "uvicorn", "pydantic", "numpy", "scipy", "pandas", "scikit-learn==1.6.1", "joblib", "openpyxl==3.1.5"]
[project.scripts]
feedback-ai = "feedback_ai.cli:main"
[tool.setuptools.packages.find]
where = ["src"]
[tool.setuptools.package-data]
feedback_ai = ["resources/*.json", "web/*.html", "web/*.css", "web/*.js", "web/*.xlsx", "web/js/*.js"]
[tool.pytest.ini_options]
testpaths = ["tests"]
markers = ["integration: trusted local artifacts", "browser: actual browser"]
''')
write('src/feedback_ai/config.py','''from dataclasses import dataclass
from pathlib import Path
import os

@dataclass(frozen=True)
class Settings:
    root: Path
    @classmethod
    def from_root(cls, root):
        root = Path(root).resolve()
        if not root.is_dir():
            raise FileNotFoundError(root)
        return cls(root)
    @property
    def data_dir(self): return self.root / 'data'
    @property
    def artifacts_dir(self): return self.root / 'artifacts'
    @property
    def outputs_dir(self): return self.root / 'outputs'

def project_root():
    value = os.environ.get('FEEDBACK_PROJECT_ROOT')
    if not value:
        raise ValueError('Set FEEDBACK_PROJECT_ROOT or pass --project-root explicitly')
    return Settings.from_root(value).root
''')
write('src/feedback_ai/common/hashing.py','import hashlib\nfrom pathlib import Path\n\ndef digest(path):\n    return hashlib.sha256(Path(path).read_bytes()).hexdigest()\n')
write('src/feedback_ai/cli.py','''import argparse
def main(argv=None):
    parser=argparse.ArgumentParser(prog='feedback-ai')
    parser.add_argument('--project-root', required=True)
    parser.parse_args(argv)
    return 0
''')
write('requirements/lock.txt',(SOURCE/'requirements-lock.txt').read_text(encoding='utf-8')+'\nopenpyxl==3.1.5\net_xmlfile==2.0.0\n')
for name, packages in {'runtime':['fastapi','uvicorn','pydantic','numpy','scipy','pandas','scikit-learn','joblib','openpyxl'], 'train':['matplotlib','nbformat'], 'test':['pytest','httpx'], 'browser':['playwright']}.items():
    write('requirements/'+name+'.txt','-c lock.txt\n'+'\n'.join(packages)+'\n')
write('.env.example','FEEDBACK_PROJECT_ROOT=/absolute/path/to/student_feedback\n# Documentation only; .env is not automatically loaded.\n')
