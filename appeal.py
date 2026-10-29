import os
import subprocess
import shutil

# --- НАСТРОЙКИ ---
FACTORY_DIR = os.path.expanduser("~/takcas_factory")
APPEAL_DIR = os.path.join(FACTORY_DIR, "appeal")
SUCCESS_DIR = os.path.join(FACTORY_DIR, "success")
TRASH_DIR = os.path.join(FACTORY_DIR, "trash")
MODEL = "qwen2.5-coder:3b"

def main():
    print("[APPEAL] Запуск Апелляционного суда...")
    
    if not os.path.exists(APPEAL_DIR):
        print(f"[APPEAL] Ошибка: папка appeal/ не найдена.")
        return
    
    # Берем последний файл из appeal/
    files = sorted(
        [f for f in os.listdir(APPEAL_DIR) if f.endswith(".py")],
        key=lambda x: os.path.getmtime(os.path.join(APPEAL_DIR, x))
    )
    
    if not files:
        print("[APPEAL] Папка appeal/ пуста. Нечего рассматривать.")
        return
    
    target_file = os.path.join(APPEAL_DIR, files[-1])
    print(f"[APPEAL] Рассматривается файл: {target_file}")
    
    try:
        with open(target_file, "r", encoding="utf-8") as f:
            code_text = f.read().strip()
    except Exception as e:
        print(f"[APPEAL] Ошибка при чтении файла: {e}")
        return
    
    if not code_text:
        print("[APPEAL] Файл пуст. Переношу в trash/.")
        shutil.move(target_file, os.path.join(TRASH_DIR, os.path.basename(target_file)))
        return
    
    # Промпт Судьи
    prompt = (
        "Ты — Судья. Этот код был забракован другим ИИ. "
        "Проверь его еще раз, игнорируя предыдущее мнение. "
        "Если код хороший — напиши ОПРАВДАТЬ. "
        "Если плохой — напиши ОБВИНИТЬ.\n"
        f"Код:\n{code_text}"
    )
    
    print(f"[APPEAL] Отправка запроса Судье ({MODEL})...")
    try:
        result = subprocess.run(
            ["ollama", "run", MODEL, prompt],
            capture_output=True, text=True, timeout=600
        )
    except subprocess.TimeoutExpired:
        print("[APPEAL] Ошибка: Судья не ответил за 10 минут.")
        return
    except Exception as e:
        print(f"[APPEAL] Ошибка при вызове Ollama: {e}")
        return
    
    if result.returncode != 0:
        print(f"[APPEAL] Ошибка: Ollama вернула код {result.returncode}.")
        return
    
    verdict = result.stdout.strip().upper()
    print(f"[APPEAL] Вердикт Судьи:\n{result.stdout.strip()[:300]}...")
    
    if "ОПРАВДАТЬ" in verdict:
        print("[APPEAL] Вердикт: ОПРАВДАТЬ. Переношу в success/.")
        try:
            shutil.move(target_file, os.path.join(SUCCESS_DIR, os.path.basename(target_file)))
        except Exception as e:
            print(f"[APPEAL] Ошибка при переносе в success/: {e}")
    elif "ОБВИНИТЬ" in verdict:
        print("[APPEAL] Вердикт: ОБВИНИТЬ. Переношу в trash/.")
        try:
            shutil.move(target_file, os.path.join(TRASH_DIR, os.path.basename(target_file)))
        except Exception as e:
            print(f"[APPEAL] Ошибка при переносе в trash/: {e}")
    else:
        print("[APPEAL] Неизвестный вердикт. Оставляю в appeal/.")

if __name__ == "__main__":
    main()
