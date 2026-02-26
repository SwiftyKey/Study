import sqlite3
import json
from typing import List, Dict, Optional, Any
from config.settings import DB_PATH


class DatabaseManager:
    def __init__(self):
        self.db_path = DB_PATH
        self.init_db()

    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS t_task (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                c_img_path TEXT,
                c_answer TEXT,
                c_score INTEGER
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

    def add_task(self, img_path: str, answer: Any, score: int) -> int:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        answer_str = json.dumps(answer) if isinstance(answer, (list, dict)) else str(answer)
        c.execute(
            "INSERT INTO t_task (c_img_path, c_answer, c_score) VALUES (?, ?, ?)",
            (str(img_path), answer_str, score)
        )
        task_id = c.lastrowid
        conn.commit()
        conn.close()
        return task_id

    def add_tasks_batch(self, tasks: List[Dict[str, Any]]) -> int:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        count = 0
        for task in tasks:
            answer_str = json.dumps(task['answer']) if isinstance(task['answer'], (list, dict)) else str(task['answer'])
            c.execute(
                "INSERT INTO t_task (id, c_img_path, c_answer, c_score) VALUES (?, ?, ?, ?)",
                (int(task['id']), str(task['img_path']), answer_str, int(task['score']))
            )
            count += 1
        conn.commit()
        conn.close()
        return count

    def clear_tasks(self) -> bool:
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute("DELETE FROM t_task")
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
