"""Окно входа — первый экран приложения."""

import tkinter as tk
from tkinter import ttk

import config
import database as db
import helpers


class LoginWindow(tk.Tk):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.title("Вход — ООО «ВелосипедДрайв»")
        self.configure(bg=config.COLOR_BG)
        self.geometry("480x450")
        self.resizable(False, False)
        self.logo_image = None
        helpers.setup_window_icon(self)
        self._build_ui()

    def _build_ui(self) -> None:
        header = tk.Frame(self, bg=config.COLOR_HEADER, height=100)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        header_inner = tk.Frame(header, bg=config.COLOR_HEADER)
        header_inner.pack(expand=True, pady=12)

        self.logo_image = helpers.load_logo(max_height=70)
        if self.logo_image:
            tk.Label(
                header_inner,
                image=self.logo_image,
                bg=config.COLOR_HEADER,
            ).pack(side=tk.LEFT, padx=(15, 10))

        tk.Label(
            header_inner,
            text="ООО «ВелосипедДрайв»",
            font=config.FONT_TITLE,
            bg=config.COLOR_HEADER,
            fg="white",
        ).pack(side=tk.LEFT)

        body = tk.Frame(self, bg=config.COLOR_BG, padx=30, pady=20)
        body.pack(fill=tk.BOTH, expand=True)

        tk.Label(body, text="Логин:", font=config.FONT_NORMAL, bg=config.COLOR_BG).pack(anchor="w")
        self.login_entry = ttk.Entry(body, width=40)
        self.login_entry.pack(fill=tk.X, pady=(0, 10))

        tk.Label(body, text="Пароль:", font=config.FONT_NORMAL, bg=config.COLOR_BG).pack(anchor="w")
        self.password_entry = ttk.Entry(body, width=40, show="*")
        self.password_entry.pack(fill=tk.X, pady=(0, 15))

        tk.Button(
            body,
            text="Войти",
            bg=config.COLOR_ACCENT,
            fg="white",
            font=config.FONT_BOLD,
            command=self._login,
        ).pack(fill=tk.X, pady=5)

        tk.Button(
            body,
            text="Просмотр товаров (гость)",
            command=self._guest,
        ).pack(fill=tk.X, pady=5)

        self.password_entry.bind("<Return>", lambda _e: self._login())

    def _login(self) -> None:
        login = self.login_entry.get().strip()
        password = self.password_entry.get()
        if not login or not password:
            helpers.show_warning(
                "Предупреждение",
                "Введите логин и пароль.\nЕсли нет учётной записи — войдите как гость.",
            )
            return
        user = db.authenticate(self.app.conn, login, password)
        if not user:
            helpers.show_error(
                "Ошибка авторизации",
                "Неверный логин или пароль.\nПроверьте данные или войдите как гость.",
            )
            return
        role = db.role_key(user["role"])
        self.app.open_products(user=user, role=role)

    def _guest(self) -> None:
        self.app.open_products(user=None, role="guest")
