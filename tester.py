import os
import subprocess
import re

# --- НАСТРОЙКИ ---
FACTORY_DIR = os.path.expanduser("~/takcas_factory")
DRAFT_FILE = os.path.join(FACTORY_DIR, "draft.py")
REPORT_FILE = os.path.join(FACTORY_DIR, "report.txt")
COMMANDS_FILE = os.path.join(FACTORY_DIR, "termux_commands.txt")
DOCS_FILE = os.path.join(FACTORY_DIR, "docs", "termux_api.md")
MODEL = "qwen2.5-coder:3b"

# Базовый справочник (если файла нет)
DEFAULT_COMMANDS = """- termux-torch on  |  ["termux-torch", "on"]
- termux-torch off  |  ["termux-torch", "off"]
- termux-brightness <0-255>  |  ["termux-brightness", "<0-255>"]
- termux-volume music <0-15>  |  ["termux-volume", "music", "<0-15>"]
- termux-camera-photo -c 0 <path>  |  ["termux-camera-photo", "-c", "0", "<path>"]
- termux-clipboard-set <text>  |  ["termux-clipboard-set", "<text>"]
- termux-tts-speak <text>  |  ["termux-tts-speak", "<text>"]
- am start -a android.intent.action.MAIN -c android.intent.category.LAUNCHER -p <package_name>  |  ["am", "start", "-a", "android.intent.action.MAIN", "-c", "android.intent.category.LAUNCHER", "-p", "<package_name>"]"""

def ensure_commands_file():
    """Создает файл справочника, если его нет."""
    if not os.path.exists(COMMANDS_FILE):
        try:
            with open(COMMANDS_FILE, "w", encoding="utf-8") as f:
                f.write(DEFAULT_COMMANDS)
            print(f"[TESTER] Создан справочник команд: {COMMANDS_FILE}")
        except Exception as e:
            print(f"[TESTER] Ошибка при создании справочника: {e}")

def load_commands():
    """Читает справочник команд из файла (если есть)."""
    if not os.path.exists(COMMANDS_FILE):
        return ""
    try:
        with open(COMMANDS_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception as e:
        print(f"[TESTER] Ошибка при чтении справочника: {e}")
        return ""

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
        print(f"[TESTER] Ошибка при поиске в документации: {e}")
        return ""

def main():
    print("[TESTER] Запуск Синтаксического Монстра...")
    
    if not os.path.exists(FACTORY_DIR):
        print(f"[TESTER] Ошибка: папка фабрики не найдена: {FACTORY_DIR}")
        return

    ensure_commands_file()

    if not os.path.exists(DRAFT_FILE):
        print(f"[TESTER] Ошибка: файл draft.py не найден: {DRAFT_FILE}")
        return

    try:
        with open(DRAFT_FILE, "r", encoding="utf-8") as f:
            code_text = f.read().strip()
        if not code_text:
            print("[TESTER] Ошибка: файл draft.py пуст.")
            return
        print(f"[TESTER] Код прочитан ({len(code_text)} символов).")
    except Exception as e:
        print(f"[TESTER] Ошибка при чтении draft.py: {e}")
        return

    commands_text = load_commands()
    
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
        "Пример хорошего ответа: УСПЕХ | код корректен",
        "Пример плохого ответа: ОШИБКА | неверный импорт",
        "Если твой ответ будет длиннее, система выдаст ошибку и ты не пройдешь проверку. Не пиши ничего кроме этой строки."
    ]
    
    if commands_text:
        prompt_parts.append(
            "СПРАВОЧНИК КОМАНД TERMUX:\n" + commands_text +
            "\n\nСверяй команды в коде со справочником. "
            "Если команды нет в справочнике — это ОШИБКА."
        )
    
    if docs_context:
        prompt_parts.append(
            "Вот выдержки из официальной документации Termux:\n" + 
            docs_context
        )
    
    prompt_parts.append(f"Код для проверки:\n{code_text}")
    prompt = "\n".join(prompt_parts)

    print(f"[TESTER] Отправка запроса в Ollama ({MODEL})...")
    try:
        result = subprocess.run(
            ["ollama", "run", MODEL, prompt],
            capture_output=True, text=True, timeout=600
        )
    except subprocess.TimeoutExpired:
        print("[TESTER] Ошибка: Ollama не ответила за 10 минут (таймаут).")
        return
    except Exception as e:
        print(f"[TESTER] Ошибка при вызове Ollama: {e}")
        return

    if result.returncode != 0:
        print(f"[TESTER] Ошибка: Ollama вернула код {result.returncode}.")
        print(f"[TESTER] stderr: {result.stderr}")
        return

    response_text = result.stdout.strip()[:60]
    if not response_text:
        print("[TESTER] Ошибка: Ollama вернула пустой ответ.")
        return

    try:
        with open(REPORT_FILE, "w", encoding="utf-8") as f:
            f.write(response_text)
        print(f"[TESTER] Проверка завершена. Результат сохранен в report.txt")
        print(f"[TESTER] Отчет:\n{response_text}")
    except Exception as e:
        print(f"[TESTER] Ошибка при сохранении отчета: {e}")
        return

if __name__ == "__main__":
    main()
