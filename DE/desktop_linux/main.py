"""
ООО «ВелосипедДрайв» — демонстрационный экзамен, вариант 2 (Linux Ubuntu).

Запуск из папки desktop_linux:
    python3 main.py

При первом запуске база velodrive.db создаётся автоматически из import/*.xlsx.
"""

import tkinter as tk

import config
import database as db
import helpers
import import_data
from login_window import LoginWindow
from products_window import ProductsWindow


class App:
    def __init__(self):
        self.root = None
        self.login_window = None
        self.products_window = None
        self.product_form_open = None
        self.order_form_open = None
        self.conn = None
        self._prepare_database()

    def _prepare_database(self) -> None:
        """Создаёт velodrive.db при первом запуске и импортирует данные из import/."""
        first_run = not config.DB_PATH.exists()
        self.conn = db.get_connection()  # sqlite3 создаёт файл, если его ещё нет
        db.init_schema(self.conn)
        if first_run or db.user_count(self.conn) == 0:
            import_data.import_all(self.conn)
        db.fix_stored_articles(self.conn)

    def run(self) -> None:
        self.show_login()
        if self.login_window:
            self.login_window.mainloop()

    def show_login(self) -> None:
        if self.products_window and self.products_window.winfo_exists():
            self.products_window.destroy()
            self.products_window = None
        if self.login_window and self.login_window.winfo_exists():
            self.login_window.deiconify()
            self.login_window.lift()
            self.login_window.login_entry.delete(0, tk.END)
            self.login_window.password_entry.delete(0, tk.END)
        else:
            self.login_window = LoginWindow(self)

    def open_products(self, user, role: str) -> None:
        if self.login_window:
            self.login_window.withdraw()
        self.products_window = ProductsWindow(self, user, role)
        self.products_window.focus()


def main() -> None:
    if not config.IMPORT_DIR.exists():
        root = tk.Tk()
        root.withdraw()
        helpers.show_error(
            "Ошибка",
            f"Папка import не найдена:\n{config.IMPORT_DIR}\n\n"
            "Положите xlsx и картинки в папку import/ рядом с main.py.",
            parent=root,
        )
        root.destroy()
        return

    # Папка для новых фото (создаётся заранее, чтобы не было ошибок при сохранении)
    config.IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    app = App()
    app.run()


if __name__ == "__main__":
    main()
