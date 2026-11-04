from pathlib import Path
import asyncio
import json
import os
import sys
import nbformat
from nbclient import NotebookClient

root = Path(__file__).resolve().parents[2]
os.environ['IPYTHONDIR'] = str(root / '.local-tools/ipython')
os.environ['JUPYTER_PATH'] = str(root / '.venv/share/jupyter')
os.environ['MPLCONFIGDIR'] = str(root / '.local-tools/matplotlib')
os.environ['MPLBACKEND'] = 'Agg'
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
path = root / 'notebooks/01_eda.ipynb'
notebook = nbformat.read(path, as_version=4)
client = NotebookClient(notebook, timeout=180, kernel_name='tv2-local', resources={'metadata': {'path': str(root)}})
client.execute()
nbformat.validate(notebook)
nbformat.write(notebook, path)
summary = {'notebook': 'notebooks/01_eda.ipynb', 'code_cells': len([c for c in notebook.cells if c.cell_type == 'code']),
           'error_outputs': sum(o.output_type == 'error' for c in notebook.cells if c.cell_type == 'code' for o in c.outputs),
           'executed': all(c.execution_count is not None for c in notebook.cells if c.cell_type == 'code')}
(root / 'reports/evidence/data/notebook-execution.json').write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
print(json.dumps(summary))
