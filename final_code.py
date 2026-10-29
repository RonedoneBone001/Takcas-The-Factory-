import subprocess

def toggle_torch():
    try:
        subprocess.run(["termux-torch"], check=True)
    except subprocess.CalledProcessError:
        subprocess.run(["termux-torch", "off"], check=True)

# Пример использования функции
toggle_torch()