"""Создаёт database.sql в корне desktop из import-данных."""

import sqlite3

import _project_root  # noqa: F401

import config
import database as db
import import_data


def build_sql() -> None:
    if config.DB_PATH.exists():
        config.DB_PATH.unlink()

    conn = db.get_connection()
    import_data.import_all(conn)
    conn.close()

    source = sqlite3.connect(config.DB_PATH)
    lines = ["PRAGMA foreign_keys = OFF;", "BEGIN TRANSACTION;"]
    for line in source.iterdump():
        if line.startswith("BEGIN TRANSACTION") or line.startswith("COMMIT"):
            continue
        lines.append(line)
    lines.append("COMMIT;")
    lines.append("PRAGMA foreign_keys = ON;")
    with config.SQL_SCRIPT_PATH.open("w", encoding="utf-8") as file:
        file.write("\n".join(lines))
        file.write("\n")
    source.close()

    print("Готово:", config.SQL_SCRIPT_PATH)


if __name__ == "__main__":
    build_sql()
