"""Настройки путей и цветов по руководству стилю (Прил. 3)."""

from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
DB_PATH = APP_DIR / "velodrive.db"
IMAGES_DIR = APP_DIR / "images"
SQL_SCRIPT_PATH = APP_DIR / "database.sql"

# Папка import: рядом с проектом или в материалах задания
IMPORT_DIR = APP_DIR / "import"
if not IMPORT_DIR.exists():
    IMPORT_DIR = (
        APP_DIR.parent
        / "1 смена"
        / "Приложения из ПРИЛ В2 КОД"
        / "Задание 1"
        / "import"
    )

PICTURE_PLACEHOLDER = IMPORT_DIR / "picture.png"
ICON_PATH = IMPORT_DIR / "icon.ico"
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
