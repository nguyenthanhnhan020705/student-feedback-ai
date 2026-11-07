"""Fill the *_sha256 fields of an experiment config from the model paths it names.

CT2/CT3 controls are produced by earlier experiments (class_weights -> word_char -> augmentation), so the
checksums can only be known after those runs. Example:

    python tools/fill_checksums.py configs/word_char.json --set ct2_models.sentiment=outputs/exp/class_weights/sentiment_pipeline.joblib ...

Writes a new config (never edits in place): --output <path>.
"""
import argparse
import hashlib
import json
from pathlib import Path


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('config', type=Path)
    parser.add_argument('--project-root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--set', action='append', default=[], metavar='KEY.TASK=PATH')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(argv)
    if args.output.exists():
        raise FileExistsError(args.output)
    config = json.loads(args.config.read_text(encoding='utf-8'))
    for item in args.set:
        target, path = item.split('=', 1)
        key, task = target.split('.')
        config[key][task] = path
    for key in [k for k in config if k.endswith('_models') or k == 'models']:
        prefix = 'model_sha256' if key == 'models' else key.replace('_models', '_sha256')
        config[prefix] = {task: sha256(args.project_root / path) for task, path in config[key].items()}
    args.output.write_text(json.dumps(config, indent=2) + '\n', encoding='utf-8')
    print(args.output)


if __name__ == '__main__':
    main()
