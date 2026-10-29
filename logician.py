import os
import subprocess
import re

# --- НАСТРОЙКИ ---
FACTORY_DIR = os.path.expanduser("~/takcas_factory")
DRAFT_FILE = os.path.join(FACTORY_DIR, "draft.py")
LOGIC_REPORT_FILE = os.path.join(FACTORY_DIR, "logic_report.txt")
DOCS_FILE = os.path.join(FACTORY_DIR, "docs", "termux_api.md")
MODEL = "llama3.2:1b"

def search_docs(query):
    """Ищет строки с query в termux_api.md (не более 10 строк)."""
    if not os.path.exists(DOCS_FILE):
        return ""
    try:
        with open(DOCS_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        found = []
        for line in lines:
            if query.lower() in line.lower():
                found.append(line.strip())
                if len(found) >= 10:
                    break
        
        return "\n".join(found)
    except Exception as e:
        print(f"[LOGICIAN] Ошибка при поиске в документации: {e}")
        return ""

def main():
    print("[LOGICIAN] Запуск Логика...")
    
    if not os.path.exists(FACTORY_DIR):
        print(f"[LOGICIAN] Ошибка: папка фабрики не найдена: {FACTORY_DIR}")
        return

    if not os.path.exists(DRAFT_FILE):
        print(f"[LOGICIAN] Ошибка: файл draft.py не найден: {DRAFT_FILE}")
        return

    try:
        with open(DRAFT_FILE, "r", encoding="utf-8") as f:
            code_text = f.read().strip()
        if not code_text:
            print("[LOGICIAN] Ошибка: файл draft.py пуст.")
            return
        print(f"[LOGICIAN] Код прочитан ({len(code_text)} символов).")
    except Exception as e:
        print(f"[LOGICIAN] Ошибка при чтении draft.py: {e}")
        return

    termux_commands = re.findall(r'termux-[a-z0-9-]+', code_text.lower())
    docs_context = ""
    for cmd in set(termux_commands):
        found = search_docs(cmd)
        if found:
            docs_context += f"\n[Документация по {cmd}]:\n{found}\n"

    prompt_parts = [
        "Ты — модуль проверки. Твой ответ будет автоматически обрезан парсером, если превысит лимит.",
        "ФОРМАТ ОТВЕТА СТРОГО:",
        "[СТАТУС] | [ПРИЧИНА]",
        "Где [СТАТУС] — это только слово УСПЕХ или ОШИБКА.",
        "Где [ПРИЧИНА] — не более 5 слов.",
        "Пример хорошего ответа: УСПЕХ | код логичен",
        "Пример плохого ответа: ОШИБКА | повтор действия",
        "Если твой ответ будет длиннее, система выдаст ошибку и ты не пройдешь проверку. Не пиши ничего кроме этой строки."
    ]
    
    if docs_context:
        prompt_parts.append(
            "Вот выдержки из официальной документации Termux:\n" + 
            docs_context + 
            "\nСверяй код с этими выдержками."
        )
    
    prompt_parts.append(f"Код для проверки:\n{code_text}")
    prompt = "\n".join(prompt_parts)

    print(f"[LOGICIAN] Отправка запроса в Ollama ({MODEL})...")
    try:
        result = subprocess.run(
            ["ollama", "run", MODEL, prompt],
            capture_output=True, text=True, timeout=600
        )
    except subprocess.TimeoutExpired:
        print("[LOGICIAN] Ошибка: Ollama не ответила за 10 минут (таймаут).")
        return
    except Exception as e:
        print(f"[LOGICIAN] Ошибка при вызове Ollama: {e}")
        return

    if result.returncode != 0:
        print(f"[LOGICIAN] Ошибка: Ollama вернула код {result.returncode}.")
        print(f"[LOGICIAN] stderr: {result.stderr}")
        return

    response_text = result.stdout.strip()[:60]
    if not response_text:
        print("[LOGICIAN] Ошибка: Ollama вернула пустой ответ.")
        return

    try:
        with open(LOGIC_REPORT_FILE, "w", encoding="utf-8") as f:
            f.write(response_text)
        print(f"[LOGICIAN] Проверка завершена. Результат сохранен в logic_report.txt")
        print(f"[LOGICIAN] Отчет:\n{response_text}")
    except Exception as e:
        print(f"[LOGICIAN] Ошибка при сохранении отчета: {e}")
        return

if __name__ == "__main__":
    main()

