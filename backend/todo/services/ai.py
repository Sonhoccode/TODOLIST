# todo/services/ai.py
import os
import threading
import logging

logger = logging.getLogger(__name__)

# Try to import AI dependencies
try:
    import joblib
    import numpy as np
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
    logger.warning("AI dependencies (joblib, numpy) not installed. AI features will use fallback.")

# AI_MODEL_PATH: đường dẫn tới file model.pkl (train trước)
DEFAULT_MODEL_PATH = os.getenv(
    "AI_MODEL_PATH",
    os.path.join(os.path.dirname(__file__), "model.pkl"),
)


class _ModelHolder:
    _instance = None
    _lock = threading.Lock()
    _load_failed = False

    @classmethod
    def get(cls, path=DEFAULT_MODEL_PATH):
        """Singleton – chỉ load model một lần duy nhất."""
        if cls._load_failed:
            return None
            
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    try:
                        if not AI_AVAILABLE:
                            logger.warning("AI dependencies not available")
                            cls._load_failed = True
                            return None
                            
                        if not os.path.exists(path):
                            logger.warning(f"AI model file not found: {path}")
                            cls._load_failed = True
                            return None
                            
                        cls._instance = joblib.load(path)
                        logger.info("AI model loaded successfully")
                    except Exception as e:
                        logger.error(f"Failed to load AI model: {e}")
                        cls._load_failed = True
                        return None
        return cls._instance


def features_from_task(task, extra_data=None):
    """
    Trích xuất đặc trưng đầu vào từ task hoặc JSON request.
    extra_data: dict (ví dụ từ request body)
    """
    if extra_data:
        # Ưu tiên dùng estimated_duration_min (đúng với FE hiện tại)
        raw_duration = (
            extra_data.get("estimated_duration_min")
            or extra_data.get("duration_min")
            or 60
        )
        duration_min = float(raw_duration)
        start_hour = int(extra_data.get("start_hour", 9))
        day_of_week = int(extra_data.get("day_of_week", 2))
    else:
        duration_min = getattr(task, "effective_duration_min", 60)
        start_hour = getattr(task, "start_hour", 9)
        day_of_week = getattr(task, "day_of_week", 2)

    # Priority numeric
    if hasattr(task, "priority_numeric"):
        priority = (
            task.priority_numeric()
            if callable(task.priority_numeric)
            else task.priority_numeric
        )
    else:
        pri_map = {"low": 1, "medium": 2, "high": 3, "urgent": 3}
        priority = pri_map.get(
            str(getattr(task, "priority", "medium")).lower(),
            2,
        )

    return [duration_min, priority, start_hour, day_of_week]


def predict_task_on_time(task, extra_data=None, return_confidence=False):
    """
    Dự đoán task có hoàn thành đúng hạn không.
    - task: instance hoặc object giả
    - extra_data: dict JSON (khi test API)
    - return_confidence: bool → trả thêm xác suất nếu True
    """
    model = _ModelHolder.get()
    
    # Fallback: nếu model không load được, dùng heuristic đơn giản
    if model is None:
        logger.warning("Using fallback prediction (model not available)")
        feats = features_from_task(task, extra_data)
        duration_min, priority, start_hour, day_of_week = feats
        
        # Simple heuristic: dựa vào duration và priority
        # Ngắn + priority thấp = dễ hoàn thành
        score = 0.7  # base score
        
        if duration_min < 60:
            score += 0.15
        elif duration_min > 180:
            score -= 0.2
            
        if priority >= 3:  # High/Urgent
            score += 0.1
        elif priority == 1:  # Low
            score -= 0.1
            
        # Weekend thì khó hoàn thành hơn
        if day_of_week in [6, 7]:
            score -= 0.05
            
        # Giờ làm việc tốt hơn
        if 9 <= start_hour <= 17:
            score += 0.05
            
        score = max(0.1, min(0.95, score))  # clamp between 0.1 and 0.95
        
        if return_confidence:
            return {
                "on_time_prediction": score,
                "confidence": 0.5,  # Low confidence for fallback
                "fallback": True,
            }
        return score
    
    # Normal prediction with model
    feats = [features_from_task(task, extra_data)]
    pred = model.predict(feats)[0]

    if return_confidence and hasattr(model, "predict_proba"):
        prob = model.predict_proba(feats)[0][1]
        return {
            "on_time_prediction": float(prob),
            "confidence": round(float(prob), 2),
            "fallback": False,
        }

    return int(pred)
