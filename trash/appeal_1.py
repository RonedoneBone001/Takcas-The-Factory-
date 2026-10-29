import datetime
import os
import subprocess
import sys
import re

def smart_alarm(time_str, reminder_text):
    # Check if the time format is correct
    if not re.match(r'^([01]?[0-9]|2[0-3]):([0-5][0-9])$', time_str):
        print("Неверное время")
        return
    
    # Parse the time string
    try:
        alarm_time = datetime.datetime.strptime(time_str, "%H:%M")
    except ValueError:
        print("Неверное время")
        return
    
    # Get the current time
    current_time = datetime.datetime.now()
    
    # Calculate the time difference
    time_difference = alarm_time - current_time
    
    # If the alarm time is already passed, adjust to the next day
    if time_difference.total_seconds() < 0:
        alarm_time += datetime.timedelta(days=1)
    
    # Wait until the alarm time
    time.sleep(time_difference.total_seconds())
    
    # Use termux-tts-speak to speak the reminder
    subprocess.run(["termux-tts-speak", reminder_text or "Пора вставать!"])[12D[K
вставать!"])

# Example usage
smart_alarm("07:30", "Пора вставать!")