import flet as ft
from config.settings import COLOR_BG
from ui.parser_app import TasksParserApp


def main(page: ft.Page):
    page.title = "TasksParser"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = COLOR_BG
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    TasksParserApp(page)


if __name__ == "__main__":
    ft.app(target=main)
