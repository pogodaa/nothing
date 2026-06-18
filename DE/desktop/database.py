"""Работа с SQLite: схема, запросы, проверки."""

import sqlite3
from datetime import datetime
from typing import Any

import config

# Кириллические буквы, похожие на латиницу (часто встречаются в xlsx импорта).
_CYRILLIC_HOMOGLYPHS = str.maketrans(
    {
        "\u0410": "A",
        "\u0430": "a",
        "\u0412": "B",
        "\u0432": "b",
        "\u0421": "C",
        "\u0441": "c",
        "\u0415": "E",
        "\u0435": "e",
        "\u041d": "H",
        "\u043d": "h",
        "\u041a": "K",
        "\u043a": "k",
        "\u041c": "M",
        "\u043c": "m",
        "\u041e": "O",
        "\u043e": "o",
        "\u0420": "P",
        "\u0440": "p",
        "\u0422": "T",
        "\u0442": "t",
        "\u0425": "X",
        "\u0445": "x",
    }
)


def normalize_article(value: str) -> str:
    """Приводит артикул к латинским буквам (А112Т4 → A112T4)."""
    return (value or "").strip().translate(_CYRILLIC_HOMOGLYPHS)


def fix_stored_articles(conn: sqlite3.Connection) -> None:
    """Исправляет артикулы, уже загруженные из xlsx с кириллицей."""
    conn.execute("PRAGMA foreign_keys = OFF")
    try:
        for row in conn.execute("SELECT id, article FROM products").fetchall():
            old = row["article"]
            new = normalize_article(old)
            if new == old:
                continue
            duplicate = conn.execute(
                "SELECT id FROM products WHERE article = ? AND id != ?",
                (new, row["id"]),
            ).fetchone()
            if duplicate:
                continue
            conn.execute(
                "UPDATE order_items SET product_article = ? WHERE product_article = ?",
                (new, old),
            )
            conn.execute(
                "UPDATE products SET article = ? WHERE id = ?",
                (new, row["id"]),
            )

        for row in conn.execute("SELECT id, articles_text FROM orders").fetchall():
            new_text = normalize_article(row["articles_text"])
            if new_text != row["articles_text"]:
                conn.execute(
                    "UPDATE orders SET articles_text = ? WHERE id = ?",
                    (new_text, row["id"]),
                )

        conn.commit()
    finally:
        conn.execute("PRAGMA foreign_keys = ON")


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL,
            full_name TEXT NOT NULL,
            login TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS pickup_points (
            id INTEGER PRIMARY KEY,
            address TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            article TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            unit TEXT,
            price REAL NOT NULL CHECK(price >= 0),
            supplier TEXT,
            manufacturer TEXT,
            category TEXT,
            discount REAL DEFAULT 0 CHECK(discount >= 0),
            quantity INTEGER DEFAULT 0 CHECK(quantity >= 0),
            description TEXT,
            photo_path TEXT
        );

        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY,
            articles_text TEXT NOT NULL,
            order_date TEXT,
            delivery_date TEXT,
            pickup_point_id INTEGER,
            client_name TEXT,
            pickup_code INTEGER,
            status TEXT,
            FOREIGN KEY (pickup_point_id) REFERENCES pickup_points(id)
        );

        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            product_article TEXT NOT NULL,
            quantity INTEGER NOT NULL CHECK(quantity > 0),
            FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
            FOREIGN KEY (product_article) REFERENCES products(article)
        );
        """
    )
    conn.commit()


def user_count(conn: sqlite3.Connection) -> int:
    row = conn.execute("SELECT COUNT(*) AS c FROM users").fetchone()
    return int(row["c"])


def authenticate(conn: sqlite3.Connection, login: str, password: str) -> dict | None:
    row = conn.execute(
        "SELECT * FROM users WHERE login = ? AND password = ?",
        (login.strip(), password),
    ).fetchone()
    return dict(row) if row else None


def role_key(role_name: str) -> str:
    role_name = (role_name or "").strip()
    if role_name == config.ROLES["admin"]:
        return "admin"
    if role_name == config.ROLES["manager"]:
        return "manager"
    if role_name == config.ROLES["client"]:
        return "client"
    return "guest"


def get_all_products(conn: sqlite3.Connection) -> list[dict]:
    rows = conn.execute(
        "SELECT * FROM products ORDER BY id"
    ).fetchall()
    return [dict(r) for r in rows]


def get_product_by_id(conn: sqlite3.Connection, product_id: int) -> dict | None:
    row = conn.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
    return dict(row) if row else None


def get_product_by_article(conn: sqlite3.Connection, article: str) -> dict | None:
    article = normalize_article(article)
    row = conn.execute(
        "SELECT * FROM products WHERE article = ?", (article,)
    ).fetchone()
    return dict(row) if row else None


def get_categories(conn: sqlite3.Connection) -> list[str]:
    rows = conn.execute(
        "SELECT DISTINCT category FROM products WHERE category IS NOT NULL ORDER BY category"
    ).fetchall()
    return [r["category"] for r in rows]


def get_suppliers(conn: sqlite3.Connection) -> list[str]:
    rows = conn.execute(
        "SELECT DISTINCT supplier FROM products WHERE supplier IS NOT NULL ORDER BY supplier"
    ).fetchall()
    return [r["supplier"] for r in rows]


def next_product_id(conn: sqlite3.Connection) -> int:
    row = conn.execute("SELECT COALESCE(MAX(id), 0) + 1 AS n FROM products").fetchone()
    return int(row["n"])


def product_in_orders(conn: sqlite3.Connection, article: str) -> bool:
    article = normalize_article(article)
    row = conn.execute(
        "SELECT 1 FROM order_items WHERE product_article = ? LIMIT 1",
        (article,),
    ).fetchone()
    return row is not None


def insert_product(conn: sqlite3.Connection, data: dict) -> None:
    data = {**data, "article": normalize_article(data["article"])}
    conn.execute(
        """
        INSERT INTO products (
            id, article, name, unit, price, supplier, manufacturer,
            category, discount, quantity, description, photo_path
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            data["id"],
            data["article"],
            data["name"],
            data["unit"],
            data["price"],
            data["supplier"],
            data["manufacturer"],
            data["category"],
            data["discount"],
            data["quantity"],
            data["description"],
            data["photo_path"],
        ),
    )
    conn.commit()


