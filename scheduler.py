import datetime
import subprocess
import time

def run_script():
    subprocess.run(['python3', 'chargingAvailability.py'])

hour = None
while True:
    current_time = datetime.datetime.now()
    if current_time.time() >= datetime.time(7, 30) and current_time.time() <= datetime.time(20, 00):
        if current_time.hour != hour and current_time.minute % 90 == 0:
            print(f'Do something {current_time}')
            run_script()
            hour = current_time.hour
    time.sleep(60)
