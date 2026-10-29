import datetime

# Создание файла 'server.log' и запись в него 10 строк лога
with open('server.log', 'w') as log_file:
    for i in range(10):
        log_file.write(f"{datetime.datetime(2026, 10, 25, 14, i)} [INFO] Us[2D[K
User logged in\n")
        log_file.write(f"{datetime.datetime(2026, 10, 25, 14, i)} [ERROR] D[1D[K
Database connection failed\n")
        log_file.write(f"{datetime.datetime(2026, 10, 25, 14, i)} [WARNING][9D[K
[WARNING] Disk space is low\n")

# Чтение файла и распарсинг строк
error_count = 0
warning_count = 0

try:
    with open('server.log', 'r') as log_file:
        for line in log_file:
            try:
                timestamp, _, level, message = line.split()
                if level == 'ERROR':
                    error_count += 1
                elif level == 'WARNING':
                    warning_count += 1
            except ValueError:
                continue

except FileNotFoundError:
    print("Error: File not found")

# Вывод результата
print(f"ERROR: {error_count}, WARNING: {warning_count}")