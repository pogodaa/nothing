"""Форма добавления и редактирования товара (только администратор)."""

import tkinter as tk
from tkinter import filedialog, ttk

import config
import database as db
import helpers


class ProductFormWindow(tk.Toplevel):
    def __init__(self, parent, app, product_id: int | None = None):
        super().__init__(parent)
        self.app = app
        self.product_id = product_id
        self.is_edit = product_id is not None
        self.old_photo_path = None
        self.new_image_source = None
        self.photo_image = None
        self._original_snapshot = None

        app.product_form_open = self
        self.title("Редактирование товара" if self.is_edit else "Добавление товара")
        self.geometry("540x720")
        self.minsize(540, 720)
        self.resizable(True, True)
        helpers.setup_window_icon(self)
        self.protocol("WM_DELETE_WINDOW", self._close)

        self._build_ui()
        if self.is_edit:
            self._load_product()
        else:
            self._prepare_new_id()

    def _build_ui(self) -> None:
        container = tk.Frame(self)
        container.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(container, highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient=tk.VERTICAL, command=canvas.yview)
        self.form_frame = tk.Frame(canvas, padx=15, pady=15)

        self.form_frame.bind(
            "<Configure>",
            lambda _e: canvas.configure(scrollregion=canvas.bbox("all")),
        )
        self.canvas_window = canvas.create_window((0, 0), window=self.form_frame, anchor="nw")
        canvas.bind(
            "<Configure>",
            lambda e: canvas.itemconfig(self.canvas_window, width=e.width),
        )
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        helpers.bind_mousewheel(canvas, self.form_frame)

        frame = self.form_frame

        # Фиксированная область превью 300x200 (как в ТЗ)
        self.photo_frame = tk.Frame(frame, width=300, height=200, relief=tk.GROOVE, bd=1, bg="#f0f0f0")
        self.photo_frame.pack(pady=5)
        self.photo_frame.pack_propagate(False)
        self.photo_label = tk.Label(self.photo_frame, text="Фото", bg="#f0f0f0")
        self.photo_label.place(relx=0.5, rely=0.5, anchor="center")

        tk.Button(frame, text="Выбрать фото", command=self._choose_photo).pack(pady=5)

        if self.is_edit:
            tk.Label(frame, text="Идентификатор (только для чтения):").pack(anchor="w")
            self.id_var = tk.StringVar()
            ttk.Entry(frame, textvariable=self.id_var, state="readonly").pack(fill=tk.X, pady=2)

        self._add_entry(frame, "Артикул *", "article")
        self._add_entry(frame, "Наименование *", "name")
        self._add_combo(frame, "Категория", "category", db.get_categories(self.app.conn))
        self.description_text = self._add_text(frame, "Описание")
        self._add_entry(frame, "Производитель", "manufacturer")
        self._add_combo(frame, "Поставщик", "supplier", db.get_suppliers(self.app.conn))
        self._add_entry(frame, "Цена *", "price")
        self._add_combo(
            frame,
            "Единица измерения",
            "unit",
            config.PRODUCT_UNITS,
            state="readonly",
        )
        self._add_entry(frame, "Количество на складе *", "quantity")
        self._add_entry(frame, "Действующая скидка (%)", "discount")

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

    def _add_entry(self, parent, label, attr):
        tk.Label(parent, text=label).pack(anchor="w")
        var = tk.StringVar()
        setattr(self, f"{attr}_var", var)
        entry = ttk.Entry(parent, textvariable=var)
        entry.pack(fill=tk.X, pady=4, ipady=3)

    def _add_combo(self, parent, label, attr, values, state=""):
        tk.Label(parent, text=label).pack(anchor="w")
        var = tk.StringVar()
        setattr(self, f"{attr}_var", var)
        combo = ttk.Combobox(parent, textvariable=var, values=values, state=state)
        combo.pack(fill=tk.X, pady=4, ipady=3)

    def _add_text(self, parent, label):
        tk.Label(parent, text=label).pack(anchor="w")
        text = tk.Text(parent, height=3)
        text.pack(fill=tk.X, pady=4)
        return text

    def _prepare_new_id(self) -> None:
        self.new_id = db.next_product_id(self.app.conn)
        self.unit_var.set(config.PRODUCT_UNITS[0])

    def _load_product(self) -> None:
        product = db.get_product_by_id(self.app.conn, self.product_id)
        if not product:
            helpers.show_error("Ошибка", "Товар не найден.")
            self._close()
            return
        self.id_var.set(str(product["id"]))
        self.article_var.set(product["article"])
        self.name_var.set(product["name"])
        self.category_var.set(product["category"] or "")
        self.description_text.insert("1.0", product["description"] or "")
        self.manufacturer_var.set(product["manufacturer"] or "")
        self.supplier_var.set(product["supplier"] or "")
        self.price_var.set(str(product["price"]))
        unit = product["unit"] or ""
        if unit not in config.PRODUCT_UNITS:
            unit = config.PRODUCT_UNITS[0]
        self.unit_var.set(unit)
        self.quantity_var.set(str(product["quantity"]))
        self.discount_var.set(str(product["discount"]))
        self.old_photo_path = product["photo_path"]
        self._show_photo(product["photo_path"])
        self._original_snapshot = self._form_snapshot()

    def _form_snapshot(self) -> dict:
        return {
            "article": self.article_var.get().strip(),
            "name": self.name_var.get().strip(),
            "category": self.category_var.get().strip(),
            "description": self.description_text.get("1.0", tk.END).strip(),
            "manufacturer": self.manufacturer_var.get().strip(),
            "supplier": self.supplier_var.get().strip(),
            "price": self.price_var.get().strip(),
            "unit": self.unit_var.get().strip(),
            "quantity": self.quantity_var.get().strip(),
            "discount": self.discount_var.get().strip(),
            "new_image": self.new_image_source,
        }

    def _has_unsaved_changes(self) -> bool:
        if not self.is_edit or self._original_snapshot is None:
            return False
        return self._form_snapshot() != self._original_snapshot

    def _show_photo(self, path: str) -> None:
        for child in self.photo_frame.winfo_children():
            child.destroy()
        self.photo_image = helpers.load_photo(path, 280, 180)
        if self.photo_image:
            self.photo_label = tk.Label(self.photo_frame, image=self.photo_image, bg="#f0f0f0")
        else:
            self.photo_label = tk.Label(self.photo_frame, text="Фото", bg="#f0f0f0")
        self.photo_label.place(relx=0.5, rely=0.5, anchor="center")

    def _choose_photo(self) -> None:
        path = filedialog.askopenfilename(
            title="Выберите изображение",
            filetypes=[("Изображения", "*.jpg *.jpeg *.png *.JPG *.PNG")],
        )
        if path:
            self.new_image_source = path
            self._show_photo(path)

    def _validate(self) -> dict | None:
        article = self.article_var.get().strip()
        name = self.name_var.get().strip()
        if not article or not name:
            helpers.show_error("Ошибка", "Артикул и наименование обязательны.")
            return None
        try:
            price = float(self.price_var.get().replace(",", "."))
            quantity = int(self.quantity_var.get())
            discount = float(self.discount_var.get().replace(",", ".") or 0)
        except ValueError:
            helpers.show_error(
                "Ошибка",
                "Цена, количество и скидка должны быть числами.",
            )
            return None
        if price < 0 or quantity < 0 or discount < 0:
            helpers.show_error("Ошибка", "Цена, количество и скидка не могут быть отрицательными.")
            return None
        if discount > 100:
            helpers.show_error("Ошибка", "Скидка не может быть больше 100%.")
            return None

        unit = self.unit_var.get().strip()
        if unit not in config.PRODUCT_UNITS:
            helpers.show_error(
                "Ошибка",
                f"Выберите единицу измерения из списка: {', '.join(config.PRODUCT_UNITS)}.",
            )
            return None

        photo_path = self.old_photo_path or config.PICTURE_PLACEHOLDER.relative_to(
            config.APP_DIR
        ).as_posix()
        if self.new_image_source:
            if self.is_edit:
                helpers.remove_file_if_exists(self.old_photo_path)
            photo_path = helpers.save_product_image(self.new_image_source, article)

        return {
            "id": self.product_id if self.is_edit else self.new_id,
            "article": article,
            "name": name,
            "unit": unit,
            "price": price,
            "supplier": self.supplier_var.get().strip(),
            "manufacturer": self.manufacturer_var.get().strip(),
            "category": self.category_var.get().strip(),
            "discount": discount,
            "quantity": quantity,
            "description": self.description_text.get("1.0", tk.END).strip(),
            "photo_path": photo_path,
        }

    def _save(self) -> None:
        data = self._validate()
        if not data:
            return

        if self.is_edit:
            if not self._has_unsaved_changes():
                helpers.show_info("Информация", "Изменений нет.")
                return
            if not helpers.ask_yes_no(
                "Подтверждение",
                "Сохранить изменения товара в базе данных?",
                parent=self,
            ):
                return

        try:
            if self.is_edit:
                db.update_product(self.app.conn, self.product_id, data)
            else:
                existing = db.get_product_by_article(self.app.conn, data["article"])
                if existing:
                    helpers.show_error("Ошибка", "Товар с таким артикулом уже существует.")
                    return
                db.insert_product(self.app.conn, data)
            helpers.show_info("Информация", "Товар успешно сохранён.")
            self._close()
            if self.app.products_window:
                self.app.products_window.refresh_list()
        except Exception as exc:
            helpers.show_error("Ошибка", "Не удалось сохранить товар.\nПроверьте введённые данные.")

    def _close(self) -> None:
        if self._has_unsaved_changes():
            if not helpers.ask_yes_no(
                "Подтверждение",
                "Есть несохранённые изменения.\nЗакрыть форму без сохранения?",
                parent=self,
            ):
                return
        self.app.product_form_open = None
        self.destroy()
