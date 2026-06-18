"""Настройки путей и цветов по руководству стилю (Прил. 3).

Все пути строятся относительно папки проекта (APP_DIR) — без C:\\...
Работает одинаково на Linux Ubuntu и Windows.
"""

from pathlib import Path

# Корень проекта: каталог, где лежит main.py (desktop_linux/)
APP_DIR = Path(__file__).resolve().parent

# SQLite-база: создаётся автоматически при первом запуске из import/
DB_PATH = APP_DIR / "velodrive.db"

# Новые фото товаров (администратор) — пути в БД хранятся относительно APP_DIR
IMAGES_DIR = APP_DIR / "images"

# SQL-скрипт для сдачи модуля 1 (генерируется other/build_sql.py)
SQL_SCRIPT_PATH = APP_DIR / "database.sql"

# Исходные xlsx и картинки для первичного импорта
IMPORT_DIR = APP_DIR / "import"

PICTURE_PLACEHOLDER = IMPORT_DIR / "picture.png"

# Иконка окна: по умолчанию PNG (Linux); ICO — запасной вариант для Windows
ICON_PATH = IMPORT_DIR / "icon.png"
ICON_PATH_FALLBACK = IMPORT_DIR / "icon.ico"
LOGO_PATH = IMPORT_DIR / "icon.png"

# Цвета
COLOR_BG = "#FFFFFF"
COLOR_HEADER = "#6A5ACD"
COLOR_ACCENT = "#4B0082"
COLOR_DISCOUNT_ROW = "#483D8B"
COLOR_OUT_OF_STOCK = "#D3D3D3"
COLOR_PRICE_OLD = "#FF0000"
COLOR_PRICE_NEW = "#000000"

FONT_FAMILY = "Arial"
FONT_NORMAL = (FONT_FAMILY, 10)
FONT_BOLD = (FONT_FAMILY, 10, "bold")
FONT_TITLE = (FONT_FAMILY, 14, "bold")

ROLES = {
    "guest": "Гость",
    "client": "Авторизированный клиент",
    "manager": "Менеджер",
    "admin": "Администратор",
}

DISCOUNT_FILTERS = [
    ("Все диапазоны", None),
    ("0 – 11,99%", (0, 11.99)),
    ("12 – 18,99%", (12, 18.99)),
    ("19% и более", (19, 100)),
]

# В Tovar.xlsx у всех товаров единица измерения — «шт.»
PRODUCT_UNITS = ["шт."]

SORT_OPTIONS = [
    ("Количество на складе", "quantity"),
    ("Цена", "price"),
    ("Действующая скидка", "discount"),
]
SORT_LABELS = [label for label, _ in SORT_OPTIONS]
DEFAULT_SORT_LABEL = SORT_OPTIONS[0][0]
SORT_KEYS = {label: key for label, key in SORT_OPTIONS}

ORDER_STATUSES = ["Новый", "Завершен"]
