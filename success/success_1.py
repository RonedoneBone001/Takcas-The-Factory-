import datetime

with open('report.txt', 'w') as file:
    file.write(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))