import flet as ft
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import io
import base64
from models import ESMI_TYPES, AUTHOR_ROLES, ESMIRecord
from database import Database
from correlation import fit_polynomial

db = Database()
db.setup_sample_data()

NUMERIC_FIELDS = {
    "duration_min": "Длительность (мин)",
    "rating": "Рейтинг"
}

def main(page: ft.Page):
    page.title = "Анализ ЭСМИ"
    page.scroll = "auto"

    # Форма добавления
    esmi_type = ft.Dropdown(label="Вид ЭСМИ", options=[ft.dropdown.Option(t) for t in ESMI_TYPES])
    channel = ft.TextField(label="Канал")
    date = ft.TextField(label="Дата (ГГГГ-ММ-ДД)")
    program = ft.TextField(label="Передача")
    topic = ft.TextField(label="Тематика")
    author_dropdown = ft.Dropdown(label="Автор")
    annotation = ft.TextField(label="Аннотация", multiline=True)
    notes = ft.TextField(label="Примечания", multiline=True)
    duration = ft.TextField(label="Длительность (мин)", value="30")
    rating = ft.TextField(label="Рейтинг (0–10)", value="5.0")

    # Форма добавления автора
    author_name_field = ft.TextField(label="Ф.И.О. автора", width=300)
    author_role_field = ft.Dropdown(
        label="Роль автора",
        width=200,
        options=[ft.dropdown.Option(r) for r in AUTHOR_ROLES]
    )
    if AUTHOR_ROLES:
        author_role_field.value = AUTHOR_ROLES[0]


    status_text = ft.Text(value="", size=14)

    def on_add_author_simple(e):
        name = author_name_field.value.strip()
        role = author_role_field.value
        if not name:
            status_text.value = "❗ Ошибка: введите Ф.И.О. автора!"
            status_text.color = "red"
            page.update()
            return
        try:
            author_id = db.add_author(name, role)
            author_name_field.value = ""
            load_authors()
            status_text.value = f"✅ Автор добавлен (ID: {author_id})"
            status_text.color = "green"
            page.update()
        except Exception as ex:
            status_text.value = f"❌ Ошибка: {ex}"
            status_text.color = "red"
            page.update()

    add_author_simple_btn = ft.ElevatedButton("Добавить автора", on_click=on_add_author_simple)

    def load_authors():
        author_dropdown.options = [
            ft.dropdown.Option(key=str(a.id), text=a.full_name) for a in db.get_authors()
        ]
        if author_dropdown.options:
            author_dropdown.value = author_dropdown.options[0].key
        page.update()

    load_authors()

    # Обновление таблицы записей
    records_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("ID")),
            ft.DataColumn(ft.Text("ЭСМИ")),
            ft.DataColumn(ft.Text("Канал")),
            ft.DataColumn(ft.Text("Дата")),
            ft.DataColumn(ft.Text("Передача")),
            ft.DataColumn(ft.Text("Автор")),
            ft.DataColumn(ft.Text("Длит., мин")),
            ft.DataColumn(ft.Text("Рейтинг")),
            ft.DataColumn(ft.Text("Действия")),
        ],
        rows=[]
    )

    def load_records():
        records_table.rows.clear()
        records = db.get_records()
        authors = {a.id: a.full_name for a in db.get_authors()}
        for r in records:
            records_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(r.id))),
                        ft.DataCell(ft.Text(r.esmi_type)),
                        ft.DataCell(ft.Text(r.channel)),
                        ft.DataCell(ft.Text(r.date)),
                        ft.DataCell(ft.Text(r.program)),
                        ft.DataCell(ft.Text(authors.get(r.author_id, "—"))),
                        ft.DataCell(ft.Text(str(r.duration_min))),
                        ft.DataCell(ft.Text(f"{r.rating:.1f}")),
                        ft.DataCell(
                            ft.IconButton(
                                icon=ft.Icons.DELETE,
                                on_click=lambda e, rid=r.id: delete_record(rid)
                            )
                        ),
                    ]
                )
            )
        page.update()

    def delete_record(record_id):
        db.delete_record(record_id)
        load_records()
        update_correlation_plot()

    def on_add_record(e):
        try:
            if not author_dropdown.options:
                raise ValueError("Сначала добавьте хотя бы одного автора")
            author_id = int(author_dropdown.value)
            dur = int(duration.value)
            rat = float(rating.value)
            if dur <= 0 or rat < 0 or rat > 10:
                raise ValueError("Длительность > 0, рейтинг от 0 до 10")
            if not all([esmi_type.value, channel.value, date.value, program.value]):
                raise ValueError("Заполните все обязательные поля")

            from datetime import datetime
            datetime.strptime(date.value, "%Y-%m-%d")

            record = ESMIRecord(
                id=0, esmi_type=esmi_type.value, channel=channel.value, date=date.value,
                program=program.value, topic=topic.value, author_id=author_id,
                annotation=annotation.value, notes=notes.value,
                duration_min=dur, rating=rat
            )
            db.add_record(record)
            load_records()
            update_correlation_plot()

            status_text.value = "✅ Запись успешно добавлена!"
            status_text.color = "green"
            page.update()

        except Exception as ex:
            status_text.value = f"❌ Ошибка: {ex}"
            status_text.color = "red"
            page.update()

    # Корреляционный график
    corr_image = ft.Image(visible=False, width=600, height=400)
    corr_text = ft.Text()
    x_field_dropdown = ft.Dropdown(
        label="Параметр X",
        options=[ft.dropdown.Option(key=k, text=v) for k, v in NUMERIC_FIELDS.items()],
        value="duration_min",
        width=200
    )
    y_field_dropdown = ft.Dropdown(
        label="Параметр Y",
        options=[ft.dropdown.Option(key=k, text=v) for k, v in NUMERIC_FIELDS.items()],
        value="rating",
        width=200
    )

    def on_recalculate_correlation(e):
        update_correlation_plot()

    recalc_btn = ft.ElevatedButton("Построить корреляцию", on_click=on_recalculate_correlation)

    def update_correlation_plot():
        x_key = x_field_dropdown.value
        y_key = y_field_dropdown.value

        if x_key == y_key:
            corr_text.value = "⚠️ Параметры X и Y должны быть разными"
            corr_image.visible = False
            page.update()
            return

        records = db.get_records_as_dicts()
        if len(records) < 3:  # для полинома 2-й степени нужно ≥3 точки
            corr_text.value = "Недостаточно данных (требуется ≥3 записи)"
            corr_image.visible = False
            page.update()
            return

        try:
            x_vals = [float(r[x_key]) for r in records if r[x_key] is not None]
            y_vals = [float(r[y_key]) for r in records if r[y_key] is not None]
            valid_pairs = [(x, y) for x, y in zip(x_vals, y_vals) if x is not None and y is not None]
            if len(valid_pairs) < 3:
                raise ValueError("Недостаточно валидных пар данных (≥3)")

            x_data = np.array([p[0] for p in valid_pairs])
            y_data = np.array([p[1] for p in valid_pairs])

            # Криволинейная (полиномиальная) регрессия 2-й степени
            coeffs, r2, poly, equation = fit_polynomial(x_data, y_data, degree=2)

            # График
            plt.figure(figsize=(8, 5))
            plt.scatter(x_data, y_data, alpha=0.7, label="Данные")

            # Плавная кривая
            x_smooth = np.linspace(x_data.min(), x_data.max(), 200)
            y_smooth = poly(x_smooth)
            plt.plot(x_smooth, y_smooth, color="red", label=f"Полином 2-й степени\nR² = {r2:.3f}")

            plt.xlabel(NUMERIC_FIELDS[x_key])
            plt.ylabel(NUMERIC_FIELDS[y_key])
            plt.title(f"Криволинейная корреляция: {NUMERIC_FIELDS[x_key]} ↔ {NUMERIC_FIELDS[y_key]}")
            plt.legend()
            plt.grid(True)

            buf = io.BytesIO()
            plt.savefig(buf, format="png")
            plt.close()
            buf.seek(0)
            corr_image.src_base64 = base64.b64encode(buf.read()).decode("utf-8")
            corr_image.visible = True

            corr_text.value = f"Уравнение: y = {equation}\nКоэффициент детерминации R² = {r2:.3f}"

        except Exception as ex:
            corr_text.value = f"Ошибка: {ex}"
            corr_image.visible = False

        page.update()

    # Сборка интерфейса
    add_record_btn = ft.ElevatedButton("Добавить запись", on_click=on_add_record)

    page.add(
        ft.Text("Анализ ЭСМИ", size=24, weight="bold"),
        ft.Divider(),
        ft.Text("Форма добавления автора", weight="bold"),
        ft.Row([author_name_field, author_role_field, add_author_simple_btn]),
        ft.Divider(),
        ft.Text("Форма добавления записи ЭСМИ", weight="bold"),
        ft.Row([esmi_type, channel, date, duration, rating]),
        ft.Row([program, topic]),
        ft.Row([author_dropdown]),
        ft.Row([annotation, notes]),
        ft.Row([add_record_btn]),
        status_text,
        ft.Divider(),
        ft.Text("Список записей", weight="bold"),
        ft.Column([records_table], scroll=ft.ScrollMode.AUTO, height=300),
        ft.Divider(),
        ft.Text("Корреляционный анализ", weight="bold"),
        ft.Row([x_field_dropdown, y_field_dropdown, recalc_btn]),
        corr_text,
        corr_image,
        ft.Text("ℹ️ Выберите два числовых параметра и нажмите 'Построить корреляцию'", italic=True)
    )

    load_records()
    update_correlation_plot()

ft.app(target=main)
