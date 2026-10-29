import os
import subprocess
import sys

# --- НАСТРОЙКИ ---
FACTORY_DIR = os.path.expanduser("~/takcas_factory")
SUCCESS_DIR = os.path.join(FACTORY_DIR, "success")
TASK_FILE = os.path.join(FACTORY_DIR, "task.txt")
DIRECTOR_SCRIPT = os.path.join(FACTORY_DIR, "director.py")
MODEL = "qwen2.5:1.5b"

def get_success_tasks():
    """Читает список файлов в success/ (чтобы не повторяться)."""
    if not os.path.exists(SUCCESS_DIR):
        return []
    try:
        files = [f for f in os.listdir(SUCCESS_DIR) if f.endswith(".py")]
        return files
    except Exception as e:
        print(f"[IDEALIST] Ошибка при чтении success/: {e}")
        return []

def generate_idea(done_tasks):
    """Генерирует идею через Ollama. Возвращает текст задачи или None."""
    done_text = "\n".join(done_tasks) if done_tasks else "(пока ничего нет)"
    
    prompt = (
        "Ты — генератор идей для Python-скриптов. "
        "Придумай ОДНУ ОЧЕНЬ ПРОСТУЮ задачу для Python-скрипта, которую можно решить за 1 минуту. "
        "Используй только стандартные библиотеки (os, time, datetime, random, math). "
        "Пример хорошей задачи: 'Напиши скрипт, который создает файл report.txt и записывает туда текущую дату и время'. "
        "Пример хорошей задачи: 'Напиши скрипт, который генерирует 5 случайных чисел и выводит их на экран'. "
        "Вот список уже сделанных задач (не повторяй их):\n"
        f"{done_text}\n"
        "Напиши ТОЛЬКО текст задачи в одну строчку. Без объяснений, без списков, без 'потребуется 5 минут'."
    )
    
    print(f"[IDEALIST] Отправка запроса в Ollama ({MODEL})...")
    try:
        result = subprocess.run(
            ["ollama", "run", MODEL, prompt],
            capture_output=True,
            text=True,
            timeout=300
        )
    except subprocess.TimeoutExpired:
        print("[IDEALIST] Ошибка: Ollama не ответила за 5 минут.")
        return None
    except Exception as e:
        print(f"[IDEALIST] Ошибка при вызове Ollama: {e}")
        return None
    
    if result.returncode != 0:
        print(f"[IDEALIST] Ошибка: Ollama вернула код {result.returncode}.")
        return None
    
    idea = result.stdout.strip()
    if not idea:
        print("[IDEALIST] Ошибка: Ollama вернула пустой ответ.")
        return None
    
    # ВЫГРУЖАЕМ МОДЕЛЬ, ЧТОБЫ ОСВОБОДИТЬ ПАМЯТЬ
    subprocess.run(["ollama", "stop", MODEL], capture_output=True)
    print(f"[IDEALIST] Модель {MODEL} выгружена из памяти.")
    
    return idea

def main():
    print("[IDEALIST] Запуск Отдела Идеалистов...")
    
    if not os.path.exists(FACTORY_DIR):
        print(f"[IDEALIST] Ошибка: папка фабрики не найдена: {FACTORY_DIR}")
        return
    
    done_tasks = get_success_tasks()
    print(f"[IDEALIST] Уже сделано задач: {len(done_tasks)}")
    
    idea = generate_idea(done_tasks)
    if not idea:
        print("[IDEALIST] Не удалось сгенерировать идею. Остановка.")
        return
    
    print(f"\n[IDEALIST] Придумана задача:\n{idea}\n")
    
    try:
        with open(TASK_FILE, "w", encoding="utf-8") as f:
            f.write(idea)
        print(f"[IDEALIST] Задача записана в task.txt")
    except Exception as e:
        print(f"[IDEALIST] Ошибка при записи task.txt: {e}")
        return
    
    print("[IDEALIST] Запуск director.py...")
    try:
        result = subprocess.run(
            [sys.executable, DIRECTOR_SCRIPT],
            cwd=FACTORY_DIR,
            timeout=3600
        )
        if result.returncode != 0:
            print(f"[IDEALIST] Ошибка: director.py завершился с кодом {result.returncode}.")
        else:
            print("[IDEALIST] director.py успешно завершил работу.")
    except subprocess.TimeoutExpired:
        print("[IDEALIST] Ошибка: director.py не ответил за 1 час.")
    except Exception as e:
        print(f"[IDEALIST] Ошибка при запуске director.py: {e}")

if __name__ == "__main__":
    main()
