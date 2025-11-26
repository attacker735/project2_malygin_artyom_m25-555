#!/usr/bin/env python3
"""Вспомогательные функции для работы с файлами."""
import json
import os

from .constants import DATA_DIR, DB_META_PATH


def load_metadata(filepath=DB_META_PATH):
    """Загружает метаданные из JSON-файла."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def save_metadata(data, filepath=DB_META_PATH):
    """Сохраняет метаданные в JSON-файл."""
    os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else '.', exist_ok=True)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_table_data(table_name):
    """Загружает данные таблицы из JSON-файла."""
    filepath = get_table_file_path(table_name)
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def save_table_data(table_name, data):
    """Сохраняет данные таблицы в JSON-файл."""
    filepath = get_table_file_path(table_name)
    os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else '.', exist_ok=True)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def ensure_data_dir():
    """Создает директорию для данных если не существует."""
    os.makedirs(DATA_DIR, exist_ok=True)


def get_table_file_path(table_name):
    """Возвращает путь к файлу таблицы."""
    return os.path.join(DATA_DIR, f"{table_name}.json")