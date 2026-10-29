import os
import time

# Проверяем, существует ли файл report.txt
if not os.path.exists('report.txt'):
    # Если файла не существует, создаем его
    with open('report.txt', 'w') as file:
        # Записываем текущую дату и время
        file.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')}\n")