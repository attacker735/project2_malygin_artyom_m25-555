#!/usr/bin/env python3
"""Константы для базы данных."""

# Пути к файлам
DB_META_PATH = "db_meta.json"
DATA_DIR = "data"

# Поддерживаемые типы данных
SUPPORTED_TYPES = {"int", "str", "bool"}

# Автоматические колонки
AUTO_ID_COLUMN = "ID:int"

# Сообщения
HELP_MESSAGE = """
***База данных***

Функции:
<command> create_table <имя_таблицы> <столбец1:тип> <столбец2:тип> .. - создать таблицу
<command> list_tables - показать список всех таблиц
<command> drop_table <имя_таблицы> - удалить таблицу
<command> exit - выход из программы
<command> help - справочная информация
"""

ERROR_MESSAGES = {
    "table_exists": 'Ошибка: Таблица "{}" уже существует.',
    "table_not_exists": 'Ошибка: Таблица "{}" не существует.',
    "invalid_type": 'Некорректный тип данных: "{}". Поддерживаемые типы: int, str, bool.',
    "unknown_command": 'Функции "{}" нет. Попробуйте снова.',
    "invalid_value": 'Некорректное значение: "{}". Попробуйте снова.',
}