import os
import urllib.request

# --- НАСТРОЙКИ ---
DOCS_DIR = os.path.expanduser("~/takcas_factory/docs")
MAX_SIZE = 8 * 1024 * 1024  # 8 МБ

# WHITELIST: только эти ссылки будут скачаны (максимум 3)
WHITELIST = [
    {
        "url": "https://raw.githubusercontent.com/termux/termux-api/master/README.md",
        "filename": "termux_api.md"
    },
    # Добавь до 2 других ссылок (если нужно)
    # {
    #     "url": "https://example.com/some_doc.md",
    #     "filename": "some_doc.md"
    # },
]

def download_file(url, filepath):
    """
    Скачивает файл с проверкой размера.
    Возвращает True (успех) / False (ошибка).
    """
    try:
        # Открываем URL (с таймаутом 30 сек)
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as response:
            # Читаем данные (с лимитом размера)
            data = response.read(MAX_SIZE + 1)  # Читаем на 1 байт больше лимита
            
            # Проверка размера
            if len(data) > MAX_SIZE:
                print(f"[DOCS] Ошибка: Файл слишком большой, отклонен (>{MAX_SIZE} байт)")
                return False
            
            # Записываем в файл
            with open(filepath, "wb") as f:
                f.write(data)
            
            print(f"[DOCS] Скачано: {filepath} ({len(data)} байт)")
            return True
    
    except Exception as e:
        print(f"[DOCS] Ошибка при скачивании {url}: {e}")
        return False

def main():
    print("[DOCS] Запуск обновления документации...")
    
    # 1. Создаем папку docs, если ее нет
    try:
        os.makedirs(DOCS_DIR, exist_ok=True)
        print(f"[DOCS] Папка создана: {DOCS_DIR}")
    except Exception as e:
        print(f"[DOCS] Ошибка при создании папки: {e}")
        return

    # 2. Проверяем лимит ссылок
    if len(WHITELIST) > 3:
        print("[DOCS] Ошибка: В WHITELIST больше 3 ссылок. Исправь список.")
        return

    # 3. Обрабатываем каждую ссылку
    for item in WHITELIST:
        url = item["url"]
        filename = item["filename"]
        filepath = os.path.join(DOCS_DIR, filename)
        
        print(f"\n[DOCS] Обработка: {url}")
        
        # 3.1 Проверка на повторное скачивание
        if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
            print(f"[DOCS] Файл уже существует: {filepath} (пропускаем)")
            continue
        
        # 3.2 Скачиваем
        download_file(url, filepath)
    
    print("\n[DOCS] Обновление документации завершено.")

if __name__ == "__main__":
    main()
