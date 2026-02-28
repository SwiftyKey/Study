import os
import subprocess

def build_app():
    app_name = ""

    cmd = [
        "flet", "pack",
        "ege_students_app.py",
        "--name", "EGE_Student_App",
        "--add-data", "config;config",
        "--add-data", "database;database",
        "--add-data", "ui;ui",
        "--add-data", "services;services",
        "--add-data", "utils;utils",
    ]

    subprocess.run(cmd)
    print(f"✅ {app_name} собран успешно!")

if __name__ == "__main__":
    build_app()
