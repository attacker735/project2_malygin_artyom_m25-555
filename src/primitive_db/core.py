#!/usr/bin/env python3
"""Основная логика работы с таблицами и данными."""
from prettytable import PrettyTable
from .constants import SUPPORTED_TYPES, AUTO_ID_COLUMN, ERROR_MESSAGES


def create_table(metadata, table_name, columns):
    """Создает новую таблицу."""
    if table_name in metadata:
        return False, ERROR_MESSAGES["table_exists"].format(table_name)
    
    parsed_columns = []
    for column in columns:
        if ':' not in column:
            return False, ERROR_MESSAGES["invalid_value"].format(column)
        
        col_name, col_type = column.split(':', 1)
        if col_type not in SUPPORTED_TYPES:
            return False, ERROR_MESSAGES["invalid_type"].format(col_type)
        
        parsed_columns.append(f"{col_name}:{col_type}")
    
    final_columns = [AUTO_ID_COLUMN] + parsed_columns
    metadata[table_name] = final_columns
    
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


def get_columns_without_id(metadata, table_name):
    """Возвращает список колонок без ID."""
    if table_name not in metadata:
        return []
    return [col for col in metadata[table_name] if not col.startswith("ID:")]


def validate_data_types(columns, values):
    """Проверяет соответствие типов данных."""
    for col, val in zip(columns, values):
        col_name, col_type = col.split(':')
        
        if col_type == 'int' and not isinstance(val, int):
            return False, f'Ожидается int для столбца {col_name}, получено {type(val).__name__}'
        elif col_type == 'bool' and not isinstance(val, bool):
            return False, f'Ожидается bool для столбца {col_name}, получено {type(val).__name__}'
        elif col_type == 'str' and not isinstance(val, str):
            return False, f'Ожидается str для столбца {col_name}, получено {type(val).__name__}'
    
    return True, None


def insert(metadata, table_name, values):
    """Добавляет новую запись в таблицу."""
    if table_name not in metadata:
        return False, ERROR_MESSAGES["table_not_exists"].format(table_name)
    
    columns_without_id = get_columns_without_id(metadata, table_name)
    
    if len(values) != len(columns_without_id):
        return False, ERROR_MESSAGES["invalid_insert"]
    
    # Проверяем типы данных
    is_valid, error_msg = validate_data_types(columns_without_id, values)
    if not is_valid:
        return False, error_msg
    
    return True, "Запись успешно добавлена"


def select(metadata, table_data, where_clause=None):
    """Выбирает записи из таблицы."""
    if not table_data:
        return ERROR_MESSAGES["no_records"]
    
    # Фильтруем данные если есть условие WHERE
    filtered_data = table_data
    if where_clause:
        filtered_data = []
        for record in table_data:
            match = True
            for col, val in where_clause.items():
                if record.get(col) != val:
                    match = False
                    break
            if match:
                filtered_data.append(record)
    
    if not filtered_data:
        return ERROR_MESSAGES["no_records"]
    
    # Создаем красивую таблицу для вывода
    table = PrettyTable()
    if metadata:
        table_name = list(metadata.keys())[0]
        table.field_names = [col.split(':')[0] for col in metadata[table_name]]
    
    for record in filtered_data:
        row = [record.get(col.split(':')[0], '') for col in metadata[table_name]]
        table.add_row(row)
    
    return table


def update(table_data, set_clause, where_clause):
    """Обновляет записи в таблице."""
    updated_count = 0
    
    for record in table_data:
        match = True
        # Проверяем условие WHERE
        if where_clause:
            for col, val in where_clause.items():
                if record.get(col) != val:
                    match = False
                    break
        
        if match:
            # Обновляем поля согласно SET
            for col, val in set_clause.items():
                record[col] = val
            updated_count += 1
    
    return table_data, updated_count


def delete(table_data, where_clause):
    """Удаляет записи из таблицы."""
    if not where_clause:
        return [], len(table_data)
    
    remaining_data = []
    deleted_count = 0
    
    for record in table_data:
        match = True
        for col, val in where_clause.items():
            if record.get(col) != val:
                match = False
                break
        
        if match:
            deleted_count += 1
        else:
            remaining_data.append(record)
    
    return remaining_data, deleted_count


def get_table_info(metadata, table_name, table_data):
    """Возвращает информацию о таблице."""
    if table_name not in metadata:
        return ERROR_MESSAGES["table_not_exists"].format(table_name)
    
    columns_str = ", ".join(metadata[table_name])
    record_count = len(table_data)
    
    return f"""Таблица: {table_name}
Столбцы: {columns_str}
Количество записей: {record_count}"""