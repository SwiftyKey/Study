import flet as ft
from pathlib import Path
import pandas as pd
from config.settings import COLOR_BG, COLOR_ACTIVE, COLOR_TEXT, COLOR_SURFACE
from ui.components import create_elevated_button, create_text_field, create_scrollable_column


class AnswersJoinerApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.folder_path = None

        self._setup_page()
        self._create_picker()
        self._build_view()

    def _setup_page(self):
        self.page.title = "Склеивание ответов"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.bgcolor = COLOR_BG

    def _create_picker(self):
        self.folder_picker = ft.FilePicker(on_result=self._on_folder_picked)
        self.page.overlay.append(self.folder_picker)

    def _build_view(self):
        self.tf_folder = create_text_field("Папка с ответами учеников", read_only=True, width=500)
        self.btn_pick = create_elevated_button(
            "Выбрать папку",
            on_click=lambda _: self.folder_picker.get_directory_path()
        )
        self.btn_join = create_elevated_button(
            "СКЛЕИТЬ ФАЙЛЫ",
            on_click=self._join_files,
            bgcolor=COLOR_SURFACE,
            color=COLOR_TEXT
        )
        self.lbl_status = ft.Text("")

        view = create_scrollable_column([
            ft.Text("Менеджер ответов", size=24, color=COLOR_ACTIVE),
            ft.Row([self.btn_pick, self.tf_folder]),
            self.btn_join,
            self.lbl_status
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

        self.page.add(view)

    def _on_folder_picked(self, e: ft.FilePickerResultEvent):
        if e.path:
            self.folder_path = Path(e.path)
            self.tf_folder.value = str(self.folder_path)
            self.tf_folder.update()

    def _join_files(self, e):
        if not self.folder_path or not self.folder_path.exists():
            self._show_status("Папка не найдена", "red")
            return

        csv_files = list(self.folder_path.glob("student_answers_*.csv"))
        if not csv_files:
            self._show_status("Файлы ответов не найдены", "red")
            return

        try:
            dfs = [pd.read_csv(f) for f in csv_files]
            merged_df = pd.concat(dfs, ignore_index=True)

            output_path = self.folder_path / "students_answers.csv"
            merged_df.to_csv(output_path, index=False, encoding='utf-8-sig')

            self._show_status(f"Успешно! Склеено {len(csv_files)} файлов в {output_path.name}", COLOR_ACTIVE)
            self._show_snackbar("Файл создан!")

        except Exception as ex:
            self._show_status(f"Ошибка: {str(ex)}", "red")

    def _show_status(self, message: str, color: str):
        self.lbl_status.value = message
        self.lbl_status.color = color
        self.lbl_status.update()

    def _show_snackbar(self, message: str):
        self.page.snack_bar = ft.SnackBar(ft.Text(message))
        self.page.snack_bar.open = True
        self.page.update()
