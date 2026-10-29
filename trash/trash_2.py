import os
import subprocess
import time

# Создание файла и запись текущей даты и времени
with open('report.txt', 'w') as f:
    f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')}")

print("Файл report.txt создан и заполнен.")