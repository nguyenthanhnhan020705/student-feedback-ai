import subprocess
import sys

import pytest


@pytest.mark.parametrize('module', ['train_sentiment', 'train_topic', 'evaluate'])
def test_cli_help_and_honest_unimplemented_status(module):
    command = [sys.executable, '-m', f'ml.{module}']
    help_result = subprocess.run(command + ['--help'], capture_output=True, text=True)
    assert help_result.returncode == 0
    result = subprocess.run(command, capture_output=True, text=True)
    assert result.returncode != 0
    assert 'chua' in result.stderr.lower()
