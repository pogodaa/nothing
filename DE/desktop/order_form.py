"""Форма добавления и редактирования заказа (только администратор)."""

import tkinter as tk
from tkinter import ttk

import config
import database as db
import helpers


class OrderFormWindow(tk.Toplevel):
    def __init__(self, parent, app, order_id: int | None, on_saved=None):
        super().__init__(parent)
        self.app = app
        self.order_id = order_id
        self.is_edit = order_id is not None
        self.on_saved = on_saved
        app.order_form_open = self

        self.title("Редактирование заказа" if self.is_edit else "Добавление заказа")
        self.geometry("520x540")
        self.minsize(520, 540)
        self.resizable(False, False)
        helpers.setup_window_icon(self)
        self.protocol("WM_DELETE_WINDOW", self._close)

        self._original_snapshot = None

        self.pickup_points = db.get_pickup_points(self.app.conn)
        self.pickup_map = {p["address"]: p["id"] for p in self.pickup_points}
        self.pickup_names = list(self.pickup_map.keys())
        self.client_names = db.get_client_names(self.app.conn)

        self._build_ui()
        if self.is_edit:
            self._load_order()
        else:
            self.new_id = db.next_order_id(self.app.conn)

    def _build_ui(self) -> None:
        frame = tk.Frame(self, padx=15, pady=15)
        frame.pack(fill=tk.BOTH, expand=True)

        if self.is_edit:
            tk.Label(frame, text="Номер заказа (только чтение):").pack(anchor="w")
            self.id_var = tk.StringVar()
            ttk.Entry(frame, textvariable=self.id_var, state="readonly").pack(fill=tk.X, pady=2)

        tk.Label(frame, text="Артикул *").pack(anchor="w")
        self.articles_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.articles_var, width=50).pack(fill=tk.X, pady=2)
        tk.Label(
            frame,
            text="Пример: A112T4, 2, G843H5, 2",
            fg="gray",
            justify=tk.LEFT,
        ).pack(anchor="w", pady=(0, 4))

        tk.Label(frame, text="Статус заказа *").pack(anchor="w", pady=(8, 0))
        self.status_var = tk.StringVar()
        ttk.Combobox(
            frame,
            textvariable=self.status_var,
            values=config.ORDER_STATUSES,
            state="readonly",
        ).pack(fill=tk.X, pady=2)

        tk.Label(frame, text="Адрес пункта выдачи *").pack(anchor="w", pady=(8, 0))
        self.pickup_var = tk.StringVar()
        ttk.Combobox(
            frame,
            textvariable=self.pickup_var,
            values=self.pickup_names,
            state="readonly",
        ).pack(fill=tk.X, pady=2)

        tk.Label(frame, text="Дата заказа (ГГГГ-ММ-ДД) *").pack(anchor="w", pady=(8, 0))
        self.order_date_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.order_date_var).pack(fill=tk.X, pady=2)

        tk.Label(frame, text="Дата выдачи (ГГГГ-ММ-ДД) *").pack(anchor="w")
        self.delivery_date_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.delivery_date_var).pack(fill=tk.X, pady=2)

        tk.Label(frame, text="ФИО клиента *").pack(anchor="w", pady=(8, 0))
        self.client_var = tk.StringVar()
        self.client_combo = ttk.Combobox(
            frame,
            textvariable=self.client_var,
            values=self.client_names,
            state="readonly",
        )
        self.client_combo.pack(fill=tk.X, pady=2)

        tk.Label(frame, text="Код для получения").pack(anchor="w")
        self.code_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.code_var).pack(fill=tk.X, pady=2)

        buttons = tk.Frame(frame)
        buttons.pack(fill=tk.X, pady=15)
        tk.Button(
            buttons,
            text="Сохранить",
            bg=config.COLOR_ACCENT,
            fg="white",
            command=self._save,
        ).pack(side=tk.LEFT, padx=5)
        tk.Button(buttons, text="Назад", command=self._close).pack(side=tk.LEFT)

    def _load_order(self) -> None:
        order = db.get_order(self.app.conn, self.order_id)
        if not order:
            helpers.show_error("Ошибка", "Заказ не найден.")
            self._close()
            return
        self.id_var.set(str(order["id"]))
        self.articles_var.set(order.get("articles_text", ""))
        self.status_var.set((order.get("status") or "").strip())
        self.pickup_var.set(order.get("pickup_address", ""))
        self.order_date_var.set(order.get("order_date", ""))
        self.delivery_date_var.set(order.get("delivery_date", ""))
        client_name = (order.get("client_name") or "").strip()
        if client_name and client_name not in self.client_names:
            self.client_names = [client_name] + self.client_names
            self.client_combo.configure(values=self.client_names)
        self.client_var.set(client_name)
        self.code_var.set(str(order.get("pickup_code") or ""))
        self._original_snapshot = self._form_snapshot()

    def _form_snapshot(self) -> dict:
        return {
            "articles_text": self.articles_var.get().strip(),
            "status": self.status_var.get().strip(),
            "pickup_address": self.pickup_var.get().strip(),
            "order_date": self.order_date_var.get().strip(),
            "delivery_date": self.delivery_date_var.get().strip(),
            "client_name": self.client_var.get().strip(),
            "pickup_code": self.code_var.get().strip(),
        }

    def _has_unsaved_changes(self) -> bool:
        if not self.is_edit or self._original_snapshot is None:
            return False
        return self._form_snapshot() != self._original_snapshot

    def _save(self) -> None:
        articles = self.articles_var.get().strip()
        status = self.status_var.get().strip()
        pickup_address = self.pickup_var.get().strip()
        order_date = self.order_date_var.get().strip()
        delivery_date = self.delivery_date_var.get().strip()
        client_name = self.client_var.get().strip()

        if (
            not articles
            or not status
            or not pickup_address
            or not order_date
            or not delivery_date
            or not client_name
        ):
            helpers.show_error(
                "Ошибка",
                "Заполните обязательные поля:\n"
                "товары в заказе, статус, адрес, даты, ФИО клиента.",
                parent=self,
            )
            return

        if client_name not in self.client_names:
            helpers.show_error("Ошибка", "Выберите клиента из списка.", parent=self)
            return

        date_error = helpers.validate_date(order_date, "Дата заказа")
        if date_error:
            helpers.show_error("Ошибка", date_error, parent=self)
            return

        date_error = helpers.validate_date(delivery_date, "Дата выдачи")
        if date_error:
            helpers.show_error("Ошибка", date_error, parent=self)
            return

        articles_error = helpers.validate_order_articles(self.app.conn, articles)
        if articles_error:
            helpers.show_error("Ошибка", articles_error, parent=self)
            return

        pickup_point_id = self.pickup_map.get(pickup_address)
        if pickup_point_id is None:
            helpers.show_error("Ошибка", "Выберите адрес пункта выдачи из списка.", parent=self)
            return

        try:
            pickup_code = int(self.code_var.get()) if self.code_var.get().strip() else None
        except ValueError:
            helpers.show_error("Ошибка", "Код для получения должен быть числом.", parent=self)
            return

        data = {
            "id": self.order_id if self.is_edit else self.new_id,
            "articles_text": articles,
            "order_date": order_date,
            "delivery_date": delivery_date,
            "pickup_point_id": pickup_point_id,
            "client_name": client_name,
            "pickup_code": pickup_code,
            "status": status,
        }

        if self.is_edit:
            if not self._has_unsaved_changes():
                helpers.show_info("Информация", "Изменений нет.")
                return
            if not helpers.ask_yes_no(
                "Подтверждение",
                "Сохранить изменения заказа в базе данных?",
                parent=self,
            ):
                return

        try:
            if self.is_edit:
                db.update_order(self.app.conn, self.order_id, data)
            else:
                db.insert_order(self.app.conn, data)
            helpers.show_info("Информация", "Заказ сохранён.")
            self._close()
            if self.on_saved:
                self.on_saved()
        except Exception:
            helpers.show_error(
                "Ошибка",
                "Не удалось сохранить заказ.\n"
                "Проверьте артикулы, даты и выбранные значения из списков.",
                parent=self,
            )

    def _close(self) -> None:
        if self._has_unsaved_changes():
            if not helpers.ask_yes_no(
                "Подтверждение",
                "Есть несохранённые изменения.\nЗакрыть форму без сохранения?",
                parent=self,
            ):
                return
        self.app.order_form_open = None
        self.destroy()
