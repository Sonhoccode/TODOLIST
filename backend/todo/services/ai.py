import os
import joblib
import threading
import numpy as np

DEFAULT_MODEL_PATH = os.getenv("AI_MODEL_PATH", os.path.join(os.path.dirname(__file__), "model.pkl"))

class _ModelHolder:
    _instance = None
    _lock = threading.Lock()

    @classmethod
    def get(cls, path=DEFAULT_MODEL_PATH):
        """Singleton – chỉ load model một lần duy nhất."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = joblib.load(path)
        return cls._instance


def features_from_task(task, extra_data=None):
    """
    Trích xuất đặc trưng đầu vào từ task hoặc JSON request.
    extra_data: dict (ví dụ từ request body)
    """
    # Ưu tiên lấy từ extra_data (khi test Postman)
    if extra_data:
        duration_min = float(extra_data.get("duration_min", 60))
        start_hour = int(extra_data.get("start_hour", 9))
        day_of_week = int(extra_data.get("day_of_week", 2))
    else:
        # fallback nếu chỉ có task object
        duration_min = getattr(task, "effective_duration_min", 60)
        start_hour = getattr(task, "start_hour", 9)
        day_of_week = getattr(task, "day_of_week", 2)

    # Lấy priority numeric
    if hasattr(task, "priority_numeric"):
        priority = task.priority_numeric() if callable(task.priority_numeric) else task.priority_numeric
    else:
        pri_map = {"low": 1, "medium": 2, "high": 3}
        priority = pri_map.get(getattr(task, "priority", "medium"), 2)

    return [duration_min, priority, start_hour, day_of_week]


def predict_task_on_time(task, extra_data=None, return_confidence=False):
    """
    Dự đoán task có hoàn thành đúng hạn không.
    - task: instance hoặc object giả
    - extra_data: dict JSON (khi test API)
    - return_confidence: bool → trả thêm xác suất nếu True
    """
    model = _ModelHolder.get()
    feats = [features_from_task(task, extra_data)]
    pred = model.predict(feats)[0]

    if return_confidence and hasattr(model, "predict_proba"):
        prob = model.predict_proba(feats)[0][1]
        return {"on_time_prediction": int(pred), "confidence": round(float(prob), 2)}

    return int(pred)
