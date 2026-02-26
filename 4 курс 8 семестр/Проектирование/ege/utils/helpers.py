from typing import Any
from datetime import datetime


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
