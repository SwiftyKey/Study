import csv
import json
import socket
import threading
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import Dict, List

from common import Task, parse_variant_folder, recv_json, send_json


DISCOVERY_PORT = 54546


class TeacherServer:
    def __init__(self, host: str, port: int, on_event):
        self.host = host
        self.port = port
        self.on_event = on_event
        self.server_socket = None
        self.discovery_socket = None
        self.running = False
        self.clients: Dict[str, socket.socket] = {}
        self.lock = threading.Lock()

    def start(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()
        self.running = True
        threading.Thread(target=self._accept_loop, daemon=True).start()
        threading.Thread(target=self._discovery_loop, daemon=True).start()
        self.on_event({"type": "log", "message": f"Сервер запущен на {self.host}:{self.port}"})

    def stop(self):
        self.running = False
        with self.lock:
            for sock in list(self.clients.values()):
                try:
                    sock.close()
                except OSError:
                    pass
            self.clients.clear()
        for sock_obj in (self.server_socket, self.discovery_socket):
            if sock_obj:
                try:
                    sock_obj.close()
                except OSError:
                    pass
        self.on_event({"type": "log", "message": "Сервер остановлен"})

    def _accept_loop(self):
        while self.running:
            try:
                client_sock, addr = self.server_socket.accept()
            except OSError:
                break
            threading.Thread(
                target=self._handle_client, args=(client_sock, addr), daemon=True
            ).start()

    def _discovery_loop(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("", DISCOVERY_PORT))
        self.discovery_socket = sock

        while self.running:
            try:
                data, addr = sock.recvfrom(2048)
                request = json.loads(data.decode("utf-8"))
                if request.get("type") != "discover_teacher":
                    continue
                payload = {
                    "type": "teacher_info",
                    "teacher_ip": self.host,
                    "teacher_port": self.port,
                }
                sock.sendto(json.dumps(payload).encode("utf-8"), addr)
            except OSError:
                break
            except Exception:
                continue

    def _handle_client(self, sock: socket.socket, addr):
        student_name = f"{addr[0]}:{addr[1]}"
        try:
            hello = recv_json(sock)
            if hello.get("type") != "hello":
                raise ValueError("Ожидался hello")
            requested_name = (hello.get("student_name") or "").strip()
            if requested_name:
                student_name = requested_name

            with self.lock:
                self.clients[student_name] = sock
            self.on_event(
                {
                    "type": "student_connected",
                    "student": student_name,
                    "address": addr[0],
                }
            )

            while self.running:
                msg = recv_json(sock)
                self.on_event({"type": "client_message", "student": student_name, "payload": msg})
        except Exception as e:
            self.on_event(
                {
                    "type": "log",
                    "message": f"Отключение {student_name}: {type(e).__name__}: {e}",
                }
            )
        finally:
            with self.lock:
                if student_name in self.clients and self.clients[student_name] is sock:
                    del self.clients[student_name]
            try:
                sock.close()
            except OSError:
                pass
            self.on_event({"type": "student_disconnected", "student": student_name})

    def broadcast(self, payload: Dict) -> int:
        sent = 0
        dead = []
        with self.lock:
            for name, sock in self.clients.items():
                try:
                    send_json(sock, payload)
                    sent += 1
                except Exception:
                    dead.append(name)
            for name in dead:
                try:
                    self.clients[name].close()
                except OSError:
                    pass
                self.clients.pop(name, None)
        return sent


class TeacherApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ЕГЭ Информатика - Учитель")
        self.geometry("1040x680")

        self.tasks: List[Task] = []
        self.student_results: Dict[str, Dict] = {}
        self.connected_students: Dict[str, str] = {}
        self.task_stats: Dict[int, Dict[str, int]] = {}

        self.host_var = tk.StringVar(value=self._detect_local_ip())
        self.port_var = tk.IntVar(value=54545)

        self.server: TeacherServer | None = None
        self._build_ui()

    def _detect_local_ip(self) -> str:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except OSError:
            return "0.0.0.0"

    def _build_ui(self):
        top = ttk.Frame(self)
        top.pack(fill=tk.X, padx=10, pady=8)

        ttk.Label(top, text="IP:").pack(side=tk.LEFT)
        ttk.Entry(top, textvariable=self.host_var, width=16).pack(side=tk.LEFT, padx=4)
        ttk.Label(top, text="Порт:").pack(side=tk.LEFT)
        ttk.Entry(top, textvariable=self.port_var, width=8).pack(side=tk.LEFT, padx=4)

        ttk.Button(top, text="Запустить сервер", command=self.start_server).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(top, text="Остановить сервер", command=self.stop_server).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(top, text="Загрузить вариант", command=self.load_variant).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(top, text="Отправить вариант", command=self.send_variant).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(top, text="Отключить интернет ученикам", command=self.block_students_internet).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(top, text="Включить интернет ученикам", command=self.unblock_students_internet).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(top, text="Экспорт статистики", command=self.export_stats).pack(
            side=tk.LEFT, padx=5
        )

        mid = ttk.Panedwindow(self, orient=tk.HORIZONTAL)
        mid.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)

        left = ttk.Frame(mid)
        mid.add(left, weight=1)
        right = ttk.Frame(mid)
        mid.add(right, weight=2)

        ttk.Label(left, text="Подключенные ученики").pack(anchor="w")
        self.students_list = tk.Listbox(left, height=14)
        self.students_list.pack(fill=tk.BOTH, expand=True, pady=4)

        ttk.Label(left, text="Лог").pack(anchor="w")
        self.log_text = tk.Text(left, height=18, state=tk.DISABLED)
        self.log_text.pack(fill=tk.BOTH, expand=True, pady=4)

        ttk.Label(right, text="Результаты").pack(anchor="w")
        self.results_tree = ttk.Treeview(
            right,
            columns=("student", "score", "max_score", "finished_at"),
            show="headings",
            height=12,
        )
        self.results_tree.heading("student", text="Ученик")
        self.results_tree.heading("score", text="Баллы")
        self.results_tree.heading("max_score", text="Макс")
        self.results_tree.heading("finished_at", text="Время сдачи")
        self.results_tree.column("student", width=220)
        self.results_tree.column("score", width=90)
        self.results_tree.column("max_score", width=90)
        self.results_tree.column("finished_at", width=200)
        self.results_tree.pack(fill=tk.X, pady=4)

        ttk.Label(right, text="Статистика по заданиям").pack(anchor="w")
        self.task_tree = ttk.Treeview(
            right,
            columns=("task_id", "correct", "incorrect", "pct"),
            show="headings",
            height=14,
        )
        self.task_tree.heading("task_id", text="Задание")
        self.task_tree.heading("correct", text="Верно")
        self.task_tree.heading("incorrect", text="Неверно")
        self.task_tree.heading("pct", text="% верных")
        self.task_tree.column("task_id", width=90)
        self.task_tree.column("correct", width=90)
        self.task_tree.column("incorrect", width=90)
        self.task_tree.column("pct", width=120)
        self.task_tree.pack(fill=tk.BOTH, expand=True, pady=4)

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def log(self, msg: str):
        self.log_text.configure(state=tk.NORMAL)
        now = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{now}] {msg}\n")
        self.log_text.see(tk.END)
        self.log_text.configure(state=tk.DISABLED)

    def start_server(self):
        if self.server:
            messagebox.showinfo("Инфо", "Сервер уже запущен")
            return
        host = self.host_var.get().strip()
        port = int(self.port_var.get())
        self.server = TeacherServer(host, port, self.handle_server_event)
        try:
            self.server.start()
            self.log(f"Автообнаружение включено на UDP порту {DISCOVERY_PORT}")
        except Exception as e:
            self.server = None
            messagebox.showerror("Ошибка", f"Не удалось запустить сервер: {e}")

    def stop_server(self):
        if self.server:
            self.server.stop()
            self.server = None
            self.connected_students.clear()
            self.refresh_students_list()

    def load_variant(self):
        folder = filedialog.askdirectory(title="Выберите папку варианта")
        if not folder:
            return
        try:
            self.tasks = parse_variant_folder(folder)
            self.task_stats = {
                t.task_id: {"correct": 0, "incorrect": 0} for t in self.tasks
            }
            self.refresh_task_stats()
            self.log(f"Вариант загружен: {len(self.tasks)} заданий")
            messagebox.showinfo("Успех", f"Загружено заданий: {len(self.tasks)}")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def send_variant(self):
        if not self.server:
            messagebox.showerror("Ошибка", "Сначала запустите сервер")
            return
        if not self.tasks:
            messagebox.showerror("Ошибка", "Сначала загрузите вариант")
            return
        payload = {
            "type": "start_exam",
            "tasks": [
                {
                    "task_id": t.task_id,
                    "image_rel_path": t.image_rel_path,
                    "image_b64": t.image_b64,
                    "correct_answer": t.correct_answer,
                    "points": t.points,
                }
                for t in self.tasks
            ],
        }
        sent = self.server.broadcast(payload)
        self.log(f"Вариант отправлен на {sent} клиент(ов)")

    def block_students_internet(self):
        self._send_internet_command(True)

    def unblock_students_internet(self):
        self._send_internet_command(False)

    def _send_internet_command(self, block: bool):
        if not self.server:
            messagebox.showerror("Ошибка", "Сначала запустите сервер")
            return
        sent = self.server.broadcast({"type": "set_internet_block", "block": block})
        if block:
            self.log(f"Отправлена команда блокировки интернета на {sent} клиент(ов)")
        else:
            self.log(f"Отправлена команда разблокировки интернета на {sent} клиент(ов)")

    def handle_server_event(self, event: Dict):
        self.after(0, self._process_event, event)

    def _process_event(self, event: Dict):
        et = event.get("type")
        if et == "log":
            self.log(event["message"])
        elif et == "student_connected":
            student = event["student"]
            self.connected_students[student] = event.get("address", "")
            self.refresh_students_list()
            self.log(f"Подключен: {student}")
        elif et == "student_disconnected":
            student = event["student"]
            self.connected_students.pop(student, None)
            self.refresh_students_list()
            self.log(f"Отключен: {student}")
        elif et == "client_message":
            student = event["student"]
            payload = event["payload"]
            msg_type = payload.get("type")
            if msg_type == "submission":
                self.process_submission(student, payload)
            elif msg_type == "internet_status":
                self.log(
                    f"Интернет/{student}: "
                    f"{'OK' if payload.get('ok') else 'Ошибка'} - {payload.get('message', '')}"
                )

    def process_submission(self, student: str, payload: Dict):
        self.student_results[student] = payload
        self.refresh_results()
        per_task = payload.get("per_task", [])
        for row in per_task:
            task_id = int(row.get("task_id"))
            ok = bool(row.get("correct"))
            if task_id not in self.task_stats:
                self.task_stats[task_id] = {"correct": 0, "incorrect": 0}
            if ok:
                self.task_stats[task_id]["correct"] += 1
            else:
                self.task_stats[task_id]["incorrect"] += 1
        self.refresh_task_stats()
        self.log(f"Получен результат от {student}: {payload.get('score')}/{payload.get('max_score')}")

    def refresh_students_list(self):
        self.students_list.delete(0, tk.END)
        for student in sorted(self.connected_students.keys()):
            self.students_list.insert(tk.END, student)

    def refresh_results(self):
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        for student, data in sorted(self.student_results.items()):
            self.results_tree.insert(
                "",
                tk.END,
                values=(
                    student,
                    data.get("score"),
                    data.get("max_score"),
                    data.get("finished_at"),
                ),
            )

    def refresh_task_stats(self):
        for item in self.task_tree.get_children():
            self.task_tree.delete(item)
        for task_id in sorted(self.task_stats.keys()):
            st = self.task_stats[task_id]
            c = st["correct"]
            i = st["incorrect"]
            total = c + i
            pct = round((c / total) * 100, 1) if total else 0.0
            self.task_tree.insert("", tk.END, values=(task_id, c, i, pct))

    def export_stats(self):
        if not self.student_results:
            messagebox.showinfo("Инфо", "Нет результатов для экспорта")
            return
        out_dir = filedialog.askdirectory(title="Папка для экспорта статистики")
        if not out_dir:
            return
        out = Path(out_dir)
        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        students_path = out / f"ege_students_{now}.csv"
        tasks_path = out / f"ege_tasks_{now}.csv"

        with students_path.open("w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(["student", "score", "max_score", "finished_at"])
            for student, data in sorted(self.student_results.items()):
                w.writerow(
                    [
                        student,
                        data.get("score"),
                        data.get("max_score"),
                        data.get("finished_at"),
                    ]
                )

        with tasks_path.open("w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(["task_id", "correct", "incorrect", "percent_correct"])
            for task_id in sorted(self.task_stats.keys()):
                st = self.task_stats[task_id]
                c = st["correct"]
                i = st["incorrect"]
                total = c + i
                pct = round((c / total) * 100, 1) if total else 0.0
                w.writerow([task_id, c, i, pct])

        messagebox.showinfo("Готово", f"Сохранено:\n{students_path}\n{tasks_path}")
        self.log("Статистика экспортирована в CSV")

    def on_close(self):
        self.stop_server()
        self.destroy()


if __name__ == "__main__":
    app = TeacherApp()
    app.mainloop()
