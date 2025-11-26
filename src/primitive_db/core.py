#!/usr/bin/env python3
"""Основная логика работы с таблицами и данными."""
from .constants import SUPPORTED_TYPES, AUTO_ID_COLUMN, ERROR_MESSAGES


def create_table(metadata, table_name, columns):
    """Создает новую таблицу."""
    # Проверяем существование таблицы
    if table_name in metadata:
        return False, ERROR_MESSAGES["table_exists"].format(table_name)
    
    # Парсим и проверяем колонки
    parsed_columns = []
    for column in columns:
        if ':' not in column:
            return False, ERROR_MESSAGES["invalid_value"].format(column)
        
        col_name, col_type = column.split(':', 1)
        if col_type not in SUPPORTED_TYPES:
            return False, ERROR_MESSAGES["invalid_type"].format(col_type)
        
        parsed_columns.append(f"{col_name}:{col_type}")
    
    # Добавляем автоматический ID в начало
    final_columns = [AUTO_ID_COLUMN] + parsed_columns
    
    # Сохраняем в метаданные
    metadata[table_name] = final_columns
    
    # Формируем сообщение об успехе
    columns_str = ", ".join(final_columns)
    success_message = f'Таблица "{table_name}" успешно создана со столбцами: {columns_str}'
    
    return True, success_message


def drop_table(metadata, table_name):
    """Удаляет таблицу."""
    if table_name not in metadata:
        return False, ERROR_MESSAGES["table_not_exists"].format(table_name)
    
    del metadata[table_name]
    return True, f'Таблица "{table_name}" успешно удалена.'


def list_tables(metadata):
    """Возвращает список всех таблиц."""
    if not metadata:
        return "Нет созданных таблиц."
    
    tables = "\n".join(f"- {table}" for table in metadata.keys())
    return tables


def validate_column_format(column):
    """Проверяет формат колонки (name:type)."""
    if ':' not in column:
        return False, None, None
    
    name, type_ = column.split(':', 1)
    return True, name.strip(), type_.strip()