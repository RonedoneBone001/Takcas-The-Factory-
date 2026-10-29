import os
import datetime
from time import time

def func(path):
    try:
        with open(path, 'w+') as f:
            f.write(str(datetime.datetime.now()))
    except Exception as e:
        print(f"Error writing to file: {e}")
    print(str(datetime.datetime.now()))
    return

func(os.getcwd()+'/report.txt')