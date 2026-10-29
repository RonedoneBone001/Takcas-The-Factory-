import os
import random

# Создание папки 'backup_test'
if not os.path.exists('backup_test'):
    os.makedirs('backup_test')

# Запись случайных чисел в 5 текстовых файлов
for i in range(1, 6):
    with open(f'backup_test/file_{i}.txt', 'w') as file:
        file.write(str(random.randint(1, 100)))

# Чтение всех чисел из файлов и вычисление суммы
total_sum = 0
for i in range(1, 6):
    with open(f'backup_test/file_{i}.txt', 'r') as file:
        total_sum += int(file.read())

# Запись суммы в новый файл 'total_sum.txt'
with open('backup_test/total_sum.txt', 'w') as file:
    file.write(str(total_sum))