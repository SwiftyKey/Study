import csv
import re
import tkinter as tk
from dataclasses import dataclass
from pathlib import Path
from tkinter import filedialog, messagebox, ttk


@dataclass
class Item:
    src_path: Path
    name: str
    answer: str = ""
    points: str = "1"


def natural_key(name: str):
    parts = re.split(r"(\d+)", name.lower())
    out = []
    for p in parts:
        if p.isdigit():
            out.append(int(p))
        else:
            out.append(p)
    return out


class CsvBuilderApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ЕГЭ Информатика - Сборщик варианта CSV")
        self.geometry("980x720")

        self.items: list[Item] = []
        self.current_idx = 0
        self.current_image = None
        self.source_dir: Path | None = None
        self.csv_path: Path | None = None

        self._build_ui()

    def _build_ui(self):
        top = ttk.Frame(self)
        top.pack(fill=tk.X, padx=10, pady=8)

        ttk.Button(top, text="Выбрать папку с картинками", command=self.choose_folder).pack(
            side=tk.LEFT, padx=4
        )
        ttk.Button(top, text="Открыть папку варианта", command=self.open_variant_hint).pack(
            side=tk.LEFT, padx=4
        )

        self.status_var = tk.StringVar(value="Папка не выбрана")
        ttk.Label(self, textvariable=self.status_var).pack(anchor="w", padx=10)

        frame = ttk.LabelFrame(self, text="Задание")
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)

        self.title_var = tk.StringVar(value="Загрузите папку с картинками")
        ttk.Label(frame, textvariable=self.title_var, font=("Segoe UI", 12, "bold")).pack(
            anchor="w", padx=8, pady=6
        )

        self.image_label = ttk.Label(frame, text="Предпросмотр изображения")
        self.image_label.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        form = ttk.Frame(frame)
        form.pack(fill=tk.X, padx=8, pady=8)

        ttk.Label(form, text="Ответ:").grid(row=0, column=0, sticky="w")
        self.answer_var = tk.StringVar(value="")
        ttk.Entry(form, textvariable=self.answer_var).grid(
            row=0, column=1, sticky="ew", padx=6
        )

        ttk.Label(form, text="Баллы:").grid(row=1, column=0, sticky="w")
        self.points_var = tk.StringVar(value="1")
        ttk.Entry(form, textvariable=self.points_var, width=8).grid(
            row=1, column=1, sticky="w", padx=6, pady=4
        )
        form.columnconfigure(1, weight=1)

        nav = ttk.Frame(self)
        nav.pack(fill=tk.X, padx=10, pady=8)

        ttk.Button(nav, text="Предыдущее", command=self.prev_item).pack(side=tk.LEFT, padx=4)
        ttk.Button(nav, text="Следующее", command=self.next_item).pack(side=tk.LEFT, padx=4)
        ttk.Button(nav, text="Сохранить текущий ответ", command=self.save_current).pack(
            side=tk.LEFT, padx=4
        )

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def choose_folder(self):
        folder = filedialog.askdirectory(title="Папка с картинками заданий")
        if not folder:
            return
        src = Path(folder)
        exts = {".png", ".gif", ".jpg", ".jpeg"}
        files = [p for p in src.iterdir() if p.is_file() and p.suffix.lower() in exts]
        files.sort(key=lambda p: natural_key(p.name))
        if not files:
            messagebox.showerror("Ошибка", "В папке нет изображений (png/gif/jpg/jpeg)")
            return

        self.source_dir = src
        self.csv_path = src / "tasks.csv"
        self.items = [Item(src_path=p, name=p.name) for p in files]
        self._load_existing_csv()
        self._write_csv()
        self.current_idx = 0
        self.render_current()
        self.status_var.set(
            f"Загружено изображений: {len(self.items)} из {src}. CSV: {self.csv_path.name}"
        )

    def render_current(self):
        if not self.items:
            return
        item = self.items[self.current_idx]
        self.title_var.set(f"{self.current_idx + 1}/{len(self.items)}: {item.name}")
        self.answer_var.set(item.answer)
        self.points_var.set(item.points)

        try:
            self.current_image = tk.PhotoImage(file=str(item.src_path))
            self.image_label.configure(image=self.current_image, text="")
        except tk.TclError:
            self.current_image = None
            self.image_label.configure(image="", text=f"Файл: {item.src_path.name}")

    def save_current(self):
        if not self.items:
            return
        item = self.items[self.current_idx]
        item.answer = self.answer_var.get().strip()
        points = self.points_var.get().strip()
        if not points:
            points = "1"
        if not points.isdigit() or int(points) <= 0:
            points = "1"
        item.points = points
        self._write_csv()
        self.status_var.set(
            f"Сохранено: задание {self.current_idx + 1}/{len(self.items)} -> {self.csv_path}"
        )

    def next_item(self):
        if not self.items:
            return
        self.save_current()
        if self.current_idx < len(self.items) - 1:
            self.current_idx += 1
            self.render_current()

    def prev_item(self):
        if not self.items:
            return
        self.save_current()
        if self.current_idx > 0:
            self.current_idx -= 1
            self.render_current()

    def _load_existing_csv(self):
        if not self.csv_path or not self.csv_path.exists():
            return
        answers = {}
        points_map = {}
        with self.csv_path.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.reader(f)
            for row in reader:
                if not row:
                    continue
                img = row[0].strip()
                ans = row[1].strip() if len(row) > 1 else ""
                pts = row[2].strip() if len(row) > 2 and row[2].strip() else "1"
                answers[img] = ans
                points_map[img] = pts

        for item in self.items:
            rel = item.name
            if rel in answers:
                item.answer = answers[rel]
                item.points = points_map.get(rel, "1")

    def _write_csv(self):
        if not self.csv_path:
            return
        rows = [[item.name, item.answer, item.points] for item in self.items]
        with self.csv_path.open("w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerows(rows)

    def open_variant_hint(self):
        if not self.source_dir:
            messagebox.showinfo("Инфо", "Сначала выберите папку с картинками")
            return
        messagebox.showinfo(
            "Готово",
            f"Готовая папка варианта:\n{self.source_dir}\n\n"
            f"CSV обновляется автоматически в файле:\n{self.csv_path}\n\n"
            "Эту же папку можно загружать в teacher_app.py",
        )

    def on_close(self):
        self.destroy()


if __name__ == "__main__":
    app = CsvBuilderApp()
    app.mainloop()
