from pathlib import Path

# Цветовая палитра
COLOR_BG = "#000000"
COLOR_ACTIVE = "#40E0D0"
COLOR_TEXT = "#FFFFFF"
COLOR_SURFACE = "#1a1a1a"
COLOR_ERROR = "#ff4444"
COLOR_SUCCESS = "#00C851"

# База данных
DB_NAME = "ege_tasks.db"
DB_PASSWORD = "admin123"

# Таймер экзамена (секунды)
EXAM_DURATION_SECONDS = 3 * 60 * 60 + 55 * 60  # 3 часа 55 минут

# Пути
BASE_DIR = Path(__file__).parent.parent
DB_PATH = BASE_DIR / DB_NAME

# IP учителя для исключения из блокировки
TEACHER_IP = "192.168.0.108"
