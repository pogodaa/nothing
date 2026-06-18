"""Вспомогательные функции: картинки, сообщения, фильтрация."""

import re
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import messagebox

from PIL import Image, ImageTk

import config
import database as db


def _dialog_parent(parent: tk.Misc | None) -> tk.Misc:
    return parent if parent is not None else tk._default_root


def validate_date(value: str, field_name: str) -> str | None:
    value = (value or "").strip()
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return (
            f"{field_name}: используйте формат ГГГГ-ММ-ДД.\n"
            "Пример: 2023-02-27"
        )
    try:
        datetime.strptime(value, "%Y-%m-%d")
    except ValueError:
        return f"{field_name}: дата «{value}» некорректна."
    return None


def validate_order_articles(conn, articles_text: str) -> str | None:
    text = (articles_text or "").strip()
    if not text:
        return "Товары в заказе: укажите артикулы и количество через запятую."

    pairs = db.parse_articles_text(text)
    if not pairs:
        return (
            "Товары в заказе: неверный формат.\n"
            "Пример: A112T4, 2, G843H5, 2"
        )

    for article, qty in pairs:
        if qty <= 0:
            return f"Количество для артикула «{article}» должно быть больше 0."
        if not db.get_product_by_article(conn, article):
            return (
                f"Артикул товара «{article}» не найден в каталоге.\n"
                "Откройте список товаров и скопируйте существующий артикул.\n"
                "Пример: A112T4, 2, G843H5, 2"
            )
    return None


def show_info(title: str, text: str, parent: tk.Misc | None = None) -> None:
    messagebox.showinfo(title, text, parent=_dialog_parent(parent))


def show_warning(title: str, text: str, parent: tk.Misc | None = None) -> None:
    messagebox.showwarning(title, text, parent=_dialog_parent(parent))


def show_error(title: str, text: str, parent: tk.Misc | None = None) -> None:
    messagebox.showerror(title, text, parent=_dialog_parent(parent))


def ask_yes_no(title: str, text: str, parent: tk.Misc | None = None) -> bool:
    return messagebox.askyesno(title, text, parent=_dialog_parent(parent))


def sort_label_to_key(label: str) -> str:
    return config.SORT_KEYS.get(label, "quantity")


