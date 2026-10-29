import os
from llm_core import ask_model, clean_code
FACTORY_DIR = os.path.expanduser("~/takcas_factory")
TASK_FILE = os.path.join(FACTORY_DIR, "task.txt")
DRAFT_1 = os.path.join(FACTORY_DIR, "draft_1.py")
DRAFT_ANALYZED = os.path.join(FACTORY_DIR, "draft_analyzed.py")
MODEL = "qwen2.5-coder:3b"
def main():
    if not os.path.exists(TASK_FILE) or not os.path.exists(DRAFT_1): return
    with open(TASK_FILE, "r", encoding="utf-8") as f: task = f.read().strip()
    with open(DRAFT_1, "r", encoding="utf-8") as f: code = f.read().strip()
    prompt = f"You are an expert Python code reviewer. Check the code for syntax errors and logical issues. Fix them. Ensure it solves the task.\nReturn ONLY raw Python code. No markdown.\nTASK: {task}\nCODE:\n{code}"
    result = ask_model(MODEL, prompt, max_tokens=1500)
    if result:
        clean = clean_code(result)
        with open(DRAFT_ANALYZED, "w", encoding="utf-8") as f: f.write(clean)
        print("[ANALYZER] Код сохранен в draft_analyzed.py")
    else: print("[ANALYZER] Ошибка генерации.")
if __name__ == "__main__": main()
