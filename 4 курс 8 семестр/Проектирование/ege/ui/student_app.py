import flet as ft
import asyncio
from typing import Dict, Any, List
from config.settings import COLOR_BG, COLOR_ACTIVE, COLOR_TEXT, COLOR_SURFACE, EXAM_DURATION_SECONDS
from services.exam_service import ExamService
from ui.components import (
    create_elevated_button, create_text_field, create_scrollable_column,
    create_timer_display, create_result_table, create_task_input_container
)


class EgeStudentApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.exam_service = ExamService()
        self.timer_seconds = EXAM_DURATION_SECONDS
        self.timer_running = False
        self.current_task_idx = 0
        self.current_input_controls = []
        self.sidebar_container = self._create_sidebar()

        self._setup_page()
        self._build_login_view()

    def _setup_page(self):
        self.page.title = "ЕГЭ: Ученик"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.bgcolor = COLOR_BG
        self.page.full_screen = True
        self.page.scroll = ft.ScrollMode.AUTO
        self.page.padding = 20

    def _create_sidebar(self):
        from ui.components import create_task_sidebar

        return create_task_sidebar(
            tasks=self.exam_service.tasks,
            current_task_idx=self.current_task_idx,
            answers=self.exam_service.answers,
            on_task_click=self._navigate_to_task
        )

    def _navigate_to_task(self, task_idx: int):
        self._save_current_answer()

        if 0 <= task_idx < len(self.exam_service.tasks):
            self.current_task_idx = task_idx
            self._render_task()
            self._update_sidebar()

    def _update_sidebar(self):
        if self.sidebar_container:
            self.sidebar_container = self._create_sidebar()
            self.page.update()

    def _build_login_view(self):
        self.tf_school = create_text_field("Школа", width=300)
        self.tf_class = create_text_field("Класс", width=100)
        self.tf_name = create_text_field("ФИО", width=400)
        self.btn_start = create_elevated_button("НАЧАТЬ ЭКЗАМЕН", on_click=self._start_exam, height=50)

        login_view = create_scrollable_column([
            ft.Text("Регистрация участника", size=30, color=COLOR_ACTIVE),
            self.tf_school,
            self.tf_class,
            self.tf_name,
            self.btn_start
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

        self.page.add(login_view)

    def _start_exam(self, e):
        if not all([self.tf_school.value, self.tf_name.value]):
            self._show_snackbar("Заполните все поля!")
            return

        success, message = self.exam_service.start_exam_session()
        if not success:
            self._show_snackbar(f"Предупреждение: {message}")

        self.exam_service.set_student_info(
            self.tf_school.value,
            self.tf_class.value,
            self.tf_name.value
        )

        tasks = self.exam_service.load_tasks()
        if not tasks:
            self._show_snackbar("Нет заданий в базе!")
            return

        self.page.clean()
        self._build_exam_view()
        self._start_timer()
        self._render_task()

    def _build_exam_view(self):
        self.lbl_timer = create_timer_display(self.timer_seconds)
        self.lbl_task_num = ft.Text("Задание 1", size=24, weight="bold")
        self.img_task = ft.Image(height=300, fit=ft.ImageFit.CONTAIN)
        self.inputs_container = ft.Column()

        nav_row = ft.Row([
            create_elevated_button("Назад", on_click=self._prev_task, bgcolor=COLOR_SURFACE, color=COLOR_TEXT),
            create_elevated_button("Далее", on_click=self._next_task),
        ], alignment=ft.MainAxisAlignment.CENTER)

        finish_btn = create_elevated_button("ЗАВЕРШИТЬ", on_click=self._finish_exam, bgcolor="red", color="white")

        header = ft.Row([
            self.lbl_timer,
            ft.Container(expand=True),
            finish_btn
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        exam_view = create_scrollable_column([
            header,
            ft.Divider(color=COLOR_ACTIVE),
            ft.Row([
                ft.Column([
                    self.lbl_task_num,
                    self.img_task,
                    self.inputs_container,
                    nav_row
                ], alignment=ft.MainAxisAlignment.START, scroll=ft.ScrollMode.AUTO, expand=True)
            ], alignment=ft.MainAxisAlignment.CENTER, expand=True)
        ], expand=True)

        self.page.add(exam_view)

    def _start_timer(self):
        self.timer_running = True

        async def timer_loop():
            while self.timer_running and self.timer_seconds > 0:
                await asyncio.sleep(1)
                self.timer_seconds -= 1
                self.lbl_timer.value = f"{self.timer_seconds // 3600:02}:{self.timer_seconds // 60 % 60:02}:{self.timer_seconds % 60:02}"
                if self.timer_seconds <= 0:
                    self.timer_running = False
                    self._finish_exam(None)
                self.page.update()

        self.page.run_task(timer_loop)

    def _render_task(self):
        tasks = self.exam_service.tasks
        if not tasks:
            return

        task = tasks[self.current_task_idx]
        task_id = task['id']

        self.lbl_task_num.value = f"Задание № {task_id}"

        img_path = task.get('c_img_path', '')
        if img_path:
            import os
            if os.path.exists(img_path):
                self.img_task.src = img_path
                self.img_task.visible = True
            else:
                self.img_task.visible = False
        else:
            self.img_task.visible = False

        saved_answer = self.exam_service.get_answer(task_id)

        self.inputs_container.controls.clear()
        self.current_input_controls = []

        input_ui = create_task_input_container(task_id, saved_answer)
        self.inputs_container.controls.append(input_ui)

        def collect_textfields(controls):
            fields = []
            for ctrl in controls:
                if isinstance(ctrl, ft.TextField):
                    fields.append(ctrl)
                elif hasattr(ctrl, 'controls'):
                    fields.extend(collect_textfields(ctrl.controls))
            return fields

        self.current_input_controls = collect_textfields(input_ui.controls)

        self.inputs_container.update()
        self.page.update()

    def _save_current_answer(self):
        tasks = self.exam_service.tasks

        if not tasks:
            return

        task = tasks[self.current_task_idx]
        task_id = task['id']
        fields = self.current_input_controls

        if not fields:
            return

        if task_id in [17, 18, 26, 27]:
            val1 = fields[0].value if len(fields) > 0 else ""
            val2 = fields[1].value if len(fields) > 1 else ""
            self.exam_service.save_answer(task_id, f"{val1},{val2}")

        elif task_id == 25:
            vals = ','.join([str(f.value) for f in fields]).replace(",,", "")
            self.exam_service.save_answer(task_id, vals)

        else:
            if len(fields) > 0:
                self.exam_service.save_answer(task_id, fields[0].value)

    def _next_task(self, e):
        self._save_current_answer()
        if self.current_task_idx < len(self.exam_service.tasks) - 1:
            self.current_task_idx += 1
            self._render_task()
            self._update_sidebar()

    def _prev_task(self, e):
        self._save_current_answer()
        if self.current_task_idx > 0:
            self.current_task_idx -= 1
            self._render_task()
            self._update_sidebar()

    def _finish_exam(self, e):
        self.timer_running = False
        self._save_current_answer()

        self.exam_service.end_exam_session()

        total, max_score, results = self.exam_service.calculate_results()

        print(results)

        filename = self.exam_service.save_results_to_csv(results, total, max_score)

        self._show_results(total, max_score, results, filename)

    def _show_results(self, total: int, max_score: int, results: List, filename: str):
        self.page.clean()

        results_content = create_scrollable_column([
            ft.Container(
                content=ft.Text(f"Результат: {total} / {max_score}", size=30, color=COLOR_ACTIVE, weight="bold"),
                padding=ft.padding.only(bottom=20)
            ),
            ft.Container(
                content=ft.Text("Интернет доступ восстановлен", color="green"),
                padding=ft.padding.only(bottom=20)
            ),
            ft.Text("Таблица результатов:", size=18, weight="bold", color=COLOR_ACTIVE),
            create_result_table(results),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        expand=True
        )

        self.page.add(results_content)
        self.page.update()

    def _show_snackbar(self, message: str):
        self.page.snack_bar = ft.SnackBar(ft.Text(message))
        self.page.snack_bar.open = True
        self.page.update()
