import os
from pathlib import Path

# Đường dẫn gốc tới repo
BASE_DIR = Path(__file__).resolve().parent.parent

# Đường dẫn chứa file mô hình ML (mặc định trỏ về <repo>/models)
MODEL_DIR = os.getenv("SFAI_MODEL_DIR", str(BASE_DIR / "models"))