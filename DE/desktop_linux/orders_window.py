"""Список заказов для менеджера и администратора."""

import tkinter as tk
from tkinter import ttk

import config
import helpers
from order_form import OrderFormWindow


class OrdersWindow(tk.Toplevel):
    def __init__(self, parent, app, user, role: str):
        super().__init__(parent)
        self.app = app
        self.user = user
        self.role = role
        self.user_name = helpers.format_user_header(user, role)

        self.title("Заказы — ООО «ВелосипедДрайв»")
        self.geometry("900x600")
        helpers.setup_window_icon(self)
        self._build_ui()
        self.refresh_list()
        if app.order_form_open:
            pass

    def _build_ui(self) -> None:
        helpers.make_header(
            self,
            "Заказы",
            self.user_name,
            self.destroy,
        )

        toolbar = tk.Frame(self, padx=10, pady=8)
        toolbar.pack(fill=tk.X)

        if self.role == "admin":
            tk.Button(
                toolbar,
                text="Добавить заказ",
                bg=config.COLOR_ACCENT,
                fg="white",
                command=self._add_order,
            ).pack(side=tk.RIGHT)

        tk.Button(toolbar, text="Назад к товарам", command=self.destroy).pack(side=tk.LEFT)

        container = tk.Frame(self)
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.canvas = tk.Canvas(container, highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient=tk.VERTICAL, command=self.canvas.yview)
        self.list_frame = tk.Frame(self.canvas)

        self.list_frame.bind(
            "<Configure>",
            lambda _e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )
        self.canvas_window = self.canvas.create_window((0, 0), window=self.list_frame, anchor="nw")
        self.canvas.bind("<Configure>", self._on_canvas_resize)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        helpers.bind_mousewheel(self.canvas, self.list_frame)

    def _on_canvas_resize(self, event) -> None:
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def refresh_list(self) -> None:
        import database as db

        for child in self.list_frame.winfo_children():
            child.destroy()

        orders = db.get_all_orders(self.app.conn)
        if not orders:
            tk.Label(self.list_frame, text="Заказы не найдены").pack(pady=20)
            return

        for order in orders:
            self._draw_order_card(order)

    def _draw_order_card(self, order: dict) -> None:
        card = tk.Frame(self.list_frame, bd=1, relief=tk.GROOVE, padx=10, pady=10)
        card.pack(fill=tk.X, pady=5)

        left = tk.Frame(card)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tk.Label(
            left,
            text=f"Артикул заказа: {order.get('articles_text', '')}",
            font=config.FONT_BOLD,
            anchor="w",
            wraplength=520,
            justify=tk.LEFT,
        ).pack(anchor="w")
        tk.Label(left, text=f"Статус заказа: {order.get('status', '')}", anchor="w").pack(anchor="w")
        address = order.get("pickup_address") or f"ПВЗ #{order.get('pickup_point_id')}"
        tk.Label(left, text=f"Адрес пункта выдачи: {address}", anchor="w").pack(anchor="w")
        tk.Label(left, text=f"Дата заказа: {order.get('order_date', '')}", anchor="w").pack(anchor="w")

        right = tk.Frame(card, bd=1, relief=tk.SUNKEN, padx=10, pady=10)
        right.pack(side=tk.RIGHT)
        tk.Label(right, text="Дата доставки", font=config.FONT_BOLD).pack()
        tk.Label(right, text=order.get("delivery_date", "")).pack()

        if self.role == "admin":
            actions = tk.Frame(card)
            actions.pack(side=tk.RIGHT, padx=8)
            tk.Button(
                actions,
                text="Изменить",
                command=lambda oid=order["id"]: self._edit_order(oid),
            ).pack(pady=2)
            tk.Button(
                actions,
                text="Удалить",
                command=lambda oid=order["id"]: self._delete_order(oid),
            ).pack(pady=2)
            skip = self._widget_tree(actions)
            self._bind_order_edit_click(card, order["id"], skip)

    def _widget_tree(self, root: tk.Widget) -> set:
        widgets = {root}
        for child in root.winfo_children():
            widgets |= self._widget_tree(child)
        return widgets

    def _bind_order_edit_click(self, widget: tk.Widget, order_id: int, skip: set) -> None:
        """По ТЗ: редактирование заказа — при нажатии на элемент в списке."""
        if widget in skip or isinstance(widget, tk.Button):
            return
        widget.bind(
            "<Button-1>",
            lambda _e, oid=order_id: self._edit_order(oid),
        )
        widget.configure(cursor="hand2")
        for child in widget.winfo_children():
            self._bind_order_edit_click(child, order_id, skip)

    def _open_order_form(self, order_id: int | None) -> None:
        if self.app.order_form_open:
            helpers.show_warning(
                "Предупреждение",
                "Уже открыто окно редактирования заказа.",
            )
            return
        OrderFormWindow(self, self.app, order_id=order_id, on_saved=self.refresh_list)

    def _add_order(self) -> None:
        self._open_order_form(None)

    def _edit_order(self, order_id: int) -> None:
        self._open_order_form(order_id)

    def _delete_order(self, order_id: int) -> None:
        import database as db

        if not helpers.ask_yes_no("Подтверждение", "Удалить заказ? Действие необратимо.", parent=self):
            return
        db.delete_order(self.app.conn, order_id)
        helpers.show_info("Информация", "Заказ удалён.")
        self.refresh_list()
