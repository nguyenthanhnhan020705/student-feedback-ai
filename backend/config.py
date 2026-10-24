
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Đường dẫn mặc định: thư mục <repo>/models
MODEL_DIR = Path(os.getenv("SFAI_MODEL_DIR", str(BASE_DIR / "models")))
