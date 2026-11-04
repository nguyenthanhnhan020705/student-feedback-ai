"""Execute the plain-Python notebook cells and capture real stdout/stderr.

This dependency-free runner is not a Jupyter kernel; the notebook deliberately
uses no magics or rich display. Its code also runs in a matching Python kernel.
"""
import contextlib
import io
import json
import os
from pathlib import Path
import sys
import traceback

ROOT = Path(__file__).resolve().parents[2]


def main():
    path = ROOT / 'notebooks/03_topic.ipynb'
    notebook = json.loads(path.read_text(encoding='utf-8'))
    scope = {'__name__': '__main__'}
    os.chdir(ROOT)
    sys.path.insert(0, str(ROOT))
    count = 0
    for cell in notebook['cells']:
        if cell['cell_type'] == 'code':
            cell['outputs'] = []
            cell['execution_count'] = None
    try:
        for cell in notebook['cells']:
            if cell['cell_type'] != 'code':
                continue
            count += 1
            cell['execution_count'] = count
            out, err = io.StringIO(), io.StringIO()
            try:
                with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                    exec(compile(''.join(cell['source']), f'{path.name}:cell-{count}', 'exec'), scope)
            except Exception as exc:
                cell['outputs'].append({'output_type': 'error', 'ename': type(exc).__name__,
                                        'evalue': str(exc), 'traceback': traceback.format_exc().splitlines()})
                raise
            finally:
                for name, stream in [('stdout', out), ('stderr', err)]:
                    if stream.getvalue():
                        cell['outputs'].append({'output_type': 'stream', 'name': name,
                                                'text': stream.getvalue().splitlines(keepends=True)})
    finally:
        path.write_text(json.dumps(notebook, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        errors = sum(output['output_type'] == 'error' for cell in notebook['cells']
                     for output in cell.get('outputs', []))
        evidence = ROOT / 'reports/evidence/topic/notebook-execution.json'
        evidence.parent.mkdir(parents=True, exist_ok=True)
        evidence.write_text(json.dumps({'notebook': 'notebooks/03_topic.ipynb',
                                        'runner': 'plain-Python exec with captured streams; not Jupyter',
                                        'executed_code_cells': count, 'error_outputs': errors}, indent=2),
                            encoding='utf-8')
    print(f'Executed {count} code cells; {errors} error outputs')


if __name__ == '__main__':
    main()
