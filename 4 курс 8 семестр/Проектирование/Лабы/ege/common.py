import base64
import csv
import json
import os
import socket
import struct
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple


@dataclass
class Task:
    task_id: int
    image_rel_path: str
    image_b64: str
    correct_answer: str
    points: int = 1


def recv_exact(sock: socket.socket, n: int) -> bytes:
    data = bytearray()
    while len(data) < n:
        chunk = sock.recv(n - len(data))
        if not chunk:
            raise ConnectionError("Socket closed while receiving data")
        data.extend(chunk)
    return bytes(data)


def send_json(sock: socket.socket, payload: Dict) -> None:
    raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    sock.sendall(struct.pack("!I", len(raw)))
    sock.sendall(raw)


def recv_json(sock: socket.socket) -> Dict:
    header = recv_exact(sock, 4)
    length = struct.unpack("!I", header)[0]
    body = recv_exact(sock, length)
    return json.loads(body.decode("utf-8"))


def parse_variant_folder(folder: str) -> List[Task]:
    root = Path(folder)
    csv_candidates = list(root.glob("*.csv"))
    if not csv_candidates:
        raise FileNotFoundError("В папке варианта не найден CSV файл")
    csv_path = csv_candidates[0]

    tasks: List[Task] = []
    with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        for idx, row in enumerate(reader, start=1):
            if not row or all(not c.strip() for c in row):
                continue
            if len(row) < 2:
                raise ValueError(
                    f"Некорректная строка CSV #{idx}: нужно минимум 2 столбца "
                    "(путь_к_картинке, правильный_ответ[, баллы])"
                )
            image_rel = row[0].strip()
            answer = row[1].strip()
            points = 1
            if len(row) >= 3 and row[2].strip():
                points = int(row[2].strip())

            image_path = (root / image_rel).resolve()
            if not image_path.exists():
                raise FileNotFoundError(f"Файл изображения не найден: {image_rel}")

            image_bytes = image_path.read_bytes()
            tasks.append(
                Task(
                    task_id=len(tasks) + 1,
                    image_rel_path=image_rel.replace("\\", "/"),
                    image_b64=base64.b64encode(image_bytes).decode("ascii"),
                    correct_answer=answer,
                    points=points,
                )
            )
    if not tasks:
        raise ValueError("CSV не содержит заданий")
    return tasks


def score_answers(tasks: List[Task], answers: Dict[str, str]) -> Tuple[int, int, List[Dict]]:
    total = 0
    max_total = 0
    per_task = []
    for t in tasks:
        max_total += t.points
        user_ans = (answers.get(str(t.task_id), "") or "").strip()
        ok = user_ans.lower() == t.correct_answer.strip().lower()
        gained = t.points if ok else 0
        total += gained
        per_task.append(
            {
                "task_id": t.task_id,
                "correct": ok,
                "gained": gained,
                "max_points": t.points,
                "user_answer": user_ans,
                "correct_answer": t.correct_answer,
            }
        )
    return total, max_total, per_task


def run_netsh(args: List[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["netsh", "advfirewall", "firewall", *args],
        capture_output=True,
        text=True,
        check=False,
    )


def add_firewall_rule(
    name: str, direction: str, action: str, remoteip: str = "any"
) -> subprocess.CompletedProcess:
    return run_netsh(
        [
            "add",
            "rule",
            f"name={name}",
            f"dir={direction}",
            f"action={action}",
            "enable=yes",
            "profile=any",
            f"remoteip={remoteip}",
        ]
    )


def delete_firewall_rule(name: str) -> subprocess.CompletedProcess:
    return run_netsh(["delete", "rule", f"name={name}"])


class InternetBlocker:
    """
    Временная блокировка исходящего интернета через Windows Firewall.
    Требует запуск приложения от имени администратора.
    """

    def __init__(self, teacher_ip: str):
        self.teacher_ip = teacher_ip
        self.rule_block = "EGE_Student_Block_All_Internet_Temp"
        self.rule_allow_local = "EGE_Student_Allow_LocalSubnet_Temp"
        self.rule_allow_teacher = "EGE_Student_Allow_Teacher_Temp"
        self.applied = False

    def apply(self) -> Tuple[bool, str]:
        if os.name != "nt":
            return False, "Блокировка интернета реализована только для Windows"

        delete_firewall_rule(self.rule_block)
        delete_firewall_rule(self.rule_allow_local)
        delete_firewall_rule(self.rule_allow_teacher)

        r1 = add_firewall_rule(self.rule_allow_local, "out", "allow", "localsubnet")
        r2 = add_firewall_rule(self.rule_allow_teacher, "out", "allow", self.teacher_ip)
        r3 = add_firewall_rule(self.rule_block, "out", "block", "any")
        if any(r.returncode != 0 for r in (r1, r2, r3)):
            err = (r1.stderr or r2.stderr or r3.stderr or "").strip()
            return False, f"Не удалось применить firewall-правила. Нужны права администратора. {err}"

        self.applied = True
        return True, "Правила блокировки интернета применены"

    def remove(self) -> Tuple[bool, str]:
        if os.name != "nt":
            return False, "Разблокировка реализована только для Windows"

        r1 = delete_firewall_rule(self.rule_block)
        r2 = delete_firewall_rule(self.rule_allow_local)
        r3 = delete_firewall_rule(self.rule_allow_teacher)
        self.applied = False
        if any(r.returncode != 0 for r in (r1, r2, r3)):
            err = (r1.stderr or r2.stderr or r3.stderr or "").strip()
            return False, f"Не удалось удалить часть firewall-правил. {err}"
        return True, "Блокировка интернета снята"
