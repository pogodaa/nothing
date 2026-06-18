"""Подключение скриптов из папки other/ к корню проекта desktop_linux."""

import os
import sys
from pathlib import Path

# Корень проекта — родитель папки other/
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SERVICE_DIR = Path(__file__).resolve().parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

if str(SERVICE_DIR) not in sys.path:
    sys.path.insert(0, str(SERVICE_DIR))

# Рабочая директория = корень проекта (важно для относительных путей)
os.chdir(PROJECT_ROOT)
