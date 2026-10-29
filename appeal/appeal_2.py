import datetime

def write_report():
    try:
        with open("report.txt", "w") as file:
            file.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"[9D[K
%H:%M:%S"))
    except IOError as e:
        print(f"Ошибка при записи в файл: {e}")
    except Exception as e:
        print(f"Произошла неизвестная ошибка: {e}")

write_report()