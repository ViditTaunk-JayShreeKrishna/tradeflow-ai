import joblib
import numpy as np
from pathlib import Path
from typing import Optional

MODEL_PATH = Path(__file__).parent / "models" / "hs_classifier.joblib"

# Module-level cache so the model loads only once
_model_data: Optional[dict] = None


def _load_model() -> bool:
    global _model_data
    if MODEL_PATH.exists():
        _model_data = joblib.load(MODEL_PATH)
        return True
    return False


def is_model_ready() -> bool:
    if _model_data is not None:
        return True
    return _load_model()


def predict(description: str) -> Optional[dict]:
    if not is_model_ready():
        return None

    pipeline = _model_data["pipeline"]
    proba = pipeline.predict_proba([description])[0]
    classes = pipeline.classes_

    # Top 3 predictions sorted by confidence
    top_indices = np.argsort(proba)[::-1][:3]

    return {
        "predicted_hs_code": classes[top_indices[0]],
        "confidence": float(proba[top_indices[0]]),
        "top_3": [
            {
                "hs_code": classes[i],
                "confidence": float(proba[i]),
            }
            for i in top_indices
        ],
        "model_version": _model_data.get("version", "1.0.0"),
    }