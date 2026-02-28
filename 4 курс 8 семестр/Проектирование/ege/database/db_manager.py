import sqlite3
import json
from typing import List, Dict, Optional, Any
from config.settings import DB_PATH


class DatabaseManager:
    def __init__(self, db_path=None):
        if db_path is None:
            from utils.helpers import get_db_path
            self.db_path = get_db_path()
        else:
            self.db_path = db_path
        self.init_db()

    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS t_task (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                c_answer TEXT,
                c_score INTEGER
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS t_student (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                c_school TEXT,
                c_class TEXT,
                c_fio TEXT,
                c_number TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def get_all_tasks(self) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM t_task ORDER BY id")
        tasks = [dict(row) for row in c.fetchall()]
        conn.close()
        return tasks

    def get_task_by_id(self, task_id: int) -> Optional[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM t_task WHERE id = ?", (task_id,))
        row = c.fetchone()
        conn.close()
        return dict(row) if row else None

    def get_student_by_number(self, number: int) -> Optional[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM t_student WHERE c_number = ?", (number,))
        row = c.fetchone()
        conn.close()
        return dict(row) if row else None

    def add_tasks_batch(self, tasks: List[Dict[str, Any]]) -> int:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        count = 0
        for task in tasks:
            answer_str = json.dumps(task['answer']) if isinstance(task['answer'], (list, dict)) else str(task['answer'])
            c.execute(
                "INSERT INTO t_task (id, c_answer, c_score) VALUES (?, ?, ?)",
                (int(task['id']), answer_str, int(task['score']))
            )
            count += 1
        conn.commit()
        conn.close()
        return count

    def add_students_batch(self, students: List[Dict[str, Any]]) -> int:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        count = 0
        query = """INSERT INTO t_student (c_school, c_class, c_fio, c_number) VALUES"""
        for student in students:
            query += f"""\n("{student['c_school']}", "{student['c_class']}", "{student['c_fio']}", "{student['c_number']}"),"""
            count += 1
        query = query[:-1] + ';'
        c.execute(query)
        conn.commit()
        conn.close()
        return count

    def clear_tasks(self) -> bool:
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute("DELETE FROM t_task")
            c.execute("DELETE FROM t_student")
            conn.commit()
            conn.close()
            return True
        except Exception:
            return False

    def get_tasks_count(self) -> int:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM t_task")
        count = c.fetchone()[0]
        conn.close()
        return count
