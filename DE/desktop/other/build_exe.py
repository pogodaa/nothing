"""Сборка VeloDrive.exe (Модуль 4). pip install pyinstaller"""

import subprocess
import sys

import _project_root  # noqa: F401

import config


def build_exe() -> None:
    try:
        import PyInstaller  # noqa: F401
    except ImportError:
        print("Установите PyInstaller: pip install pyinstaller")
        sys.exit(1)

    app_dir = config.APP_DIR
    icon = config.ICON_PATH if config.ICON_PATH.exists() else None
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--onefile",
        "--windowed",
        "--name",
        "VeloDrive",
        "--distpath",
        str(app_dir / "dist"),
        "--workpath",
        str(app_dir / "build"),
        "--specpath",
        str(app_dir),
    ]
    if icon:
        cmd.extend(["--icon", str(icon)])
    cmd.append(str(app_dir / "main.py"))

    subprocess.run(cmd, check=True, cwd=app_dir)
    print("Готово:", app_dir / "dist" / "VeloDrive.exe")
    print("Рядом с exe: папки import, images и velodrive.db")


if __name__ == "__main__":
    build_exe()
