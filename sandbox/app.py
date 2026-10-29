from flask import Flask, render_template, request, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)

# Database initialization
def get_db_connection():
    conn = sqlite3.connect('app.db')
    conn.row_factory = sqlite3.Row
    return conn

# Route for the home page
@app.route('/', methods=['GET', 'POST'])
def index():
    text = None
    summary = None
    error_message = None

    if request.method == 'POST':
        text = request.form.get('text')

        if not text or len(text) > 5000:
            error_message = "Invalid input. Please enter a non-empty text with less than 5000 characters."
            return render_template('index.html', text=text, summary=summary, error_message=error_message)

        # Save request to database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO requests (text, request_time) VALUES (?, ?)",
                      (text, datetime.now()))
        conn.commit()
        conn.close()

        try:
            # Send request to Ollama
            import requests
            url = 'http://127.0.0.1:11434/api/generate'
            headers = {
                'Content-Type': 'application/json'
            }
            payload = {
                'model': 'qwen2.5:3b',
                'prompt': text
            }
            response = requests.post(url, headers=headers, json=payload)

            # Parse response
            if response.status_code == 200:
                summary = response.json().get('response', 'No summary available.')
                # Save summary to database
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("INSERT INTO summaries (summary, request_id) VALUES (?, ?)",
                              (summary, cursor.lastrowid))
                conn.commit()
                conn.close()
            else:
                error_message = "Error communicating with Ollama. Please try again later."

        except requests.exceptions.RequestException as e:
            error_message = f"An error occurred: {str(e)}"

    return render_template('index.html', text=text, summary=summary, error_message=error_message)

if __name__ == '__main__':
    app.run(debug=True)