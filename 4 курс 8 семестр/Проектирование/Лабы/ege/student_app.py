import base64
import json
import os
import socket
import tempfile
import threading
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import messagebox, ttk
from typing import Dict, List, Optional, Tuple

from common import InternetBlocker, Task, recv_json, score_answers, send_json


DISCOVERY_PORT = 54546


class StudentClient:
    def __init__(self, host: str, port: int, student_name: str, on_event):
        self.host = host
        self.port = port
        self.student_name = student_name
        self.on_event = on_event
        self.sock = None
        self.running = False

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        self.running = True
        send_json(self.sock, {"type": "hello", "student_name": self.student_name})
        threading.Thread(target=self._recv_loop, daemon=True).start()

    def send(self, payload: Dict):
        if self.sock and self.running:
            send_json(self.sock, payload)

    def _recv_loop(self):
        try:
            while self.running:
                msg = recv_json(self.sock)
                self.on_event({"type": "server_message", "payload": msg})
        except Exception as e:
            self.on_event({"type": "log", "message": f"Соединение прервано: {e}"})
        finally:
            self.running = False
            if self.sock:
                try:
                    self.sock.close()
                except OSError:
                    pass
            self.on_event({"type": "disconnected"})

    def close(self):
        self.running = False
        if self.sock:
            try:
                self.sock.close()
            except OSError:
                pass


class StudentApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ЕГЭ Информатика - Ученик")
        self.geometry("980x720")

        self.name_var = tk.StringVar(value=os.getenv("USERNAME", "student"))

        self.client: StudentClient | None = None
        self.blocker: InternetBlocker | None = None
        self.internet_blocked = False

        self.tasks: List[Task] = []
        self.current_idx = 0
        self.answers: Dict[str, str] = {}
        self.temp_dir = Path(tempfile.mkdtemp(prefix="ege_student_"))
        self.current_image = None

        self._build_ui()
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def _build_ui(self):
        conn = ttk.Frame(self)
        conn.pack(fill=tk.X, padx=10, pady=8)

        ttk.Label(conn, text="Имя Фамилия:").pack(side=tk.LEFT)
        ttk.Entry(conn, textvariable=self.name_var, width=32).pack(side=tk.LEFT, padx=4)
        ttk.Button(conn, text="Подключиться", command=self.connect).pack(side=tk.LEFT, padx=8)

        self.status_var = tk.StringVar(value="Не подключено")
        ttk.Label(self, textvariable=self.status_var).pack(anchor="w", padx=10)

        task_frame = ttk.LabelFrame(self, text="Задание")
        task_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)

        self.task_title_var = tk.StringVar(value="Ожидание варианта от учителя")
        ttk.Label(task_frame, textvariable=self.task_title_var, font=("Segoe UI", 12, "bold")).pack(
            anchor="w", padx=8, pady=4
        )

        self.image_label = ttk.Label(task_frame, text="Изображение задания будет здесь")
        self.image_label.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        answer_frame = ttk.Frame(task_frame)
        answer_frame.pack(fill=tk.X, padx=8, pady=4)
        ttk.Label(answer_frame, text="Ответ:").pack(side=tk.LEFT)
        self.answer_var = tk.StringVar(value="")
        self.answer_entry = ttk.Entry(answer_frame, textvariable=self.answer_var)
        self.answer_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=6)

        nav = ttk.Frame(self)
        nav.pack(fill=tk.X, padx=10, pady=8)
        ttk.Button(nav, text="Предыдущее", command=self.prev_task).pack(side=tk.LEFT, padx=4)
        ttk.Button(nav, text="Следующее", command=self.next_task).pack(side=tk.LEFT, padx=4)
        ttk.Button(nav, text="Сохранить ответ", command=self.save_current_answer).pack(
            side=tk.LEFT, padx=4
        )
        ttk.Button(nav, text="Завершить", command=self.finish_exam).pack(side=tk.RIGHT, padx=4)

        self.log_text = tk.Text(self, height=10, state=tk.DISABLED)
        self.log_text.pack(fill=tk.BOTH, padx=10, pady=8)

    def log(self, msg: str):
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"{datetime.now().strftime('%H:%M:%S')} {msg}\n")
        self.log_text.see(tk.END)
        self.log_text.configure(state=tk.DISABLED)

    def discover_teacher(self, timeout: float = 1.5) -> Optional[Tuple[str, int]]:
        req = json.dumps({"type": "discover_teacher"}).encode("utf-8")
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.settimeout(timeout)
        try:
            sock.sendto(req, ("255.255.255.255", DISCOVERY_PORT))
            data, _ = sock.recvfrom(2048)
            resp = json.loads(data.decode("utf-8"))
            if resp.get("type") != "teacher_info":
                return None
            ip = str(resp.get("teacher_ip", "")).strip()
            port = int(resp.get("teacher_port", 0))
            if not ip or port <= 0:
                return None
            return ip, port
        except Exception:
            return None
        finally:
            sock.close()

    def connect(self):
        name = self.name_var.get().strip() or "student"
        found = self.discover_teacher()
        if not found:
            messagebox.showerror(
                "Ошибка", "Не удалось найти учителя автоматически. Проверьте, что сервер учителя запущен."
            )
            return
        host, port = found

        self.log(f"Учитель найден автоматически: {host}:{port}")

        self.client = StudentClient(host, port, name, self.handle_event)
        try:
            self.client.connect()
            self.status_var.set("Подключено к учителю")
            self.log("Установлено соединение с учителем")
        except Exception as e:
            self.client = None
            messagebox.showerror("Ошибка", f"Не удалось подключиться: {e}")

    def handle_event(self, event: Dict):
        self.after(0, self._process_event, event)

    def _process_event(self, event: Dict):
        et = event.get("type")
        if et == "server_message":
            payload = event["payload"]
            msg_type = payload.get("type")
            if msg_type == "start_exam":
                self.start_exam(payload)
            elif msg_type == "set_internet_block":
                self.apply_internet_policy(bool(payload.get("block")))
        elif et == "log":
            self.log(event["message"])
        elif et == "disconnected":
            self.status_var.set("Соединение закрыто")

    def start_exam(self, payload: Dict):
        tasks_payload = payload.get("tasks", [])
        self.tasks.clear()
        self.answers.clear()
        for row in tasks_payload:
            t = Task(
                task_id=int(row["task_id"]),
                image_rel_path=row["image_rel_path"],
                image_b64=row["image_b64"],
                correct_answer=row["correct_answer"],
                points=int(row.get("points", 1)),
            )
            self.tasks.append(t)
            image_file = self.temp_dir / f"task_{t.task_id}.png"
            image_file.write_bytes(base64.b64decode(t.image_b64))

        if not self.tasks:
            messagebox.showerror("Ошибка", "Получен пустой вариант")
            return

        self.current_idx = 0
        self.render_current_task()
        self.status_var.set(f"Экзамен начат. Заданий: {len(self.tasks)}")
        self.log("Вариант получен, экзамен начат")

    def apply_internet_policy(self, block: bool):
        if block:
            if not self.client:
                return
            self.blocker = InternetBlocker(self.client.host)
            ok, info = self.blocker.apply()
            self.internet_blocked = ok
            self.log(info if ok else f"Ошибка блокировки: {info}")
            self.send_internet_status(ok=ok, message=info, blocked=ok)
            return

        if self.blocker:
            self.blocker.remove()
        self.internet_blocked = False
        info = "Блокировка интернета снята"
        self.log(info)
        self.send_internet_status(ok=True, message=info, blocked=False)

    def send_internet_status(self, ok: bool, message: str, blocked: bool):
        if not self.client:
            return
        try:
            self.client.send(
                {
                    "type": "internet_status",
                    "ok": ok,
                    "message": message,
                    "blocked": blocked,
                    "at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }
            )
        except Exception:
            pass

    def render_current_task(self):
        if not self.tasks:
            return
        self.save_current_answer()
        t = self.tasks[self.current_idx]
        self.task_title_var.set(f"Задание {t.task_id} / {len(self.tasks)}")

        img_path = self.temp_dir / f"task_{t.task_id}.png"
        try:
            self.current_image = tk.PhotoImage(file=str(img_path))
            self.image_label.configure(image=self.current_image, text="")
        except tk.TclError:
            self.current_image = None
            self.image_label.configure(image="", text=f"Файл: {img_path.name}")

        self.answer_var.set(self.answers.get(str(t.task_id), ""))

    def save_current_answer(self):
        if not self.tasks:
            return
        t = self.tasks[self.current_idx]
        self.answers[str(t.task_id)] = self.answer_var.get()

    def next_task(self):
        if not self.tasks:
            return
        self.save_current_answer()
        self.current_idx = min(self.current_idx + 1, len(self.tasks) - 1)
        self.render_current_task()

    def prev_task(self):
        if not self.tasks:
            return
        self.save_current_answer()
        self.current_idx = max(self.current_idx - 1, 0)
        self.render_current_task()

    def finish_exam(self):
        if not self.tasks:
            return
        self.save_current_answer()
        if not messagebox.askyesno("Подтверждение", "Завершить тест и отправить результат?"):
            return
        score, max_score, per_task = score_answers(self.tasks, self.answers)
        payload = {
            "type": "submission",
            "student_name": self.name_var.get().strip(),
            "score": score,
            "max_score": max_score,
            "answers": self.answers,
            "per_task": per_task,
            "finished_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        if self.client:
            try:
                self.client.send(payload)
                messagebox.showinfo("Результат", f"Отправлено: {score}/{max_score}")
                self.log(f"Результат отправлен: {score}/{max_score}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось отправить результат: {e}")

    def on_close(self):
        try:
            if self.blocker:
                self.blocker.remove()
            if self.client:
                self.client.close()
        finally:
            self.destroy()


if __name__ == "__main__":
    app = StudentApp()
    app.mainloop()
