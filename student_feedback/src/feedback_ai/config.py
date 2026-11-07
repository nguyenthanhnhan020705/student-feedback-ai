from dataclasses import dataclass
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
