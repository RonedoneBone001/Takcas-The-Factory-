from flask import Flask, request, render_template, redirect, url_for
import sqlite3
from datetime import datetime
import os
import requests

app = Flask(__name__)

# Placeholder function to simulate Ollama summarization
def summarize_text(text, model="qwen2.5:3b"):
    url = "https://api.ollama.ai/predict"
    headers = {
        "Authorization": "Bearer YOUR_OLLAMA_API_KEY",
        "Content-Type": "application/json"
    }
    data = {
        "model": model,
        "prompt": text
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()  # Raise an error for bad responses
        summary = response.json().get("output", "No summary available")
        return summary
    except requests.exceptions.RequestException as e:
        return f"Ollama is offline: {str(e)}"

@app.route('/', methods=['GET', 'POST'])
def index():
    summary = None
    error_message = None
    if request.method == 'POST':
        text = request.form.get('textarea')
        if text:
            if len(text) > 5000:
                error_message = "Text exceeds 5000 characters."
            else:
                try:
                    summary = summarize_text(text)
                except Exception as e:
                    error_message = f"Ollama is offline: {str(e)}"
        else:
            error_message = "Text cannot be empty."
    
    # Log to SQLite with timestamp
    conn = sqlite3.connect('logs.db')
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS logs (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT, text TEXT, summary TEXT)")
    c.execute("INSERT INTO logs (timestamp, text, summary) VALUES (?, ?, ?)",
             (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), text, summary))
    conn.commit()
    conn.close()
    
    return render_template('index.html', summary=summary, error_message=error_message)

@app.route('/requirements.txt')
def requirements():
    return """
Flask
sqlalchemy
requests
"""

if __name__ == '__main__':
    app.run(debug=True)