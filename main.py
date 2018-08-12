import subprocess

if __name__ == "__main__":
    files = ["worker_gmail.py", "listener_gmail.py", "worker_preprocess.py", "listener_preprocess.py", "worker_voice.py", "listener_voice.py", "worker_timer.py", "listener_timer.py"]
    for file in files:
        p = subprocess.Popen(['python', file], stderr=subprocess.STDOUT)
    p.wait()