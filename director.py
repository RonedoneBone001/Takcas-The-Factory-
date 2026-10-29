import os
import subprocess
import shutil
import datetime
from llm_core import free_memory

FACTORY_DIR = os.path.expanduser("~/takcas_factory")
SUCCESS_DIR = os.path.join(FACTORY_DIR, "success")
TRASH_DIR = os.path.join(FACTORY_DIR, "trash")
SANDBOX_DIR = os.path.join(FACTORY_DIR, "sandbox")
TASK_FILE = os.path.join(FACTORY_DIR, "task.txt")
FEEDBACK_FILE = os.path.join(FACTORY_DIR, "feedback.txt")
DRAFT_FINAL = os.path.join(FACTORY_DIR, "draft_final.py")
SANDBOX_TARGET = os.path.join(SANDBOX_DIR, "voice_jarvis.py")
SANDBOX_SUCCESS_LOG = os.path.join(SANDBOX_DIR, "sandbox_success.log")
SANDBOX_ERROR_LOG = os.path.join(SANDBOX_DIR, "sandbox_error.log")

ERROR_FILES = [
    "logic_errors.txt", "syntax_errors.txt", "coder_errors.txt"
]

MAX_ATTEMPTS = 3

def run_script(script_name):
    path = os.path.join(FACTORY_DIR, script_name)
    try:
        res = subprocess.run(["python", path], cwd=FACTORY_DIR, timeout=1200)
        return res.returncode == 0
    except Exception:
        return False

def clean_old_logs():
    # Удаляем старые отчеты критиков и логи песочницы
    for f in ERROR_FILES:
        p = os.path.join(FACTORY_DIR, f)
        if os.path.exists(p): os.remove(p)
    for f in [SANDBOX_SUCCESS_LOG, SANDBOX_ERROR_LOG]:
        if os.path.exists(f): os.remove(f)

def main():
    for d in [SUCCESS_DIR, TRASH_DIR, SANDBOX_DIR]:
        os.makedirs(d, exist_ok=True)

    if not os.path.exists(TASK_FILE):
        print("[DIRECTOR] Нет task.txt")
        return

    for attempt in range(1, MAX_ATTEMPTS + 1):
        print(f"\n[DIRECTOR] === Попытка {attempt} из {MAX_ATTEMPTS} ===")
        
        if os.path.exists(FEEDBACK_FILE): os.remove(FEEDBACK_FILE)

        if not free_memory(): print("[DIRECTOR] Память не освободилась. Остановка."); return
        print("[DIRECTOR] Запуск Кодера...")
        if not run_script("coder.py"): continue

        if not free_memory(): print("[DIRECTOR] Память не освободилась. Остановка."); return
        print("[DIRECTOR] Запуск Аналитика...")
        if not run_script("analyzer.py"): continue

        # Очистка перед критиками
        clean_old_logs()

        if not free_memory(): print("[DIRECTOR] Память не освободилась. Остановка."); return
        run_script("critic_logic.py")
        
        if not free_memory(): print("[DIRECTOR] Память не освободилась. Остановка."); return
        run_script("critic_syntax.py")
        
        if not free_memory(): print("[DIRECTOR] Память не освободилась. Остановка."); return
        run_script("critic_coder.py")

        if not free_memory(): print("[DIRECTOR] Память не освободилась. Остановка."); return
        print("[DIRECTOR] Запуск Судьи...")
        if not run_script("judge.py"): continue

        if not os.path.exists(DRAFT_FINAL): continue

        print("[DIRECTOR] Запуск Песочницы...")
        shutil.copy2(DRAFT_FINAL, SANDBOX_TARGET)
        if not run_script("sandbox.py"): continue

        if os.path.exists(SANDBOX_SUCCESS_LOG):
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            shutil.copy2(DRAFT_FINAL, os.path.join(SUCCESS_DIR, f"success_{timestamp}.py"))
            print(f"\n[DIRECTOR] УСПЕХ! Код в success_{timestamp}.py")
            return
        else:
            print("[DIRECTOR] Песочница нашла ошибки. Записываю фидбек...")
            shutil.copy2(DRAFT_FINAL, os.path.join(TRASH_DIR, f"trash_{attempt}.py"))
            
            fb = []
            for err_file in ERROR_FILES:
                p = os.path.join(FACTORY_DIR, err_file)
                if os.path.exists(p):
                    with open(p, "r", encoding="utf-8") as f:
                        content = f.read().strip()
                        if content and "УСПЕХ" not in content.upper():
                            fb.append(f"[{err_file}]: {content}")
            
            if os.path.exists(SANDBOX_ERROR_LOG):
                with open(SANDBOX_ERROR_LOG, "r", encoding="utf-8") as f:
                    fb.append(f"[Песочница]: {f.read().strip()}")
            
            if fb:
                with open(FEEDBACK_FILE, "w", encoding="utf-8") as f:
                    f.write("\n".join(fb))

    print(f"\n[DIRECTOR] Не удалось за {MAX_ATTEMPTS} попытки.")

if __name__ == "__main__":
    main()
