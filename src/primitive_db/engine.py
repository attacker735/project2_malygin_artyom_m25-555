#!/usr/bin/env python3
import prompt


def welcome():
    """Функция приветствия и основного цикла"""
    print("***")
    print("<command> exit - выйти из программы")
    print("<command> help - справочная информация")
    
    while True:
        command = prompt.string("Введите команду: ").strip().lower()
        
        if command == "exit":
            print("Выход из программы.")
            break
        elif command == "help":
            print("<command> exit - выйти из программы")
            print("<command> help - справочная информация")
        else:
            print(f"Неизвестная команда: {command}")


if __name__ == "__main__":
    welcome()