def update_product(conn: sqlite3.Connection, product_id: int, data: dict) -> None:
    data = {**data, "article": normalize_article(data["article"])}
    conn.execute(
        """
        UPDATE products SET
            article = ?, name = ?, unit = ?, price = ?, supplier = ?,
            manufacturer = ?, category = ?, discount = ?, quantity = ?,
            description = ?, photo_path = ?
        WHERE id = ?
        """,
        (
            data["article"],
            data["name"],
            data["unit"],
            data["price"],
            data["supplier"],
            data["manufacturer"],
            data["category"],
            data["discount"],
            data["quantity"],
            data["description"],
            data["photo_path"],
            product_id,
        ),
    )
    conn.commit()


def delete_product(conn: sqlite3.Connection, product_id: int) -> None:
    conn.execute("DELETE FROM products WHERE id = ?", (product_id,))
    conn.commit()


def get_all_orders(conn: sqlite3.Connection) -> list[dict]:
    rows = conn.execute(
        """
        SELECT o.*, p.address AS pickup_address
        FROM orders o
        LEFT JOIN pickup_points p ON p.id = o.pickup_point_id
        ORDER BY o.id
        """
    ).fetchall()
    return [dict(r) for r in rows]


def get_order(conn: sqlite3.Connection, order_id: int) -> dict | None:
    row = conn.execute(
        """
        SELECT o.*, p.address AS pickup_address
        FROM orders o
        LEFT JOIN pickup_points p ON p.id = o.pickup_point_id
        WHERE o.id = ?
        """,
        (order_id,),
    ).fetchone()
    return dict(row) if row else None


def get_pickup_points(conn: sqlite3.Connection) -> list[dict]:
    rows = conn.execute("SELECT * FROM pickup_points ORDER BY id").fetchall()
    return [dict(r) for r in rows]


def get_client_names(conn: sqlite3.Connection) -> list[str]:
    rows = conn.execute(
        """
        SELECT full_name AS name FROM users WHERE role = ?
        UNION
        SELECT DISTINCT client_name AS name FROM orders
        WHERE client_name IS NOT NULL AND TRIM(client_name) != ''
        ORDER BY name
        """,
        (config.ROLES["client"],),
    ).fetchall()
    return [row["name"] for row in rows]


def next_order_id(conn: sqlite3.Connection) -> int:
    row = conn.execute("SELECT COALESCE(MAX(id), 0) + 1 AS n FROM orders").fetchone()
    return int(row["n"])


def insert_order(conn: sqlite3.Connection, data: dict) -> None:
    articles_text = normalize_article(data["articles_text"])
    conn.execute(
        """
        INSERT INTO orders (
            id, articles_text, order_date, delivery_date,
            pickup_point_id, client_name, pickup_code, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            data["id"],
            articles_text,
            data["order_date"],
            data["delivery_date"],
            data["pickup_point_id"],
            data["client_name"],
            data["pickup_code"],
            data["status"],
        ),
    )
    _sync_order_items(conn, data["id"], articles_text)
    conn.commit()


def update_order(conn: sqlite3.Connection, order_id: int, data: dict) -> None:
    articles_text = normalize_article(data["articles_text"])
    conn.execute(
        """
        UPDATE orders SET
            articles_text = ?, order_date = ?, delivery_date = ?,
            pickup_point_id = ?, client_name = ?, pickup_code = ?, status = ?
        WHERE id = ?
        """,
        (
            articles_text,
            data["order_date"],
            data["delivery_date"],
            data["pickup_point_id"],
            data["client_name"],
            data["pickup_code"],
            data["status"],
            order_id,
        ),
    )
    conn.execute("DELETE FROM order_items WHERE order_id = ?", (order_id,))
    _sync_order_items(conn, order_id, articles_text)
    conn.commit()


def delete_order(conn: sqlite3.Connection, order_id: int) -> None:
    conn.execute("DELETE FROM order_items WHERE order_id = ?", (order_id,))
    conn.execute("DELETE FROM orders WHERE id = ?", (order_id,))
    conn.commit()


def _sync_order_items(conn: sqlite3.Connection, order_id: int, articles_text: str) -> None:
    for article, qty in parse_articles_text(articles_text):
        conn.execute(
            """
            INSERT INTO order_items (order_id, product_article, quantity)
            VALUES (?, ?, ?)
            """,
            (order_id, article, qty),
        )


def parse_articles_text(text: str) -> list[tuple[str, int]]:
    parts = [p.strip() for p in (text or "").split(",") if p.strip()]
    result = []
    i = 0
    while i < len(parts):
        article = normalize_article(parts[i])
        qty = 1
        if i + 1 < len(parts) and parts[i + 1].isdigit():
            qty = int(parts[i + 1])
            i += 2
        else:
            i += 1
        result.append((article, qty))
    return result


def format_date(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d")
    return str(value)[:10]


def final_price(price: float, discount: float) -> float:
    if discount and discount > 0:
        return round(price * (1 - discount / 100), 2)
    return round(price, 2)
