import flet as ft
import csv
from pathlib import Path
from typing import Optional
from config.settings import COLOR_BG, COLOR_ACTIVE, COLOR_TEXT, COLOR_SURFACE, DB_PASSWORD
from database.db_manager import DatabaseManager
from ui.components import create_elevated_button, create_text_field, create_scrollable_column


class TasksParserApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.db = DatabaseManager()
        self.students_path: Optional[Path] = None
        self.csv_path: Optional[Path] = None

        self._setup_page()
        self._create_pickers()
        self._build_login_view()

    def _setup_page(self):
        self.page.title = "Загрузчик заданий ЕГЭ"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.bgcolor = COLOR_BG

    def _create_pickers(self):
        self.student_picker = ft.FilePicker(on_result=self._on_student_picked)
        self.csv_picker = ft.FilePicker(on_result=self._on_csv_picked)
        self.page.overlay.extend([self.csv_picker, self.student_picker])

    def _build_login_view(self):
        self.pw_field = create_text_field("Пароль администратора", password=True, width=300)
        self.btn_login = create_elevated_button("Войти", on_click=self._check_password)

        self.login_view = ft.Column([
            ft.Container(
                content=ft.Text("Доступ к базе данных", size=24, weight="bold", color=COLOR_ACTIVE),
                padding=10
            ),
            self.pw_field,
            self.btn_login
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

        self.page.add(self.login_view)

    def _check_password(self, e):
        if self.pw_field.value == DB_PASSWORD:
            self.page.clean()
            self._build_main_view()
        else:
            self.pw_field.error_text = "Неверный пароль"
            self.pw_field.update()

    def _build_main_view(self):
        self.tf_student = create_text_field("CSV файл со студентами", read_only=True, width=400)
        self.tf_csv = create_text_field("CSV файл с ответами", read_only=True, width=400)
        self.lbl_status = ft.Text("", color=COLOR_ACTIVE)
        self.lbl_status_s = ft.Text("", color=COLOR_ACTIVE)

        btn_pick_student = create_elevated_button(
            "Выбрать CSV файл",
            on_click=lambda _: self.student_picker.pick_files(allowed_extensions=["csv"]),
            bgcolor=COLOR_SURFACE,
            color=COLOR_TEXT
        )

        btn_pick_csv = create_elevated_button(
            "Выбрать CSV файл",
            on_click=lambda _: self.csv_picker.pick_files(allowed_extensions=["csv"]),
            bgcolor=COLOR_SURFACE,
            color=COLOR_TEXT
        )

        btn_upload = create_elevated_button(
            "ЗАГРУЗИТЬ В БАЗУ",
            on_click=self._upload_to_db,
            height=50
        )

        btn_clear = ft.TextButton("Очистить базу", on_click=self._clear_db, icon_color="red")

        main_view = create_scrollable_column([
            ft.Text("Настройка варианта ЕГЭ", size=24, weight="bold", color=COLOR_ACTIVE),
            ft.Row([btn_pick_student, self.tf_student]),
            ft.Row([btn_pick_csv, self.tf_csv]),
            self.lbl_status,
            self.lbl_status_s,
            ft.Divider(),
            btn_upload,
            btn_clear
        ])

        self.page.add(main_view)

    def _on_csv_picked(self, e: ft.FilePickerResultEvent):
        if e.files:
            self.csv_path = Path(e.files[0].path)
            self.tf_csv.value = str(self.csv_path)
            self.tf_csv.update()

    def _on_student_picked(self, e: ft.FilePickerResultEvent):
        if e.files:
            self.students_path = Path(e.files[0].path)
            self.tf_student.value = str(self.students_path)
            self.tf_student.update()

    def _upload_to_db(self, e):
        if not self.csv_path:
            self._show_status("Ошибка: Путь к папке или файлу не указан", "red")
            return

        try:
            tasks = []
            students = []
            with open(self.csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter=';')
                for row in reader:
                    t_id = row.get('id') or row.get('номер') or row.get('task_num')
                    ans = row.get('answer') or row.get('ответ')
                    score = row.get('score') or row.get('баллы') or 1

                    if t_id and ans:
                        tasks.append({
                            'id': t_id,
                            'answer': ans,
                            'score': int(score)
                        })

            count = self.db.add_tasks_batch(tasks)
            self._show_status(f"Успешно загружено {count} заданий.", COLOR_ACTIVE)

            with open(self.students_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter=';')
                for row in reader:
                    students.append(row)

            count = self.db.add_students_batch(students)
            self._show_status_s(f"Успешно загружено {count} студентов.", COLOR_ACTIVE)

        except Exception as ex:
            self._show_status(f"Ошибка при загрузке: {str(ex)}", "red")

    def _clear_db(self, e):
        if self.db.clear_tasks():
            self._show_status("База данных очищена", COLOR_ACTIVE)

    def _show_status(self, message: str, color: str):
        self.lbl_status.value = message
        self.lbl_status.color = color
        self.lbl_status.update()

    def _show_status_s(self, message: str, color: str):
        self.lbl_status_s.value = message
        self.lbl_status_s.color = color
        self.lbl_status_s.update()
