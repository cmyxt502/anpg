import os
import time
import sys

OUTPUT_DIR = os.path.join(sys.path[0], 'output')
AGE_LIMIT = 24

age_limit_seconds = AGE_LIMIT * 60 * 60  # Convert to seconds

now = time.time()

for root, dirs, files in os.walk(OUTPUT_DIR):
    for name in files:
        print(f"Checking file: {name}")
        file_path = os.path.join(root, name)
        try:
            mtime = os.path.getmtime(file_path)
            if now - mtime > age_limit_seconds:
                os.remove(file_path)
                print(f"Deleted: {file_path}")
        except Exception as e:
            print(f"Error deleting {file_path}: {e}")