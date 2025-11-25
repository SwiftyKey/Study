from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
import re
import sys
import csv
import time
import queue
import shutil
import threading
import tempfile
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import matplotlib
matplotlib.use("TkAgg")


GROUP_COUNT = 11  # 1..11, + общий = 12 круговых диаграмм
PIE_CATEGORIES = ["passed", "failed",
                  "compile_error", "runtime_error", "unknown"]
DEFAULT_TEST_ROOT = 'C:\\Users\\Swifty\\Downloads\\tests'
DEFAULT_BUILD_DIR = 'C:\\Users\\Swifty\\Downloads\\tests\\build'
DEFAULT_COMPILER = 'C:\\Programs\\gcc\\bin\\gcc.exe'

STD_CHOICES = [
    ("C89/90", "-std=c90"),
    ("C99", "-std=c99"),
    ("C11", "-std=c11"),
    ("C17", "-std=c17"),
    ("C23", "-std=c2x"),  # многие компиляторы используют -std=c2x
]


@dataclass
class TestResult:
    path: Path
    group: int
    name: str
    # one of PIE_CATEGORIES (except 'unknown' is allowed), or 'skipped'
    status: str
    stdout: str = ""
    stderr: str = ""
    compile_cmd: List[str] = field(default_factory=list)
    run_cmd: List[str] = field(default_factory=list)
    duration_s: float = 0.0


class RunnerThread(threading.Thread):
    def __init__(
        self,
        test_files: List[Path],
        compiler: str,
        std_flag: str,
        build_dir: Path,
        timeout_sec: float,
        jobs: int,
        result_queue: "queue.Queue[TestResult]",
        stop_event: threading.Event,
    ):
        super().__init__(daemon=True)
        self.test_files = test_files
        self.compiler = compiler
        self.std_flag = std_flag
        self.build_dir = build_dir
        self.timeout_sec = timeout_sec
        self.jobs = max(1, jobs)
        self.result_queue = result_queue
        self.stop_event = stop_event

    def run(self):
        # Параллелим компиляцию/прогон на несколько воркеров
        file_iter = iter(self.test_files)
        workers = []
        for _ in range(self.jobs):
            t = threading.Thread(target=self.worker_loop,
                                 args=(file_iter,), daemon=True)
            t.start()
            workers.append(t)
        for t in workers:
            t.join()

    def worker_loop(self, file_iter):
        while not self.stop_event.is_set():
            try:
                path = next(file_iter)
            except StopIteration:
                return
            try:
                res = self.process_one(path)
            except Exception as e:
                res = TestResult(
                    path=path,
                    group=extract_group_number(path.name) or 0,
                    name=path.name,
                    status="unknown",
                    stdout="",
                    stderr=f"runner exception: {e}",
                    duration_s=0.0,
                )
            self.result_queue.put(res)

    def process_one(self, path: Path) -> TestResult:
        # Берём группу только из имени папки (например, 1.xx -> 1)
        try:
            group = int(path.parts[-2].split('.')[0])
        except Exception:
            group = 0  # если не получилось распарсить папку

        target_name = f"{path.stem}.exe" if os.name == "nt" else path.stem
        group_build = self.build_dir / f"group_{group:02d}"
        group_build.mkdir(parents=True, exist_ok=True)
        output_bin = group_build / target_name

        # компиляция
        compile_cmd = [self.compiler, self.std_flag, "-O0",
                       "-Wall", "-Wextra", str(path), "-o", str(output_bin)]

        if path.suffix.lower() in [".cpp", ".cxx", ".cc"] and "clang" in (self.compiler or ""):
            # Если вдруг компилируем C++ файлы clang'ом — оставим как есть.
            pass

        t0 = time.time()
        try:
            cp = subprocess.run(
                compile_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
                timeout=self.timeout_sec,
                text=True,
            )
        except subprocess.TimeoutExpired:
            return TestResult(
                path=path, group=group, name=path.name, status="compile_error",
                stdout="", stderr="compile timeout", compile_cmd=compile_cmd, duration_s=time.time()-t0
            )
        if cp.returncode != 0 or not output_bin.exists():
            return TestResult(
                path=path, group=group, name=path.name, status="compile_error",
                stdout=cp.stdout, stderr=cp.stderr, compile_cmd=compile_cmd, duration_s=time.time()-t0
            )

        # Запуск
        run_cmd = [str(output_bin)]
        try:
            rp = subprocess.run(
                run_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
                timeout=self.timeout_sec,
                text=True,
            )
            duration = time.time() - t0
        except subprocess.TimeoutExpired:
            return TestResult(
                path=path, group=group, name=path.name, status="runtime_error",
                stdout="", stderr="run timeout", compile_cmd=compile_cmd, run_cmd=run_cmd, duration_s=time.time()-t0
            )

        stdout = rp.stdout or ""
        stderr = rp.stderr or ""
        status = classify_output(stdout, stderr, rp.returncode)

        return TestResult(
            path=path, group=group, name=path.name, status=status,
            stdout=stdout, stderr=stderr, compile_cmd=compile_cmd, run_cmd=run_cmd, duration_s=duration
        )


