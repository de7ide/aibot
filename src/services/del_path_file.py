import os
import time


def clear_old_files(folder: str, age_limit: int):
    now = time.time()
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
