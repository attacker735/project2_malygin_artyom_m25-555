#!/usr/bin/env python3
"""Движок базы данных - основной цикл и парсинг команд."""
import shlex

from .constants import CRUD_HELP_MESSAGE, ERROR_MESSAGES
from .core import (
    create_table,
    delete,
    drop_table,
    get_table_info,
    insert,
    list_tables,
    select,
    update,
)
from .parser import (
    get_expected_types,
    parse_insert_values,
    parse_set_clause,
    parse_where_condition,
)
from .utils import (
    ensure_data_dir,
    load_metadata,
    load_table_data,
    save_metadata,
    save_table_data,
)


def print_help():
    """Prints the help message for the current mode."""
    print(CRUD_HELP_MESSAGE)


def run():
    """Основной цикл программы."""
    ensure_data_dir()
    print_help()
    
    while True:
        try:
            user_input = input("Введите команду: ").strip()
            if not user_input:
                continue
                
            parts = shlex.split(user_input)
            command = parts[0].lower()
            args = parts[1:]
            
            metadata = load_metadata()
            
            if command == "exit":
                print("Выход из программы.")
                break
                
            elif command == "help":
                print_help()
                
            elif command == "create_table":
                if len(args) < 2:
                    print("Ошибка: Недостаточно аргументов. Используйте: create_table <имя> <столбец1:тип> ...")
                    continue
                
                table_name = args[0]
                columns = args[1:]
                
                success, message = create_table(metadata, table_name, columns)
                print(message)
                if success:
                    save_metadata(metadata)
                    
            elif command == "drop_table":
                if len(args) != 1:
                    print("Ошибка: Неверное количество аргументов. Используйте: drop_table <имя_таблицы>")
                    continue
                
                table_name = args[0]
                success, message = drop_table(metadata, table_name)
                print(message)
                if success:
                    save_metadata(metadata)
                    
            elif command == "list_tables":
                result = list_tables(metadata)
                print(result)
                
            elif command == "insert":
                if len(args) < 4 or args[0].lower() != "into" or args[2].lower() != "values":
                    print("Ошибка: Неверный формат команды. Используйте: insert into <таблица> values (<значения>)")
                    continue
                
                table_name = args[1]
                values_str = " ".join(args[3:])
                
                try:
                    expected_types = get_expected_types(metadata, table_name)
                    values = parse_insert_values(values_str, expected_types)
                    
                    table_data = load_table_data(table_name)
                    success, message = insert(metadata, table_name, values)
                    
                    if success:
                        new_id = len(table_data) + 1
                        columns_without_id = [col.split(':')[0] for col in metadata[table_name] if not col.startswith("ID:")]
                        
                        new_record = {"ID": new_id}
                        for col, val in zip(columns_without_id, values):
                            new_record[col] = val
                        
                        table_data.append(new_record)
                        save_table_data(table_name, table_data)
                        print(f'Запись с ID={new_id} успешно добавлена в таблицу "{table_name}".')
                    else:
                        print(message)
                        
                except Exception as e:
                    print(f"Ошибка: {e}")
                    
            elif command == "select":
                if len(args) < 2 or args[0].lower() != "from":
                    print("Ошибка: Неверный формат команды. Используйте: select from <таблица> [where условие]")
                    continue
                
                table_name = args[1]
                where_condition = None
                
                if len(args) > 3 and args[2].lower() == "where":
                    where_str = " ".join(args[3:])
                    try:
                        where_condition = parse_where_condition(where_str)
                    except Exception as e:
                        print(f"Ошибка: {e}")
                        continue
                
                if table_name not in metadata:
                    print(ERROR_MESSAGES["table_not_exists"].format(table_name))
                    continue
                
                table_data = load_table_data(table_name)
                result = select(metadata, table_data, where_condition)
                print(result)
                
            elif command == "update":
                if len(args) < 6:
                    print("Ошибка: Неверный формат команды. Используйте: update <таблица> set <столбец=значение> where <условие>")
                    continue
                
                try:
                    set_index = args.index("set")
                    where_index = args.index("where")
                except ValueError:
                    print("Ошибка: Неверный формат команды. Используйте: update <таблица> set <столбец=значение> where <условие>")
                    continue
                
                table_name = args[0]
                set_str = " ".join(args[set_index+1:where_index])
                where_str = " ".join(args[where_index+1:])
                
                try:
                    set_clause = parse_set_clause(set_str)
                    where_condition = parse_where_condition(where_str)
                    
                    table_data = load_table_data(table_name)
                    updated_data, updated_count = update(table_data, set_clause, where_condition)
                    
                    if updated_count > 0:
                        save_table_data(table_name, updated_data)
                        print(f'Обновлено {updated_count} записей в таблице "{table_name}".')
                    else:
                        print("Записи для обновления не найдены.")
                        
                except Exception as e:
                    print(f"Ошибка: {e}")
                    
            elif command == "delete":
                if len(args) < 4 or args[0].lower() != "from":
                    print("Ошибка: Неверный формат команды. Используйте: delete from <таблица> where <условие>")
                    continue
                
                table_name = args[1]
                
                try:
                    where_index = args.index("where")
                    where_str = " ".join(args[where_index+1:])
                except ValueError:
                    print("Ошибка: Неверный формат команды. Используйте: delete from <таблица> where <условие>")
                    continue
                
                try:
                    where_condition = parse_where_condition(where_str)
                    table_data = load_table_data(table_name)
                    updated_data, deleted_count = delete(table_data, where_condition)
                    
                    if deleted_count > 0:
                        save_table_data(table_name, updated_data)
                        print(f'Удалено {deleted_count} записей из таблицы "{table_name}".')
                    else:
                        print("Записи для удаления не найдены.")
                        
                except Exception as e:
                    print(f"Ошибка: {e}")
                    
            elif command == "info":
                if len(args) != 1:
                    print("Ошибка: Неверное количество аргументов. Используйте: info <имя_таблицы>")
                    continue
                
                table_name = args[0]
                table_data = load_table_data(table_name)
                result = get_table_info(metadata, table_name, table_data)
                print(result)
                
            else:
                print(ERROR_MESSAGES["unknown_command"].format(command))
                
        except KeyboardInterrupt:
            print("\nВыход из программы.")
            break
        except Exception as e:
            print(f"Произошла ошибка: {e}")