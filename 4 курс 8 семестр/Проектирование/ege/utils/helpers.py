from typing import Any
from datetime import datetime
import sys
from pathlib import Path


def get_app_path() -> Path:
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent
    else:
        return Path(__file__).parent.parent


def get_images_path() -> Path:
    return get_app_path() / "images"


def get_task_image_path(task_id: int) -> Path:
    images_dir = get_images_path()

    for ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp']:
        img_path = images_dir / f"{task_id}{ext}"
        if img_path.exists():
            return img_path

    return images_dir / f"{task_id}.png"


def format_time(minutes: int) -> str:
    h, remainder = divmod(minutes, 60)
    m, s = divmod(remainder, 60)
    return f"{h:02}:{m:02}:{s:02}"


def generate_student_filename(school: str, class_name: str, fio: str) -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_fio = "".join(c for c in fio if c.isalnum() or c in " _-").strip()
    safe_school = "".join(c for c in school if c.isalnum() or c in " _-").strip()
    return f"student_answers_{safe_fio}_{safe_school}_{class_name}_{timestamp}.csv"


def compare_answers(user_answer: Any, correct_answer: Any, task_id: int) -> bool:
    return str(user_answer).strip().lower() == str(correct_answer).strip().lower()
