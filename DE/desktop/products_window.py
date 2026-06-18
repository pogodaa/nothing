"""Список товаров с поиском, фильтром и сортировкой."""

import tkinter as tk
from tkinter import ttk

import config
import database as db
import helpers
from order_form import OrderFormWindow
from orders_window import OrdersWindow
from product_form import ProductFormWindow


class ProductsWindow(tk.Toplevel):
    def __init__(self, app, user, role: str):
        super().__init__(app.root)
        self.app = app
        self.user = user
        self.role = role
        self.user_name = helpers.format_user_header(user, role)
        self.search_var = tk.StringVar()
        self.filter_var = tk.StringVar(value="Все диапазоны")
        self.sort_var = tk.StringVar(value=config.DEFAULT_SORT_LABEL)
        self.sort_desc_var = tk.BooleanVar(value=False)
        self.photo_cache = []

        self.title("Список товаров — ООО «ВелосипедДрайв»")
        self.geometry("1100x700")
        self.configure(bg=config.COLOR_BG)
        helpers.setup_window_icon(self)

        self.search_var.trace_add("write", lambda *_: self.refresh_list())
        self.filter_var.trace_add("write", lambda *_: self.refresh_list())
        self.sort_var.trace_add("write", lambda *_: self.refresh_list())
        self.sort_desc_var.trace_add("write", lambda *_: self.refresh_list())

        self._build_ui()
        self.refresh_list()
        self.protocol("WM_DELETE_WINDOW", self._logout)

    def _build_ui(self) -> None:
        helpers.make_header(
            self,
            "Список товаров",
            self.user_name,
            self._logout,
        )

        toolbar = tk.Frame(self, bg=config.COLOR_BG, padx=10, pady=8)
        toolbar.pack(fill=tk.X)

        if self.role in ("manager", "admin"):
            tk.Label(toolbar, text="Поиск:", bg=config.COLOR_BG).pack(side=tk.LEFT)
            ttk.Entry(toolbar, textvariable=self.search_var, width=25).pack(side=tk.LEFT, padx=5)

            tk.Label(toolbar, text="Скидка:", bg=config.COLOR_BG).pack(side=tk.LEFT, padx=(10, 0))
            ttk.Combobox(
                toolbar,
                textvariable=self.filter_var,
                values=[name for name, _ in config.DISCOUNT_FILTERS],
                state="readonly",
                width=16,
            ).pack(side=tk.LEFT, padx=5)

            tk.Label(toolbar, text="Сортировка:", bg=config.COLOR_BG).pack(side=tk.LEFT, padx=(10, 0))
            ttk.Combobox(
                toolbar,
                textvariable=self.sort_var,
                values=config.SORT_LABELS,
                state="readonly",
                width=22,
            ).pack(side=tk.LEFT, padx=5)
            ttk.Checkbutton(
                toolbar,
                text="По убыванию",
                variable=self.sort_desc_var,
            ).pack(side=tk.LEFT, padx=5)

        if self.role == "admin":
            tk.Button(
                toolbar,
                text="Добавить товар",
                bg=config.COLOR_ACCENT,
                fg="white",
                command=self._add_product,
            ).pack(side=tk.RIGHT, padx=5)

        if self.role in ("manager", "admin"):
            tk.Button(
                toolbar,
                text="Заказы",
                bg=config.COLOR_ACCENT,
                fg="white",
                command=self._open_orders,
            ).pack(side=tk.RIGHT, padx=5)

        container = tk.Frame(self)
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.canvas = tk.Canvas(container, bg=config.COLOR_BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient=tk.VERTICAL, command=self.canvas.yview)
        self.list_frame = tk.Frame(self.canvas, bg=config.COLOR_BG)

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
        # Ширина списка = ширина области просмотра, чтобы справа не уходило под скроллбар
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def _get_discount_range(self):
        name = self.filter_var.get()
        for label, value in config.DISCOUNT_FILTERS:
            if label == name:
                return value
        return None

    def refresh_list(self) -> None:
        for child in self.list_frame.winfo_children():
            child.destroy()
        self.photo_cache.clear()

        products = db.get_all_products(self.app.conn)
        if self.role in ("manager", "admin"):
            query = self.search_var.get().strip()
            discount_range = self._get_discount_range()
            products = [
                p
                for p in products
                if helpers.product_matches_search(p, query)
                and helpers.product_matches_discount_filter(p, discount_range)
            ]
            products = helpers.sort_products(
                products,
                helpers.sort_label_to_key(self.sort_var.get()),
                self.sort_desc_var.get(),
            )

        if not products:
            tk.Label(
                self.list_frame,
                text="Товары не найдены",
                font=config.FONT_NORMAL,
                bg=config.COLOR_BG,
            ).pack(pady=20)
            return

        for product in products:
            self._draw_product_card(product)

    def _row_background(self, product: dict) -> str:
        quantity = int(product.get("quantity") or 0)
        discount = float(product.get("discount") or 0)
        if quantity <= 0:
            return config.COLOR_OUT_OF_STOCK
        if discount > 15:
            return config.COLOR_DISCOUNT_ROW
        return config.COLOR_BG

    def _draw_product_card(self, product: dict) -> None:
        bg = self._row_background(product)
        fg = "white" if bg == config.COLOR_DISCOUNT_ROW else "black"

        card = tk.Frame(self.list_frame, bg=bg, bd=1, relief=tk.GROOVE, padx=8, pady=8)
        card.pack(fill=tk.X, pady=4, padx=4)
        card.columnconfigure(1, weight=1)

        # Слева — фото (как на макете стр. 4)
        photo_box = tk.Frame(card, bg=bg, bd=1, relief=tk.GROOVE, width=140, height=110)
        photo_box.grid(row=0, column=0, rowspan=2, padx=5, pady=5, sticky="nw")
        photo_box.pack_propagate(False)

        photo = helpers.load_photo(product.get("photo_path"), 130, 100)
        if photo:
            self.photo_cache.append(photo)
            tk.Label(photo_box, image=photo, bg=bg).pack(expand=True)
        else:
            tk.Label(photo_box, text="Фото", bg=bg, fg=fg).pack(expand=True)

        # Справа — блок «Действующая скидка»
        discount = float(product.get("discount") or 0)
        discount_frame = tk.Frame(card, bg=bg, bd=1, relief=tk.SUNKEN, padx=12, pady=12)
        discount_frame.grid(row=0, column=2, padx=8, pady=5, sticky="ne")
        tk.Label(
            discount_frame,
            text="Действующая\nскидка",
            font=config.FONT_NORMAL,
            bg=bg,
            fg=fg,
            justify=tk.CENTER,
        ).pack()
        tk.Label(
            discount_frame,
            text=f"{discount:.0f}%",
            font=config.FONT_BOLD,
            bg=bg,
            fg=fg,
        ).pack()

        if self.role == "admin":
            admin_box = tk.Frame(card, bg=bg)
            admin_box.grid(row=1, column=2, padx=8, sticky="ne")
            tk.Button(
                admin_box,
                text="Изменить",
                command=lambda p=product: self._edit_product(p["id"]),
            ).pack(pady=2, fill=tk.X)
            tk.Button(
                admin_box,
                text="Удалить",
                command=lambda p=product: self._delete_product(p),
            ).pack(pady=2, fill=tk.X)

        # По центру — поля как в ТЗ (каждое на своей строке)
        info = tk.Frame(card, bg=bg)
        info.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=8, pady=5)

        title = f"{product.get('category', '')} | {product.get('name', '')}"
        tk.Label(
            info,
            text=title,
            font=config.FONT_BOLD,
            bg=bg,
            fg=fg,
            anchor="w",
            wraplength=500,
            justify=tk.LEFT,
        ).pack(anchor="w")

        self._add_field_line(
            info,
            "Описание товара:",
            product.get("description", ""),
            bg,
            fg,
            wrap=500,
        )
        self._add_field_line(
            info,
            "Производитель:",
            product.get("manufacturer", ""),
            bg,
            fg,
        )
        self._add_field_line(
            info,
            "Поставщик:",
            product.get("supplier", ""),
            bg,
            fg,
        )

        price_line = tk.Frame(info, bg=bg)
        price_line.pack(anchor="w", fill=tk.X, pady=1)
        tk.Label(
            price_line,
            text="Цена:",
            font=config.FONT_NORMAL,
            bg=bg,
            fg=fg,
            width=22,
            anchor="w",
        ).pack(side=tk.LEFT)
        self._draw_price(price_line, product, bg)

        self._add_field_line(
            info,
            "Единица измерения:",
            product.get("unit", ""),
            bg,
            fg,
        )
        self._add_field_line(
            info,
            "Количество на складе:",
            str(product.get("quantity", 0)),
            bg,
            fg,
        )

        if self.role == "admin":
            skip = self._widget_tree(admin_box)
            self._bind_product_edit_click(card, product["id"], skip)

    def _widget_tree(self, root: tk.Widget) -> set[tk.Widget]:
        widgets = {root}
        for child in root.winfo_children():
            widgets |= self._widget_tree(child)
        return widgets

    def _bind_product_edit_click(
        self,
        widget: tk.Widget,
        product_id: int,
        skip: set[tk.Widget],
    ) -> None:
        """По ТЗ: редактирование — при нажатии на элемент товара в списке."""
        if widget in skip or isinstance(widget, tk.Button):
            return
        widget.bind(
            "<Button-1>",
            lambda _e, pid=product_id: self._edit_product(pid),
        )
        widget.configure(cursor="hand2")
        for child in widget.winfo_children():
            self._bind_product_edit_click(child, product_id, skip)

    def _add_field_line(
        self,
        parent: tk.Frame,
        label: str,
        value: str,
        bg: str,
        fg: str,
        wrap: int | None = None,
    ) -> None:
        line = tk.Frame(parent, bg=bg)
        line.pack(anchor="w", fill=tk.X, pady=1)
        tk.Label(
            line,
            text=label,
            font=config.FONT_NORMAL,
            bg=bg,
            fg=fg,
            width=22,
            anchor="w",
        ).pack(side=tk.LEFT, anchor="nw")
        text_kwargs = {
            "font": config.FONT_NORMAL,
            "bg": bg,
            "fg": fg,
            "anchor": "w",
            "justify": tk.LEFT,
        }
        if wrap:
            text_kwargs["wraplength"] = wrap
        tk.Label(line, text=str(value or ""), **text_kwargs).pack(side=tk.LEFT, fill=tk.X, expand=True)

    def _draw_price(self, parent, product: dict, bg: str) -> None:
        price = float(product.get("price") or 0)
        discount = float(product.get("discount") or 0)
        final = db.final_price(price, discount)
        fg = "white" if bg == config.COLOR_DISCOUNT_ROW else config.COLOR_PRICE_NEW

        if discount > 0:
            tk.Label(
                parent,
                text=f"{price:.2f} руб.",
                font=(config.FONT_FAMILY, 10, "overstrike"),
                fg=config.COLOR_PRICE_OLD,
                bg=bg,
            ).pack(side=tk.LEFT, padx=(0, 8))
            tk.Label(
                parent,
                text=f"{final:.2f} руб.",
                font=config.FONT_BOLD,
                fg=fg,
                bg=bg,
            ).pack(side=tk.LEFT)
        else:
            tk.Label(
                parent,
                text=f"{price:.2f} руб.",
                font=config.FONT_BOLD,
                fg=fg,
                bg=bg,
            ).pack(side=tk.LEFT)

    def _open_product_form(self, product_id: int | None) -> None:
        if self.app.product_form_open:
            helpers.show_warning(
                "Предупреждение",
                "Уже открыто окно редактирования.\nЗакройте его перед открытием нового.",
            )
            return
        ProductFormWindow(self, self.app, product_id=product_id)

    def _add_product(self) -> None:
        self._open_product_form(None)

    def _edit_product(self, product_id: int) -> None:
        self._open_product_form(product_id)

    def _delete_product(self, product: dict) -> None:
        if db.product_in_orders(self.app.conn, product["article"]):
            helpers.show_error(
                "Ошибка",
                "Нельзя удалить товар, который присутствует в заказе.",
            )
            return
        if not helpers.ask_yes_no(
            "Подтверждение",
            f"Удалить товар «{product['name']}»?\nЭто действие необратимо.",
            parent=self,
        ):
            return
        helpers.remove_file_if_exists(product.get("photo_path"))
        db.delete_product(self.app.conn, product["id"])
        helpers.show_info("Информация", "Товар удалён.")
        self.refresh_list()

    def _open_orders(self) -> None:
        OrdersWindow(self, self.app, self.user, self.role)

    def _logout(self) -> None:
        self.destroy()
        self.app.products_window = None
        self.app.show_login()
