from pathlib import Path


def test_paths_do_not_follow_cwd(tmp_path, monkeypatch):
    from feedback_ai.config import Settings
    root = tmp_path/'project'
    root.mkdir()
    settings = Settings.from_root(root)
    monkeypatch.chdir(tmp_path)
    assert settings.data_dir == root/'data'
    assert settings.artifacts_dir == root/'artifacts'
    assert settings.outputs_dir == root/'outputs'


def test_missing_root_is_reported(tmp_path):
    import pytest
    from feedback_ai.config import Settings
    with pytest.raises(FileNotFoundError):
        Settings.from_root(tmp_path/'missing')
