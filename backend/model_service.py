from pathlib import Path
import joblib
from backend.config import MODEL_DIR

class ModelService:
    def __init__(self, model_dir: str = MODEL_DIR):
        self.model_dir = Path(model_dir)
        self.sentiment_model = None
        self.topic_model = None
        self.loaded = False
        self.reload()

    def reload(self):
        s_path = self.model_dir / "sentiment_pipeline.joblib"
        t_path = self.model_dir / "topic_pipeline.joblib"

        # Chỉ load khi cả 2 file artifact mô hình thật đã tồn tại
        if s_path.exists() and t_path.exists():
            try:
                self.sentiment_model = joblib.load(s_path)
                self.topic_model = joblib.load(t_path)
                self.loaded = True
            except Exception:
                self.loaded = False
        else:
            self.loaded = False

    def predict(self, text: str) -> dict:
        if not self.loaded or not self.sentiment_model or not self.topic_model:
            return None
        sentiment_pred = self.sentiment_model.predict([text])[0]
        topic_pred = self.topic_model.predict([text])[0]
        return {
            "text": text,
            "sentiment": str(sentiment_pred),
            "topic": str(topic_pred)
        }

model_service = ModelService()