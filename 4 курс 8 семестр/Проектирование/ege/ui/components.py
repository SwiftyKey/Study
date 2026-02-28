import flet as ft
from config.settings import COLOR_BG, COLOR_ACTIVE, COLOR_ERROR, COLOR_SUCCESS, COLOR_SURFACE, COLOR_TEXT
from utils.helpers import format_time
from typing import List, Dict, Any, Callable


def create_elevated_button(
        text: str,
        on_click,
        bgcolor: str = COLOR_ACTIVE,
        color: str = COLOR_BG,
        **kwargs
    ):
    return ft.ElevatedButton(
        text=text,
        on_click=on_click,
        bgcolor=bgcolor,
        color=color,
        **kwargs
    )


def create_text_field(label: str="", value: str="", read_only: bool = False, **kwargs):
    return ft.TextField(
        label=label,
        value=value,
        read_only=read_only,
        border_color=COLOR_ACTIVE,
        focused_border_color=COLOR_ACTIVE,
        **kwargs
    )


def create_scrollable_column(controls: list, expand: bool = False, **kwargs) -> ft.Column:
    return ft.Column(
        controls=controls,
        scroll=ft.ScrollMode.AUTO,
        expand=expand,
        spacing=10,
        **kwargs
    )


def create_task_input_container(task_id: int, answer_value: Any = "") -> ft.Column:
    container = ft.Column()

    if answer_value is None:
        answer_value = ""

    if task_id in [17, 18, 20, 26]:
        if isinstance(answer_value, list):
            parts = answer_value
        else:
            parts = str(answer_value).split(';')

        val1 = parts[0] if len(parts) > 0 else ""
        val2 = parts[1] if len(parts) > 1 else ""

        row = ft.Row([
            create_text_field(label="Ответ 1", value=str(val1), width=200),
            create_text_field(label="Ответ 2", value=str(val2), width=200),
        ])
        container.controls.append(row)
    elif task_id == 25:
        if not isinstance(answer_value, list):
            saved_vals = [""] * 16
        else:
            saved_vals = answer_value
            while len(saved_vals) < 16:
                saved_vals.append("")

        for r in range(8):
            row_controls = ft.Row()
            for c in range(2):
                idx = r * 2 + c
                val = saved_vals[idx] if idx < len(saved_vals) else ""
                row_controls.controls.append(
                    create_text_field(value=str(val), width=150, text_size=12, text_align=ft.TextAlign.CENTER)
                )
            container.controls.append(row_controls)
    elif task_id == 27:
        if not isinstance(answer_value, list):
            saved_vals = [""] * 4
        else:
            saved_vals = answer_value
            while len(saved_vals) < 4:
                saved_vals.append("")

        for r in range(2):
            row_controls = ft.Row()
            for c in range(2):
                idx = r * 2 + c
                val = saved_vals[idx] if idx < len(saved_vals) else ""
                row_controls.controls.append(
                    create_text_field(value=str(val), width=150, text_size=12, text_align=ft.TextAlign.CENTER)
                )
            container.controls.append(row_controls)
    else:
        container.controls.append(
            create_text_field(label="Ваш ответ", value=str(answer_value), width=500, multiline=True, min_lines=1, max_lines=5)
        )

    return container


def create_timer_display(minutes: int) -> ft.Text:
    return ft.Text(
        format_time(minutes),
        size=20,
        weight="bold",
        color=COLOR_ACTIVE
    )


def create_result_table(results: List) -> ft.Container:
    table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("№", weight="bold")),
            ft.DataColumn(ft.Text("Ваш ответ", weight="bold")),
            ft.DataColumn(ft.Text("Правильный", weight="bold")),
            ft.DataColumn(ft.Text("Баллы", weight="bold")),
            ft.DataColumn(ft.Text("Статус", weight="bold")),
        ],
        rows=[
            ft.DataRow(cells=[
                ft.DataCell(ft.Text(str(r['task_id']), width=40)),
                ft.DataCell(ft.Text(
                    str(r['user_answer']),
                    width=200
                )),
                ft.DataCell(ft.Text(
                    str(r['correct_answer']),
                    width=200
                )),
                ft.DataCell(ft.Text(str(r['score']), width=50)),
                ft.DataCell(ft.Icon(
                    ft.Icons.CHECK if r['is_correct'] else ft.Icons.CLOSE,
                    color=COLOR_SUCCESS if r['is_correct'] else COLOR_ERROR
                )),
            ])
            for r in results
        ], data_row_max_height=float("inf")
    )

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Row([table], scroll=ft.ScrollMode.AUTO),
            ],
            scroll=ft.ScrollMode.AUTO,
            height=400,
        ),
        border=ft.border.all(1, COLOR_ACTIVE),
        padding=10,
        expand=True,
    )


def create_task_sidebar(tasks: List[Dict[str, Any]], current_task_idx: int,
                        answers: Dict[int, Any], on_task_click: Callable) -> ft.Container:
    task_buttons = []

    for idx, task in enumerate(tasks):
        task_id = task['id']
        is_current = (task_id == current_task_idx)
        is_answered = task_id in answers and answers[task_id] not in [None, "", [], ',']

        if is_current:
            bgcolor = COLOR_ACTIVE
            color = COLOR_BG
        elif is_answered:
            bgcolor = COLOR_SURFACE
            color = COLOR_ACTIVE
        else:
            bgcolor = COLOR_SURFACE
            color = COLOR_TEXT

        btn = ft.ElevatedButton(
            text=f"{task_id}",
            width=45,
            height=45,
            style=ft.ButtonStyle(
                bgcolor=bgcolor,
                color=color,
                shape=ft.RoundedRectangleBorder(radius=4),
            ),
            on_click=lambda e, t_idx=idx: on_task_click(t_idx),
            key=f"task_{task_id}",
        )
        task_buttons.append(btn)

    return ft.Container(
        content=ft.Column(
            controls=task_buttons,
            scroll=ft.ScrollMode.AUTO,
            spacing=5,
            expand=True,
        ),
        width=90,
        padding=20,
        bgcolor=COLOR_SURFACE,
        border=ft.border.only(right=ft.BorderSide(1, COLOR_ACTIVE)),
        expand=False,
    )
