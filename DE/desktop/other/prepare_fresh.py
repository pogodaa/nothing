"""Сброс проекта к состоянию «первый запуск»."""

import shutil

import _project_root  # noqa: F401

import config


def prepare_fresh(regenerate_sql: bool = True) -> None:
    app_dir = config.APP_DIR

    if config.DB_PATH.exists():
        try:
            config.DB_PATH.unlink()
            print("Удалён:", config.DB_PATH.name)
        except PermissionError:
            print(
                "Не удалось удалить velodrive.db — закройте приложение "
                "и снова выполните: python other/prepare_fresh.py"
            )
            regenerate_sql = False

    cache = app_dir / "__pycache__"
    if cache.exists():
        shutil.rmtree(cache)
        print("Удалён: __pycache__")

    for folder_name in ("build", "dist"):
        folder = app_dir / folder_name
        if folder.exists():
            shutil.rmtree(folder)
            print("Удалена папка:", folder_name)

    for spec in app_dir.glob("*.spec"):
        spec.unlink()
        print("Удалён:", spec.name)

    if config.IMAGES_DIR.exists():
        for item in config.IMAGES_DIR.iterdir():
            if item.name == ".gitkeep":
                continue
            if item.is_file():
                item.unlink()
                print("Удалён файл:", item.relative_to(app_dir))

    if not config.IMPORT_DIR.exists():
        raise FileNotFoundError(
            f"Нет папки import: {config.IMPORT_DIR}\n"
            "Скопируйте import из материалов задания в desktop/import"
        )

    if regenerate_sql:
        from build_sql import build_sql

        build_sql()
    else:
        print("database.sql не пересоздавался")

    print()
    print("Готово. Первый запуск: python main.py")


if __name__ == "__main__":
    prepare_fresh()
