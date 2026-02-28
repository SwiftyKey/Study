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
        return self.tasks

    def set_student_info(self, number: str):
        info = self.db.get_student_by_number(number)
        if info is None:
            raise Exception("Не найден участник с таким номером")
        self.student_info = {
            "school": info['c_school'],
            "class": info['c_class'],
            "fio": info['c_fio']
        }

    def save_answer(self, task_id: int, answer: Any):
        if answer in ['', ',', None]:
            answer = None
        self.answers[task_id] = answer

    def get_answer(self, task_id: int) -> Any:
        return self.answers.get(task_id, "")

    def calculate_results(self) -> Tuple[int, int, List[Dict[str, Any]]]:
        total_score = 0
        max_score = 0
        total_test_score = 0
        table_map = {
            0: 0, 1: 7, 2: 14, 3: 20, 4: 27, 5: 34, 6: 40,
            7: 43, 8: 46, 9: 48, 10: 51, 11: 54, 12: 56,
            13: 59, 14: 62, 15: 64, 16: 67, 17: 70,
            18: 72, 19: 75, 20: 78, 21: 80, 22: 83,
            23: 85, 24: 88, 25: 90, 26: 93, 27: 95, 28: 98, 29: 100
        }
        results = []
        print(self.answers)

        for task in self.tasks:
            task_id = task['id']
            correct_answer = task['c_answer']
            user_answer = self.answers.get(task_id, "")
            if user_answer is None:
                user_answer = ''
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

        total_test_score = table_map[total_score]

        return total_score, max_score, total_test_score, 100, results

    def save_results_to_csv(self, results: List[Dict[str, Any]], total_score: int, total_test_score: int) -> str:
        from utils.helpers import generate_student_filename
        import csv

        filename = generate_student_filename(self.student_info['school'], self.student_info['class'], self.student_info['fio'])

        row = {
            "school": self.student_info['school'],
            "class": self.student_info['class'],
            "fio": self.student_info['fio'],
            "total_score": total_score,
            "total_test_score": total_test_score
        }

        for res in results:
            tid = res['task_id']
            u_ans = res['user_answer']
            if u_ans is not None and ',' in u_ans:
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
