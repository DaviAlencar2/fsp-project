import datetime
import os

def save_log(file_name,ip):
    log_dir = os.path.join(os.path.dirname(__file__), "data/logs")
    log_file = os.path.join(log_dir, "log.csv")
    date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file, "a") as f:
        f.write(f"{date_time};{file_name};{ip}\n")