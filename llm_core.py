import os
import time
import requests
import re

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"

def free_memory(*args, **kwargs):
    print("[MEM] Ожидание 5 секунд для очистки памяти...")
    time.sleep(5)
    return True

def ask_model(model_name, prompt, max_tokens=500, timeout=600):
    print(f"[LLM] Запрос к {model_name}...")
    payload = {
        "model": model_name,
        "prompt": prompt,
        "stream": False,
        "options": {"num_ctx": 2048, "num_predict": max_tokens}
    }
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=timeout)
        response.raise_for_status()
        return response.json().get("response", "")
    except Exception as e:
        print(f"[LLM] Ошибка API: {e}")
        return None

def clean_code(text):
    if not text: return ""
    match = re.search(r'```(?:python)?\s*(.*?)```', text, re.DOTALL)
    if match: return match.group(1).strip()
    return text.strip()
