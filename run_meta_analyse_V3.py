import subprocess
import time

def run_meta_analyse():
    subprocess.run(['python', 'meta_analyse_v3.py'], shell=True)
    time.sleep(360)