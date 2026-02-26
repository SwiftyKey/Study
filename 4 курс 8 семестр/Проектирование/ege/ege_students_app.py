import flet as ft
from config.settings import COLOR_BG
from ui.student_app import EgeStudentApp


def main(page: ft.Page):
    page.title = "EgeStudentsApp"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = COLOR_BG
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.AUTO
    page.padding = 20

    EgeStudentApp(page)


if __name__ == "__main__":
    ft.app(target=main)
