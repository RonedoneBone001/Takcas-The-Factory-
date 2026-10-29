import os
import random

def create_folder_and_files():
    # Создаем папку 'secure_data'
    if not os.path.exists('secure_data'):
        os.makedirs('secure_data')

    # Создаем 5 файлов 'data_1.txt' - 'data_5.txt' и записываем случайные ч[1D[K
числа от 1 до 100
    for i in range(1, 6):
        file_path = os.path.join('secure_data', f'data_{i}.txt')
        with open(file_path, 'w') as f:
            f.write(str(random.randint(1, 100)))

def calculate_sum_and_create_result():
    total_sum = 0
    found_files = 0

    # Читаем все файлы из папки 'secure_data'
    for i in range(1, 6):
        file_path = os.path.join('secure_data', f'data_{i}.txt')
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                try:
                    total_sum += int(f.read().strip())
                    found_files += 1
                except ValueError:
                    print(f"Пропускаем поврежденный файл: {file_path}")
        else:
            print(f"Пропускаем отсутствующий файл: {file_path}")

    # Создаем файл 'result.txt' с соответствующим сообщением
    if found_files == 5:
        with open('result.txt', 'w') as f:
            if total_sum > 250:
                f.write('HIGH')
            else:
                f.write('LOW')

# Вызываем функции
create_folder_and_files()
calculate_sum_and_create_result()