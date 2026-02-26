import os
import subprocess
from typing import List, Tuple
from config.settings import TEACHER_IP


def run_netsh(args: List[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["netsh", "advfirewall", "firewall", *args],
        capture_output=True,
        text=True,
        check=False,
        creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
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
    def __init__(self, teacher_ip: str = TEACHER_IP):
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

    def __enter__(self):
        self.apply()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.remove()
