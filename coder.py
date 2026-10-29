import os
from llm_core import ask_model, clean_code
FACTORY_DIR = os.path.expanduser("~/takcas_factory")
TASK_FILE = os.path.join(FACTORY_DIR, "task.txt")
DRAFT_FILE = os.path.join(FACTORY_DIR, "draft_1.py")
MODEL = "qwen2.5-coder:3b"
def main():
    if not os.path.exists(TASK_FILE): return
    with open(TASK_FILE, "r", encoding="utf-8") as f: task = f.read().strip()
    prompt = f"You are an expert Python developer. Write the complete code for the following task.\nReturn ONLY raw Python code. No markdown, no explanations.\nTASK: {task}\n"
    result = ask_model(MODEL, prompt, max_tokens=1500)
    if result:
        clean = clean_code(result)
        with open(DRAFT_FILE, "w", encoding="utf-8") as f: f.write(clean)
        print("[CODER] Код сохранен в draft_1.py")
    else: print("[CODER] Ошибка генерации.")
if __name__ == "__main__": main()
