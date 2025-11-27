#!/usr/bin/env python3
import time
from functools import wraps


def handle_db_errors(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError:
            return False, "Ошибка: Файл данных не найден. Возможно, база данных не инициализирована."
        except KeyError as e:
            return False, f"Ошибка: Таблица или столбец {e} не найден."
        except ValueError as e:
            return False, f"Ошибка валидации: {e}"
        except Exception as e:
            return False, f"Произошла непредвиденная ошибка: {e}"
    return wrapper


def confirm_action(action_name):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            response = input(f'Вы уверены, что хотите выполнить "{action_name}"? [y/n]: ').strip().lower()
            if response != 'y':
                return False, "Операция отменена."
            return func(*args, **kwargs)
        return wrapper
    return decorator


def log_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.monotonic()
        result = func(*args, **kwargs)
        end_time = time.monotonic()
        print(f"Функция {func.__name__} выполнилась за {end_time - start_time:.3f} секунд.")
        return result
    return wrapper


def create_cacher():
    cache = {}

    def cache_result(key, value_func):
        if key in cache:
            return cache[key]
        else:
            result = value_func()
            cache[key] = result
            return result

    return cache_result