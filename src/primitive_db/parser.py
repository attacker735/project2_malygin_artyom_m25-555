#!/usr/bin/env python3
"""Парсер для условий WHERE и SET."""
import re
import shlex


def parse_where_condition(condition_str):
    """Парсит условие WHERE в формате 'column = value'."""
    if not condition_str:
        return None
    
    try:
        # Разбиваем на части, учитывая кавычки
        parts = shlex.split(condition_str)
        if len(parts) != 3 or parts[1] != '=':
            raise ValueError("Некорректный формат условия WHERE")
        
        column = parts[0]
        # Нормализуем имя столбца (ID всегда в верхнем регистре)
        if column.lower() == 'id':
            column = 'ID'
            
        value = parse_value(parts[2])
        return {column: value}
    except Exception as e:
        raise ValueError(f'Некорректное условие WHERE: "{condition_str}"') from e


def parse_set_clause(set_str):
    """Парсит условие SET в формате 'column = value'."""
    try:
        # Разбиваем на части, учитывая кавычки
        parts = shlex.split(set_str)
        if len(parts) != 3 or parts[1] != '=':
            raise ValueError("Некорректный формат условия SET")
        
        column = parts[0]
        # Нормализуем имя столбца (ID всегда в верхнем регистре)
        if column.lower() == 'id':
            column = 'ID'
            
        value = parse_value(parts[2])
        return {column: value}
    except Exception as e:
        raise ValueError(f'Некорректное условие SET: "{set_str}"') from e


def parse_value(value_str):
    """Парсит значение с учетом типа."""
    # Булевы значения
    if value_str.lower() == 'true':
        return True
    elif value_str.lower() == 'false':
        return False
    
    # Числа
    try:
        return int(value_str)
    except ValueError:
        pass
    
    # Строки (убираем кавычки если есть)
    if (value_str.startswith('"') and value_str.endswith('"')) or \
       (value_str.startswith("'") and value_str.endswith("'")):
        return value_str[1:-1]
    
    # Если дошли сюда, это строка без кавычек
    return value_str


def parse_insert_values(values_str, expected_types):
    """Парсит значения для INSERT в формате '(value1, value2, ...)' с учетом ожидаемых типов."""
    if not values_str.startswith('(') or not values_str.endswith(')'):
        raise ValueError("Значения должны быть в скобках")
    
    # Убираем скобки
    content = values_str[1:-1].strip()
    if not content:
        return []
    
    # Используем регулярное выражение для разбивки с учетом кавычек
    pattern = r',\s*(?=(?:[^"]*"[^"]*")*[^"]*$)'
    raw_values = re.split(pattern, content)
    
    # Убираем пробелы вокруг значений
    raw_values = [val.strip() for val in raw_values if val.strip()]
    
    if len(raw_values) != len(expected_types):
        raise ValueError(f"Ожидается {len(expected_types)} значений, получено {len(raw_values)}")
    
    # Преобразуем значения к ожидаемым типам
    converted_values = []
    for i, (raw_val, expected_type) in enumerate(zip(raw_values, expected_types)):
        try:
            if expected_type == 'int':
                # Пробуем преобразовать в int
                converted_values.append(int(raw_val))
            elif expected_type == 'bool':
                # Булевы значения
                if raw_val.lower() == 'true':
                    converted_values.append(True)
                elif raw_val.lower() == 'false':
                    converted_values.append(False)
                else:
                    raise ValueError(f"Некорректное булево значение: {raw_val}")
            else:  # str
                # Строки - убираем кавычки если есть
                if (raw_val.startswith('"') and raw_val.endswith('"')) or \
                   (raw_val.startswith("'") and raw_val.endswith("'")):
                    converted_values.append(raw_val[1:-1])
                else:
                    converted_values.append(raw_val)
        except (ValueError, TypeError) as e:
            raise ValueError(f'Не удалось преобразовать значение "{raw_val}" к типу {expected_type}') from e
    
    return converted_values


def get_expected_types(metadata, table_name):
    """Возвращает ожидаемые типы для столбцов таблицы (без ID)."""
    if table_name not in metadata:
        return []
    
    types = []
    for column in metadata[table_name]:
        if not column.startswith("ID:"):
            _, col_type = column.split(':')
            types.append(col_type)
    return types