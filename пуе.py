import os
from pathlib import Path

# Функция для отображения структуры папок
def print_directory_structure(startpath, exclude_dirs=None):
    if exclude_dirs is None:
        exclude_dirs = set()

    for root, dirs, files in os.walk(startpath, topdown=True):
        # Исключаем ненужные директории
        dirs[:] = [d for d in dirs if d not in exclude_dirs]

        # Вычисляем уровень вложенности
        level = root.replace(startpath, '').count(os.sep)
        indent = ' ' * 4 * level
        print(f"{indent}{os.path.basename(root)}/")

        # Выводим файлы
        subindent = ' ' * 4 * (level + 1)
        for file in files:
            print(f"{subindent}{file}")

# Указываем директорию проекта
project_path = Path(__file__).parent  # Текущая директория скрипта или укажите путь вручную

# Директории, которые нужно исключить
exclude_dirs = {
    '__pycache__',  # Кэш Python
    '.git',         # Git-репозиторий
    '.venv',        # Виртуальное окружение
    'venv',         # Виртуальное окружение
    'env',          # Виртуальное окружение
    'node_modules', # Node.js модули (если есть)
    '.idea',        # Директория IDE (например, PyCharm)
    '.vscode',      # Директория VS Code
    '.py~'
}

# Выводим структуру папок
print_directory_structure(r'C:\temp\python\confyBot', exclude_dirs)
# Укажите путь к корневой директории вашего проекта
# project_path = r'C:\temp\python\confyBot'
# print_directory_structure(project_path)