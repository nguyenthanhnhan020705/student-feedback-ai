"""Read-only CT4 artifacts and fixed CT5 q10 thresholds, bound to frozen hashes."""
import math
from pathlib import Path

from feedback_ai.inference.model_loader import ModelService
from feedback_ai.common.json_io import read
from feedback_ai.common.hashing import digest
from feedback_ai.inference.signals import extract_signals
from feedback_ai.inference.policy import LABELS, make_prediction, finite_nonnegative




def read_object(path):
    value = read(path)
    if not isinstance(value,dict):
        raise ValueError('Provenance must be a JSON object')
    return value


class FrozenModels:
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.ready = False
        self.status = {task:'invalid' for task in LABELS}
        self.thresholds, self.model_hashes, self.models = {}, {}, {}
        try:
            from feedback_ai.inference.bundle import verify_manifest
            verify_manifest(self.root/'manifest.json')
            ct4 = self.root/'ct4'
            ct5 = self.root/'ct5'
            directory = ct4/'research-selected'
            if any(p.resolve() != p for p in (ct4,ct5,directory)):
                raise ValueError('Redirected frozen source')
            receipt = read_object(ct5/'receipt.json')
            if (receipt.get('schema_version') != 'ct5.1' or receipt.get('promotion') != 'not_deployed'
                    or receipt.get('deployment') != 'offline_research_only'):
                raise ValueError('Invalid CT5 source receipt')
            for name in ('config.json','thresholds.json'):
                path = ct5/name
                if path.resolve() != path or digest(path) != receipt['payload'][name]:
                    raise ValueError('Frozen policy payload changed')
            config = read_object(ct5/'config.json')
            if (config.get('schema_version') != 'ct5.1'
                    or digest(ct5/'config.json') != receipt['config_sha256']
                    or digest(ct4/'receipt.json') != config['control_receipts']['ct4']):
                raise ValueError('CT4/policy provenance changed')
            parent = read_object(ct4/'receipt.json')
            if (parent.get('schema_version') != 'ct4.1' or parent.get('promotion') != 'not_deployed'
                    or parent.get('deployment') != 'research_only'):
                raise ValueError('Invalid frozen CT4 receipt')
            thresholds = read_object(ct5/'thresholds.json')['ct4']['zero_plus_margin_q10']
            if (not isinstance(thresholds,dict) or set(thresholds) != set(LABELS)
                    or any(not finite_nonnegative(v) for v in thresholds.values())):
                raise ValueError('Invalid fixed per-task thresholds')
            expected = config['models']['ct4']
            actual = {}
            for task in LABELS:
                for suffix in ('pipeline.joblib','metadata.json'):
                    name = f'{task}_{suffix}'
                    path = directory/name
                    if path.resolve() != path:
                        raise ValueError('Redirected model')
                    actual[name] = digest(path)
                    if actual[name] != expected[name]:
                        raise ValueError('CT4 model hashes differ')
            service = ModelService(directory)
            self.status = service.status.copy()
            if not service.loaded:
                raise ValueError('CT4 runtime/readiness invalid')
            self.models = {task: getattr(service, task+'_model') for task in LABELS}
            self.thresholds, self.model_hashes = thresholds, actual
            self.ready = True
        except (OSError, ValueError, KeyError, TypeError):
            self.ready = False

    def predict(self, text):
        if not self.ready:
            raise RuntimeError('CT4 demo not ready')
        signals = {task: extract_signals(pipe, [text], task)[0] for task, pipe in self.models.items()}
        return make_prediction(signals, self.thresholds)
