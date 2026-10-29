import os
import subprocess
import re

# --- НАСТРОЙКИ ---
FACTORY_DIR = os.path.expanduser("~/takcas_factory")
DRAFT_1 = os.path.join(FACTORY_DIR, "draft_1.py")
DRAFT_2 = os.path.join(FACTORY_DIR, "draft_2.py")
DRAFT_3 = os.path.join(FACTORY_DIR, "draft_3.py")
DRAFT_FINAL = os.path.join(FACTORY_DIR, "draft_final.py")
ANALYSIS_FILE = os.path.join(FACTORY_DIR, "analysis.txt")
MODEL = "qwen2.5-coder:3b"

def clean_code(text):
    """Очищает ответ модели от маркдауна."""
    match = re.search(r'```(?:python)?\s*(.*?)```', text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text.strip()

def read_file(filepath):
    """Читает файл, если он существует."""
    if not os.path.exists(filepath):
        return None
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read().strip()
        return content if content else None
    except Exception as e:
        print(f"[SYNTH] Ошибка при чтении {filepath}: {e}")
        return None

def main():
    print("[SYNTH] Запуск Верховного Синтезатора...")
    
    # 1. Читаем analysis.txt
    analysis_text = read_file(ANALYSIS_FILE)
    if not analysis_text:
        print("[SYNTH] Ошибка: analysis.txt не найден или пуст. Использую draft_1.py.")
        analysis_text = "1 | ОШИБОК НЕТ"
    
    print(f"[SYNTH] Анализ: {analysis_text[:200]}...")
    
    # 2. Парсим номер драфта из analysis.txt
    match = re.search(r'(\d)', analysis_text)
    if match:
        draft_number = match.group(1)
    else:
        draft_number = "1"
    
    print(f"[SYNTH] Выбран драфт №{draft_number}")
    
    # 3. Читаем ВЫБРАННЫЙ драфт
    draft_map = {"1": DRAFT_1, "2": DRAFT_2, "3": DRAFT_3}
    selected_draft_path = draft_map.get(draft_number, DRAFT_1)
    draft_content = read_file(selected_draft_path)
    
    if not draft_content:
        print(f"[SYNTH] Ошибка: выбранный драфт {selected_draft_path} пуст. Пробую draft_1.py.")
        draft_content = read_file(DRAFT_1)
    
    if not draft_content:
        print("[SYNTH] Ошибка: нет доступных драфтов.")
        return
    
    # 4. Извлекаем список ошибок из analysis.txt
    errors_match = re.search(r'ОШИБКИ:\s*(.+)', analysis_text, re.DOTALL)
    if errors_match:
        errors_text = errors_match.group(1).strip()
    else:
        errors_text = "ОШИБОК НЕТ"
    
    print(f"[SYNTH] Ошибки: {errors_text[:200]}...")
    
    # 5. Формируем промпт для Синтезатора
    prompt = (
        "Ты — Главный Архитектор. "
        f"Вот выбранный лучший вариант кода (драфт №{draft_number}). "
        f"В нем есть следующие ошибки (от Анализатора): {errors_text}. "
        "Твоя задача — исправить эти ошибки, добавить обработку ошибок и сделать код идеальным. "
        "НЕ СМЕШИВАЙ его с другими вариантами. "
        "Напиши только финальный код, без объяснений. "
        "Используй только стандартные библиотеки Python (os, subprocess, time, datetime, re, sys). "
        f"\n\n--- ВЫБРАННЫЙ ДРАФТ ---\n{draft_content}"
    )

    # 6. Отправляем в Ollama
    print(f"[SYNTH] Отправка запроса в Ollama ({MODEL})...")
    try:
        result = subprocess.run(
            ["ollama", "run", MODEL, prompt],
            capture_output=True,
            text=True,
            timeout=1200
        )
    except subprocess.TimeoutExpired:
        print("[SYNTH] Ошибка: Ollama не ответила за 20 минут.")
        return
    except Exception as e:
        print(f"[SYNTH] Ошибка при вызове Ollama: {e}")
        return

    if result.returncode != 0:
        print(f"[SYNTH] Ошибка: Ollama вернула код {result.returncode}.")
        return

    response_text = result.stdout.strip()
    if not response_text:
        print("[SYNTH] Ошибка: Ollama вернула пустой ответ.")
        return

    # 7. Очищаем код
    clean = clean_code(response_text)
    if not clean:
        print("[SYNTH] Ошибка: не удалось извлечь код.")
        return

    # 8. Сохраняем
    try:
        with open(DRAFT_FINAL, "w", encoding="utf-8") as f:
            f.write(clean)
        print(f"[SYNTH] Финальный код сохранен в draft_final.py ({len(clean)} символов).")
    except Exception as e:
        print(f"[SYNTH] Ошибка при сохранении: {e}")
        return

if __name__ == "__main__":
    main()
