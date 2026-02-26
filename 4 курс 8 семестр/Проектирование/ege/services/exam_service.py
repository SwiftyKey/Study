import csv
from typing import Dict, List, Any, Tuple
from database.db_manager import DatabaseManager
from utils.helpers import compare_answers
from utils.internet_blocker import InternetBlocker


class ExamService:
    def __init__(self):
        self.db = DatabaseManager()
        self.blocker = InternetBlocker()
        self.student_info = {}
        self.answers = {}
        self.tasks = []

    def load_tasks(self) -> List[Dict[str, Any]]:
        self.tasks = self.db.get_all_tasks()
        for task in self.tasks:
            task['c_answer'] = task['c_answer']
        return self.tasks

    def set_student_info(self, school: str, class_name: str, fio: str):
        self.student_info = {
            "school": school,
            "class": class_name,
            "fio": fio
        }

    def save_answer(self, task_id: int, answer: Any):
        self.answers[task_id] = answer

    def get_answer(self, task_id: int) -> Any:
        return self.answers.get(task_id, "")

    def calculate_results(self) -> Tuple[int, int, List[Dict[str, Any]]]:
        total_score = 0
        max_score = 0
        results = []

        for task in self.tasks:
            task_id = task['id']
            correct_answer = task['c_answer']
            user_answer = self.answers.get(task_id, "")
            score = task['c_score']
            max_score += score

            is_correct = compare_answers(user_answer, correct_answer, task_id)

            if is_correct:
                total_score += score

            results.append({
                "task_id": task_id,
                "user_answer": user_answer,
                "correct_answer": correct_answer,
                "is_correct": is_correct,
                "score": score if is_correct else 0
            })

        return total_score, max_score, results

    def save_results_to_csv(self, results: List[Dict[str, Any]], total_score: int, max_score: int) -> str:
        from utils.helpers import generate_student_filename
        import csv

        filename = generate_student_filename(self.student_info['school'], self.student_info['class'], self.student_info['fio'])

        row = {
            "school": self.student_info['school'],
            "class": self.student_info['class'],
            "fio": self.student_info['fio'],
            "total_score": total_score,
            "max_score": max_score
        }

        for res in results:
            tid = res['task_id']
            u_ans = res['user_answer']
            if ',' in u_ans:
                u_ans = f'"{u_ans}"'

            row[str(tid)] = u_ans
            row[f"correctness_{tid}"] = 1 if res['is_correct'] else 0

        fieldnames = list(row.keys())

        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow(row)

        return filename

    def start_exam_session(self) -> Tuple[bool, str]:
        success, message = self.blocker.apply()
        return success, message

    def end_exam_session(self) -> Tuple[bool, str]:
        success, message = self.blocker.remove()
        return success, message
