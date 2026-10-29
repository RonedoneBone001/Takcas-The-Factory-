import os
from llm_core import ask_model
FACTORY_DIR = os.path.expanduser("~/takcas_factory")
DRAFT_FILE = os.path.join(FACTORY_DIR, "draft_analyzed.py")
TASK_FILE = os.path.join(FACTORY_DIR, "task.txt")
REPORT_FILE = os.path.join(FACTORY_DIR, "syntax_errors.txt")
MODEL = "qwen2.5:1.5b"
def main():
    if not os.path.exists(DRAFT_FILE) or not os.path.exists(TASK_FILE): return
    with open(DRAFT_FILE, "r", encoding="utf-8") as f: code = f.read().strip()
    with open(TASK_FILE, "r", encoding="utf-8") as f: task = f.read().strip()
    prompt = f"Задача: {task}\nТы — Синтаксический Монстр. Проверь код на синтаксические ошибки (незакрытые скобки, пропущенные импорты). Если всё хорошо — напиши 'УСПЕХ'. Если есть ошибки — 'ОШИБКА: [причина]'. \nКод:\n{code}"
    result = ask_model(MODEL, prompt, max_tokens=300)
    if result:
        with open(REPORT_FILE, "w", encoding="utf-8") as f: f.write(result.strip())
        print("[CRITIC_SYNTAX] Отчет сохранен.")
if __name__ == "__main__": main()
