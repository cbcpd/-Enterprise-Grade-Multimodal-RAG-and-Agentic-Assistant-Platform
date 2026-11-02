import json
from pathlib import Path
from datetime import datetime, timezone
from app.config import settings

def save_feedback(payload: dict):
    path = Path(settings.feedback_file)
    path.parent.mkdir(parents=True, exist_ok=True)
    record = {**payload, "created_at": datetime.now(timezone.utc).isoformat()}
    with path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(record, ensure_ascii=False) + "\n")
