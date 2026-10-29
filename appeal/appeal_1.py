import random
import sys

try:
    random_number = random.randint(10, 50)
    print(random_number)
except Exception as e:
    print(f"An error occurred: {e}", file=sys.stderr)