def extract_group_number(filename: str) -> Optional[int]:
    """
    Ждём имена вида 1.хх/.. или 1.xx_...; но в файле может встречаться префикс '1.' / '2.' в самом имени.
    Попробуем распарсить ведущий номер перед первой точкой.
    """
    m = re.match(r"^\s*(\d+)[._-]", filename)
    if m:
        try:
            return int(m.group(1))
        except Exception:
            return None
    return None


def infer_group_from_parents(path: Path) -> int:
    """
    Если имя файла не даёт номер — смотрим на родительские каталоги вида '1.xx'.
    """
    for parent in path.parents:
        m = re.match(r"^\s*(\d+)\s*[._-]\s*(\w+)\s*$", parent.name)
        if m:
            try:
                return int(m.group(1))
            except Exception:
                pass
    return 0


def classify_output(stdout: str, stderr: str, returncode: int) -> str:
    out = (stdout or "").lower()
    err = (stderr or "").lower()
    if " ok" in out or out.strip().endswith("ok"):
        return "passed"
    if "false" in out:
        return "failed"
    if returncode != 0:
        return "runtime_error"
    # Если ничего явного — неизвестно
    return "unknown"


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("C Compiler Conformance Test Runner – 12 Pie Charts")
        self.geometry("1400x900")
        self.minsize(1100, 760)

        self.compiler_var = tk.StringVar(value=DEFAULT_COMPILER or "")
        self.std_var = tk.StringVar(
            value=STD_CHOICES[1][1])  # C99 по умолчанию
        self.test_root_var = tk.StringVar(value=DEFAULT_TEST_ROOT)
        self.build_dir_var = tk.StringVar(value=DEFAULT_BUILD_DIR)
        self.timeout_var = tk.DoubleVar(value=5.0)
        self.jobs_var = tk.IntVar(value=11)

        self.status_var = tk.StringVar(value="Готово")
        self.total_var = tk.StringVar(value="—")
        self.group_counts: Dict[int, Dict[str, int]] = {
            i: {k: 0 for k in PIE_CATEGORIES} for i in range(1, GROUP_COUNT+1)}
        self.all_counts: Dict[str, int] = {k: 0 for k in PIE_CATEGORIES}

        self.results: List[TestResult] = []

        self._runner: Optional[RunnerThread] = None
        self._queue: "queue.Queue[TestResult]" = queue.Queue()
        self._stop_event = threading.Event()

        self.create_menu()
        self.create_controls()
        self.create_plots()
        self.poll_results_queue()

    # ---------------- UI ----------------

    def create_menu(self):
        menubar = tk.Menu(self)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Сохранить отчет CSV…",
                             command=self.save_csv)
        filemenu.add_separator()
        filemenu.add_command(label="Выход", command=self.on_exit)
        menubar.add_cascade(label="Файл", menu=filemenu)

        helpmenu = tk.Menu(menubar, tearoff=0)
        helpmenu.add_command(label="О программе", command=self.show_about)
        menubar.add_cascade(label="Справка", menu=helpmenu)

        self.config(menu=menubar)

    def create_controls(self):
        frm = ttk.Frame(self, padding=8)
        frm.pack(side=tk.TOP, fill=tk.X)

        ttk.Label(frm, text="Компилятор:").grid(row=0, column=0, sticky="w")
        ent_comp = ttk.Entry(frm, textvariable=self.compiler_var, width=42)
        ent_comp.grid(row=0, column=1, sticky="we", padx=(4, 8))
        ttk.Button(frm, text="…", width=3, command=self.pick_compiler).grid(
            row=0, column=2, sticky="w")

        ttk.Label(frm, text="Стандарт:").grid(
            row=0, column=3, sticky="w", padx=(8, 0))
        cmb_std = ttk.Combobox(frm, textvariable=self.std_var, state="readonly", width=12,
                               values=[flag for _, flag in STD_CHOICES])
        cmb_std.grid(row=0, column=4, sticky="w")

        ttk.Label(frm, text="Папка тестов:").grid(
            row=1, column=0, sticky="w", pady=(6, 0))
        ent_tests = ttk.Entry(frm, textvariable=self.test_root_var, width=42)
        ent_tests.grid(row=1, column=1, sticky="we", padx=(4, 8), pady=(6, 0))
        ttk.Button(frm, text="…", width=3, command=self.pick_tests).grid(
            row=1, column=2, sticky="w", pady=(6, 0))

        ttk.Label(frm, text="Build dir:").grid(
            row=1, column=3, sticky="w", padx=(8, 0), pady=(6, 0))
        ent_build = ttk.Entry(frm, textvariable=self.build_dir_var, width=28)
        ent_build.grid(row=1, column=4, sticky="we", pady=(6, 0))

        ttk.Label(frm, text="Timeout (сек):").grid(
            row=0, column=5, sticky="e", padx=(12, 0))
        spn_timeout = ttk.Spinbox(
            frm, from_=1.0, to=120.0, increment=0.5, textvariable=self.timeout_var, width=8)
        spn_timeout.grid(row=0, column=6, sticky="w")

        ttk.Label(frm, text="Параллельно jobs:").grid(
            row=1, column=5, sticky="e", padx=(12, 0), pady=(6, 0))
        spn_jobs = ttk.Spinbox(frm, from_=1, to=max(
            64, (os.cpu_count() or 4)*2), textvariable=self.jobs_var, width=8)
        spn_jobs.grid(row=1, column=6, sticky="w", pady=(6, 0))

        btn_run = ttk.Button(
            frm, text="Запустить все тесты", command=self.start_run)
        btn_run.grid(row=0, column=7, rowspan=2, padx=(
            16, 0), ipadx=12, ipady=6, sticky="ns")

        btn_stop = ttk.Button(frm, text="Стоп", command=self.stop_run)
        btn_stop.grid(row=0, column=8, rowspan=2, padx=(
            8, 0), ipadx=10, ipady=6, sticky="ns")

        # Строка состояния
        bar = ttk.Frame(self, padding=(8, 0, 8, 8))
        bar.pack(side=tk.TOP, fill=tk.X)
        ttk.Label(bar, textvariable=self.status_var).pack(side=tk.LEFT)
        ttk.Label(bar, text="   |   Итого: ").pack(side=tk.LEFT)
        ttk.Label(bar, textvariable=self.total_var).pack(side=tk.LEFT)

        for i in range(9):
            frm.columnconfigure(i, weight=1)

    def create_plots(self):
        # 12 кругов: 1..11 и ALL
        self.fig = Figure(figsize=(12, 7.2), dpi=100, layout="constrained")
        self.ax_map: Dict[str, any] = {}
        grid_rows, grid_cols = 3, 4
        labels = PIE_CATEGORIES

        # Создаём 12 подграфиков
        idx = 1
        for grp in range(1, GROUP_COUNT+1):
            ax = self.fig.add_subplot(grid_rows, grid_cols, idx)
            ax.set_title(f"Группа {grp}")
            self.ax_map[f"group_{grp}"] = ax
            idx += 1
        ax_all = self.fig.add_subplot(grid_rows, grid_cols, idx)
        ax_all.set_title("Все группы (суммарно)")
        self.ax_map["all"] = ax_all

        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Первичная отрисовка пустых кругов
        for key, ax in self.ax_map.items():
            counts = [0, 0, 0, 0, 0]
            self.draw_pie(ax, counts, labels)
        self.canvas.draw()

    def draw_pie(self, ax, counts, labels):
        total = sum(counts)
        if total == 0:
            ax.clear()
            ax.pie([1], labels=["нет данных"], autopct=None, startangle=110)
            ax.axis("equal")
            return
        ax.clear()
        filtered_counts = [c for c in counts if c > 0]

        filtered_labels = [l for l, c in zip(labels, counts) if c > 0]

        if not filtered_counts:  # если совсем нет данных
            ax.clear()
            ax.pie([1], labels=["нет данных"], startangle=110)
        else:
            ax.clear()
            ax.pie(
                filtered_counts,
                labels=filtered_labels,
                autopct=lambda pct: f"{pct:.0f}%" if pct >= 2 else "",
                startangle=110
            )
        ax.axis("equal")

    # ---------------- Actions ----------------

    def pick_compiler(self):
        path = filedialog.askopenfilename(
            title="Выберите компилятор (gcc/clang)")
        if path:
            self.compiler_var.set(path)

    def pick_tests(self):
        path = filedialog.askdirectory(title="Выберите папку с тестами")
        if path:
            self.test_root_var.set(path)

    def start_run(self):
        if self._runner and self._runner.is_alive():
            messagebox.showinfo("Уже запущено", "Выполнение уже идёт.")
            return

        test_root = Path(self.test_root_var.get()).expanduser()
        build_dir = Path(self.build_dir_var.get()).expanduser()
        compiler = self.compiler_var.get().strip() or DEFAULT_COMPILER
        std_flag = self.std_var.get().strip()
        timeout_sec = float(self.timeout_var.get())
        jobs = int(self.jobs_var.get())

        if not compiler:
            messagebox.showerror("Компилятор не найден",
                                 "Укажите путь к компилятору (gcc/clang).")
            return
        if not test_root.exists():
            messagebox.showerror("Папка тестов не найдена",
                                 f"Каталог не существует:\n{test_root}")
            return

        # Сканируем тесты
        test_files = self.collect_tests(test_root)
        if not test_files:
            messagebox.showwarning(
                "Тесты не найдены", f"В {test_root} не обнаружены файлы .c/.cpp")
            return

        # Сбрасываем результаты и счётчики
        self.results.clear()
        self.group_counts = {i: {k: 0 for k in PIE_CATEGORIES}
                             for i in range(1, GROUP_COUNT+1)}
        self.all_counts = {k: 0 for k in PIE_CATEGORIES}
        self.refresh_plots()

        # Готовим build dir
        try:
            build_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            messagebox.showerror(
                "Ошибка", f"Не удалось создать build dir:\n{e}")
            return

        self._stop_event.clear()
        self._queue = queue.Queue()

        self._runner = RunnerThread(
            test_files=test_files,
            compiler=compiler,
            std_flag=std_flag,
            build_dir=build_dir,
            timeout_sec=timeout_sec,
            jobs=jobs,
            result_queue=self._queue,
            stop_event=self._stop_event
        )
        self._runner.start()
        self.status_var.set(f"Запущено {len(test_files)} тестов…")
        self.total_var.set(
            "0 пройдено / 0 не пройдено / 0 ошибок компиляции / 0 ошибок выполнения")

    def stop_run(self):
        if self._runner and self._runner.is_alive():
            self._stop_event.set()
            self.status_var.set("Остановка…")

    def on_exit(self):
        self.stop_run()
        self.destroy()

    def collect_tests(self, root: Path) -> List[Path]:
        return list({p.resolve() for p in Path(root).rglob("*.c")})

    def poll_results_queue(self):
        updated = False
        try:
            while True:
                res: TestResult = self._queue.get_nowait()
                self.results.append(res)
                grp = res.group
                cat = res.status if res.status in PIE_CATEGORIES else "unknown"
                if 1 <= grp <= GROUP_COUNT:
                    self.group_counts[grp][cat] += 1
                self.all_counts[cat] += 1
                updated = True
        except queue.Empty:
            pass

        if updated:
            self.refresh_plots()
            # Обновление сводки
            t = self.all_counts
            self.total_var.set(f"{t['passed']} пройдено / {t['failed']} не пройдено / "
                               f"{t['compile_error']} ошибок компиляции / {t['runtime_error']} ошибок выполнения / "
                               f"{t['unknown']} неизвестно")

        # Обновим статус, если поток завершился
        if self._runner and not self._runner.is_alive() and self.status_var.get().startswith("Запущено"):
            self.status_var.set("Готово 262")

        self.after(200, self.poll_results_queue)

    def refresh_plots(self):
        # Отрисовать все 12 диаграмм
        labels = PIE_CATEGORIES
        for grp in range(1, GROUP_COUNT+1):
            ax = self.ax_map.get(f"group_{grp}")
            counts = [self.group_counts[grp][k] for k in labels]
            self.draw_pie(ax, counts, labels)
        ax_all = self.ax_map["all"]
        counts_all = [self.all_counts[k] for k in labels]
        self.draw_pie(ax_all, counts_all, labels)
        self.canvas.draw_idle()

    def show_about(self):
        messagebox.showinfo(
            "О программе",
            "Графическая программа для запуска тестов компилятора C и визуализации результатов 12 круговыми диаграммами.\n"
            "Автор: Вы.\nЛицензия: MIT."
        )

    def save_csv(self):
        if not self.results:
            messagebox.showwarning("Нет данных", "Сначала выполните тесты.")
            return
        path = filedialog.asksaveasfilename(
            title="Сохранить отчет CSV",
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv"), ("Все файлы", "*.*")],
            initialfile="test_results.csv"
        )
        if not path:
            return
        try:
            with open(path, "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f, delimiter=";")
                w.writerow(["group", "file", "status",
                           "duration_s", "compile_cmd", "run_cmd"])
                for r in self.results:
                    w.writerow([r.group, r.path.as_posix(), r.status, f"{r.duration_s:.3f}", " ".join(
                        r.compile_cmd), " ".join(r.run_cmd or [])])
        except Exception as e:
            messagebox.showerror("Ошибка сохранения",
                                 f"Не удалось сохранить CSV:\n{e}")
        else:
            messagebox.showinfo("Готово", f"Отчет сохранён:\n{path}")


def main():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
