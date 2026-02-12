import sqlite3
import random
from datetime import datetime, timedelta
from typing import List
from models import ESMIRecord, Author

class Database:
    def __init__(self, db_path="esmi.db"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.init_db()

    def init_db(self):
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS authors (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    full_name TEXT NOT NULL,
                    role TEXT NOT NULL
                )
            """)
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS esmi_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    esmi_type TEXT NOT NULL,
                    channel TEXT NOT NULL,
                    date TEXT NOT NULL,
                    program TEXT NOT NULL,
                    topic TEXT,
                    author_id INTEGER NOT NULL,
                    annotation TEXT,
                    notes TEXT,
                    duration_min INTEGER NOT NULL,
                    rating REAL NOT NULL,
                    FOREIGN KEY (author_id) REFERENCES authors(id)
                )
            """)

    def add_author(self, full_name: str, role: str) -> int:
        with self.conn:
            cur = self.conn.execute(
                "INSERT INTO authors (full_name, role) VALUES (?, ?)",
                (full_name, role)
            )
            return cur.lastrowid

    def get_records_as_dicts(self):
        cur = self.conn.execute("""
            SELECT
                id, esmi_type, channel, date, program, topic, author_id,
                annotation, notes, duration_min, rating
            FROM esmi_records
        """)
        columns = [desc[0] for desc in cur.description]
        return [dict(zip(columns, row)) for row in cur.fetchall()]

    def get_authors(self) -> List[Author]:
        cur = self.conn.execute("SELECT id, full_name, role FROM authors")
        return [Author(id=row[0], full_name=row[1], role=row[2]) for row in cur.fetchall()]

    def add_record(self, record: ESMIRecord) -> int:
        with self.conn:
            cur = self.conn.execute("""
                INSERT INTO esmi_records (
                    esmi_type, channel, date, program, topic, author_id,
                    annotation, notes, duration_min, rating
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                record.esmi_type, record.channel, record.date, record.program, record.topic,
                record.author_id, record.annotation, record.notes, record.duration_min, record.rating
            ))
            return cur.lastrowid

    def get_records(self) -> List[ESMIRecord]:
        cur = self.conn.execute("""
            SELECT id, esmi_type, channel, date, program, topic, author_id,
                   annotation, notes, duration_min, rating
            FROM esmi_records
        """)
        return [
            ESMIRecord(
                id=r[0], esmi_type=r[1], channel=r[2], date=r[3], program=r[4], topic=r[5],
                author_id=r[6], annotation=r[7], notes=r[8], duration_min=r[9], rating=r[10]
            )
            for r in cur.fetchall()
        ]

    def delete_record(self, record_id: int):
        with self.conn:
            self.conn.execute("DELETE FROM esmi_records WHERE id = ?", (record_id,))

    def get_all_durations_and_ratings(self):
        cur = self.conn.execute("SELECT duration_min, rating FROM esmi_records")
        return [(r[0], r[1]) for r in cur.fetchall()]

# В конец файла database.py

    def has_records(self) -> bool:
        cur = self.conn.execute("SELECT COUNT(*) FROM esmi_records")
        return cur.fetchone()[0] > 0

    def setup_sample_data(self):
        if self.has_records():
            return

        # Добавляем авторов
        authors_data = [
            ("Иванов И.И.", "журналист"),
            ("Петров П.П.", "депутат"),
            ("Сидорова А.В.", "корреспондент"),
            ("Козлов Д.С.", "работник администрации"),
            ("Морозова Е.Н.", "активист партии"),
        ]
        author_ids = {}
        for name, role in authors_data:
            aid = self.add_author(name, role)
            author_ids[name] = aid

        # Добавляем записи ЭСМИ
        esmi_records_data = []
        base_date = datetime(2024, 1, 1)
        for i in range(30):
            esmi_type = random.choice(["радио", "телевидение", "интернет"])
            channel = random.choice(["Первый", "Радио Свобода", "РИА Новости", "ТВ Центр", "Медуза"])
            date = (base_date + timedelta(days=i)).strftime("%Y-%m-%d")
            program = f"Эфир №{i+1}"
            topic = random.choice(["Политика", "Экономика", "Общество", "Культура", "Спорт"])
            author_name = random.choice(list(author_ids.keys()))
            author_id = author_ids[author_name]
            annotation = f"Анализ событий от {author_name}"
            notes = "Тестовая запись"
            # Генерируем коррелирующие данные: чем дольше передача, тем выше рейтинг (с шумом)
            duration = random.randint(10, 60)
            rating = max(0.0, min(10.0, 2.0 + 0.12 * duration + random.gauss(0, 0.8)))

            esmi_records_data.append(ESMIRecord(
                id=0,
                esmi_type=esmi_type,
                channel=channel,
                date=date,
                program=program,
                topic=topic,
                author_id=author_id,
                annotation=annotation,
                notes=notes,
                duration_min=duration,
                rating=round(rating, 1)
            ))

        # Сохраняем в БД
        for record in esmi_records_data:
            self.add_record(record)

        print("✅ Добавлены тестовые данные (30 записей, 5 авторов).")