def load_logo(max_height: int = 64) -> ImageTk.PhotoImage | None:
    """Логотип компании для главной формы (Прил. 3, icon.png из import)."""
    for candidate in (config.LOGO_PATH, config.IMPORT_DIR / "icon.jpg", config.PICTURE_PLACEHOLDER):
        if candidate.exists():
            image = Image.open(candidate)
            width, height = image.size
            if height > max_height:
                width = max(1, int(width * max_height / height))
                height = max_height
                image = image.resize((width, height), Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(image)
    return None


def resolve_photo_path(path: str | None) -> Path:
    """Путь к фото: относительный — от APP_DIR, абсолютный — как есть."""
    if not path:
        candidate = config.PICTURE_PLACEHOLDER
    else:
        candidate = Path(path)
        if not candidate.is_absolute():
            candidate = config.APP_DIR / candidate
    if candidate.exists():
        return candidate
    if config.PICTURE_PLACEHOLDER.exists():
        return config.PICTURE_PLACEHOLDER
    return candidate


def load_photo(path: str, width: int = 120, height: int = 90) -> ImageTk.PhotoImage | None:
    file_path = resolve_photo_path(path)
    if not file_path.exists():
        return None
    image = Image.open(file_path)
    image.thumbnail((width, height), Image.Resampling.LANCZOS)
    return ImageTk.PhotoImage(image)


def save_product_image(source_path: str, article: str) -> str:
    """Сохраняет фото в images/ и возвращает относительный путь для БД."""
    config.IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    target = config.IMAGES_DIR / f"{article}.jpg"
    image = Image.open(source_path)
    image = image.resize((300, 200), Image.Resampling.LANCZOS)
    image.convert("RGB").save(target, "JPEG", quality=85)
    return target.relative_to(config.APP_DIR).as_posix()


def remove_file_if_exists(path: str | None) -> None:
    if not path:
        return
    file_path = resolve_photo_path(path)
    images_dir = config.IMAGES_DIR.resolve()
    if file_path.exists() and file_path.resolve().parent == images_dir:
        file_path.unlink()


def product_matches_search(product: dict, query: str) -> bool:
    if not query:
        return True
    query = query.lower()
    text_fields = [
        product.get("article", ""),
        product.get("name", ""),
        product.get("unit", ""),
        product.get("supplier", ""),
        product.get("manufacturer", ""),
        product.get("category", ""),
        product.get("description", ""),
        str(product.get("price", "")),
        str(product.get("discount", "")),
        str(product.get("quantity", "")),
    ]
    return any(query in str(value).lower() for value in text_fields)


def product_matches_discount_filter(product: dict, discount_range) -> bool:
    if discount_range is None:
        return True
    low, high = discount_range
    discount = float(product.get("discount") or 0)
    return low <= discount <= high


def sort_products(products: list[dict], sort_key: str, descending: bool) -> list[dict]:
    key_map = {
        "quantity": lambda p: int(p.get("quantity") or 0),
        "price": lambda p: float(p.get("price") or 0),
        "discount": lambda p: float(p.get("discount") or 0),
    }
    if sort_key not in key_map:
        return products
    return sorted(products, key=key_map[sort_key], reverse=descending)


def setup_window_icon(window: tk.Tk | tk.Toplevel) -> None:
    """Иконка окна: на Linux — iconphoto + import/icon.png; на Windows — также .ico."""
    import sys

    candidates = [config.ICON_PATH]
    if sys.platform == "win32":
        candidates.append(config.ICON_PATH_FALLBACK)

    for candidate in candidates:
        if not candidate.exists():
            continue
        # .ico — только Windows (iconbitmap); на Linux не используется
        if candidate.suffix.lower() == ".ico":
            if sys.platform != "win32":
                continue
            try:
                window.iconbitmap(str(candidate))
                return
            except tk.TclError:
                continue
        try:
            image = Image.open(candidate)
            photo = ImageTk.PhotoImage(image)
            window.iconphoto(True, photo)
            # Ссылка на PhotoImage, иначе GC удалит иконку
            window._icon_photo = photo
            return
        except (OSError, tk.TclError):
            continue


def bind_mousewheel(canvas: tk.Canvas, widget: tk.Widget) -> None:
    """Прокрутка списка колёсиком мыши (Linux: Button-4/5, Windows: MouseWheel)."""

    def on_mousewheel(event):
        if event.num == 5 or event.delta < 0:
            canvas.yview_scroll(1, "units")
        elif event.num == 4 or event.delta > 0:
            canvas.yview_scroll(-1, "units")

    def on_enter(_event):
        canvas.bind_all("<MouseWheel>", on_mousewheel)
        canvas.bind_all("<Button-4>", on_mousewheel)
        canvas.bind_all("<Button-5>", on_mousewheel)

    def on_leave(_event):
        canvas.unbind_all("<MouseWheel>")
        canvas.unbind_all("<Button-4>")
        canvas.unbind_all("<Button-5>")

    widget.bind("<Enter>", on_enter)
    widget.bind("<Leave>", on_leave)
    canvas.bind("<Enter>", on_enter)
    canvas.bind("<Leave>", on_leave)


def format_user_header(user: dict | None, role: str) -> str:
    if user:
        return f"{user['full_name']} — {user['role']}"
    return config.ROLES.get(role, role)


def make_header(parent: tk.Widget, title: str, user_name: str, on_logout) -> tk.Frame:
    frame = tk.Frame(parent, bg=config.COLOR_HEADER, height=70)
    frame.pack(fill=tk.X)
    frame.pack_propagate(False)

    tk.Label(
        frame,
        text=title,
        font=config.FONT_TITLE,
        bg=config.COLOR_HEADER,
        fg="white",
    ).pack(side=tk.LEFT, padx=15, pady=15)

    right = tk.Frame(frame, bg=config.COLOR_HEADER)
    right.pack(side=tk.RIGHT, padx=15, pady=15)

    tk.Label(
        right,
        text=user_name,
        font=config.FONT_BOLD,
        bg=config.COLOR_HEADER,
        fg="white",
    ).pack(side=tk.LEFT, padx=8)

    tk.Button(
        right,
        text="Выход",
        bg=config.COLOR_ACCENT,
        fg="white",
        command=on_logout,
    ).pack(side=tk.LEFT)

    return frame
