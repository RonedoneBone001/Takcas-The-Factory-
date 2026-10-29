import os
import subprocess
import shutil
import time
import re
FACTORY_DIR = os.path.expanduser("~/takcas_factory")
SANDBOX_DIR = os.path.join(FACTORY_DIR, "sandbox")
SOURCE_FILE = os.path.join(FACTORY_DIR, "draft_final.py")
TARGET_FILE = os.path.join(SANDBOX_DIR, "app.py")
TIMEOUT = 15 # Увеличили таймаут для тестов
BLACKLIST = [r"os\.remove", r"os\.unlink", r"shutil\.rmtree", r"shutil\.move", r"subprocess\.run.*rm\s", r"os\.system", r"eval\(", r"exec\(", r"__import__\('os'\)", r"open\(.*['\"]\/", r"open\(.*['\"]~"]

def is_safe(code):
    for pattern in BLACKLIST:
        if re.search(pattern, code, re.IGNORECASE):
            return False, f"Обнаружена опасная команда: {pattern}"
    return True, "OK"

def main():
    if not os.path.exists(SANDBOX_DIR): os.makedirs(SANDBOX_DIR, exist_ok=True)
    if not os.path.exists(SOURCE_FILE): return
    with open(SOURCE_FILE, "r", encoding="utf-8") as f: code = f.read()
    
    safe, reason = is_safe(code)
    if not safe:
        print(f"[SANDBOX] БЛОКИРОВКА! {reason}")
        with open(os.path.join(SANDBOX_DIR, "sandbox_error.log"), "w", encoding="utf-8") as f: f.write(f"ОШИБКА: {reason}")
        return
    shutil.copy2(SOURCE_FILE, TARGET_FILE)
    
    try:
        process = subprocess.Popen(["python", TARGET_FILE], cwd=SANDBOX_DIR, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate(timeout=TIMEOUT)
        if process.returncode == 0:
            print("[SANDBOX] УСПЕХ (код и тесты прошли)")
            with open(os.path.join(SANDBOX_DIR, "sandbox_success.log"), "w", encoding="utf-8") as f: f.write("OK")
        else:
            print(f"[SANDBOX] ОШИБКА (упал с кодом {process.returncode})")
            with open(os.path.join(SANDBOX_DIR, "sandbox_error.log"), "w", encoding="utf-8") as f: f.write(stderr)
    except subprocess.TimeoutExpired:
        process.kill()
        print("[SANDBOX] ОШИБКА (завис)")
        with open(os.path.join(SANDBOX_DIR, "sandbox_error.log"), "w", encoding="utf-8") as f: f.write("Timeout")
if __name__ == "__main__": main()
