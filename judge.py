import os
import ast
from llm_core import ask_model, clean_code

FACTORY_DIR = os.path.expanduser("~/takcas_factory")
DRAFT_FILE = os.path.join(FACTORY_DIR, "draft_analyzed.py")
TASK_FILE = os.path.join(FACTORY_DIR, "task.txt")
DRAFT_FINAL = os.path.join(FACTORY_DIR, "draft_final.py")
LOGIC_ERRORS = os.path.join(FACTORY_DIR, "logic_errors.txt")
SYNTAX_ERRORS = os.path.join(FACTORY_DIR, "syntax_errors.txt")
CODER_ERRORS = os.path.join(FACTORY_DIR, "coder_errors.txt")
MODEL = "qwen2.5-coder:3b"

def read_file(path):
    if not os.path.exists(path): return ""
    with open(path, "r", encoding="utf-8") as f: return f.read().strip()

def main():
    if not os.path.exists(DRAFT_FILE) or not os.path.exists(TASK_FILE): return
    with open(DRAFT_FILE, "r", encoding="utf-8") as f: current_code = f.read().strip()
    with open(TASK_FILE, "r", encoding="utf-8") as f: task = f.read().strip()
    
    logic_err = read_file(LOGIC_ERRORS)
    syntax_err = read_file(SYNTAX_ERRORS)
    coder_err = read_file(CODER_ERRORS)
    
    errors_text = ""
    if logic_err and "УСПЕХ" not in logic_err.upper(): errors_text += f"Logic: {logic_err}\n"
    if syntax_err and "УСПЕХ" not in syntax_err.upper(): errors_text += f"Syntax: {syntax_err}\n"
    if coder_err and "УСПЕХ" not in coder_err.upper(): errors_text += f"Code Quality: {coder_err}\n"
    
    print("[JUDGE] Финальная проверка и генерация тестов...")
    prompt = (
        f"Task: {task}\n"
        f"Code:\n{current_code}\n"
        f"Errors found by critics:\n{errors_text if errors_text else 'None.'}\n"
        "Fix any remaining errors. THEN, add a simple test at the end of the file inside `if __name__ == '__main__':` using `assert` to verify basic functionality. Return ONLY Python code."
    )
    
    result = ask_model(MODEL, prompt, max_tokens=1500)
    if result:
        clean = clean_code(result)
        if len(clean) > 10 and "def " in clean:
            try:
                ast.parse(clean)
                with open(DRAFT_FINAL, "w", encoding="utf-8") as f: f.write(clean)
                print("[JUDGE] Финальный код с тестом сохранен.")
            except SyntaxError:
                print("[JUDGE] ОШИБКА: Невалидный синтаксис. Оставляю старый код.")
                with open(DRAFT_FINAL, "w", encoding="utf-8") as f: f.write(current_code)
        else:
            print("[JUDGE] ОШИБКА: Пустой код. Оставляю старый.")
            with open(DRAFT_FINAL, "w", encoding="utf-8") as f: f.write(current_code)
if __name__ == "__main__": main()
