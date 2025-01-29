import os
import time
import threading
import random
import re
import psutil
from pathlib import Path
from tkinter import Tk, Label, IntVar, ttk
from PIL import Image, ImageTk
from typing import Set
from pystray import Icon, MenuItem, Menu
from PIL import Image as PILImage
import sys

# Global 
gameRunning = True
loadingComplete = False
suspiciousActions = 0
monitoredProcesses: Set[int] = set()
logLock = threading.Lock()
suspiciousActionsLock = threading.Lock()

# Log yazma
def logEvent(message: str):
    with logLock:
        with open("G-AntiCheat.log", "a") as logFile:
            logFile.write(f"[{time.ctime()}] {message}\n")


def displayLoadingScreen():
    def animate_progress():
        for i in range(101):
            time.sleep(0.03)
            progress_var.set(i)
            progress_label.config(text=f"Loading... {i}%")
            root.update_idletasks()
        time.sleep(5)
        root.destroy()

    root = Tk()
    root.title("G-AntiCheat Loading")
    root.config(bg="#2d2f38")


    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()


    window_width = 300
    window_height = 150


    position_top = (screen_height // 2) - (window_height // 2)
    position_left = (screen_width // 2) - (window_width // 2)

    root.geometry(f'{window_width}x{window_height}+{position_left}+{position_top}')
    root.overrideredirect(True)


    try:
        logo_image = Image.open("G-AntiCheat.png")
        logo_image = logo_image.resize((300, 150), Image.ANTIALIAS)
        logo_photo = ImageTk.PhotoImage(logo_image)
        logo_label = Label(root, image=logo_photo, bg="#2d2f38")
        logo_label.image = logo_photo
        logo_label.pack(pady=20)
    except Exception:
        Label(root, text="G-AntiCheat", font=("Arial", 16, "bold"), bg="#2d2f38", fg="white").pack(pady=20)


    progress_var = IntVar()
    progress_bar = ttk.Progressbar(root, orient="horizontal", length=270, mode="determinate", variable=progress_var, maximum=100)
    progress_bar.pack(pady=20)

    progress_label = Label(root, text="Loading... 0%", font=("Arial", 10), bg="#2d2f38", fg="white")
    progress_label.pack()

    threading.Thread(target=animate_progress, daemon=True).start()
    root.mainloop()

# Süreç izleme
def monitorProcesses():
    global suspiciousActions
    while gameRunning:
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                processName = proc.info['name']
                pid = proc.info['pid']
                if pid not in monitoredProcesses and ("inject" in processName or "hack" in processName):
                    monitoredProcesses.add(pid)
                    with suspiciousActionsLock:
                        suspiciousActions += 1
                    logEvent(f"Suspicious process detected: {processName}")
        except Exception as e:
            logEvent(f"Error monitoring processes: {str(e)}")
        time.sleep(0.5)

# Dinamik bellek taraması
def dynamicMemoryScan():
    global suspiciousActions
    while gameRunning:
        try:
            for proc in psutil.process_iter(['pid']):
                try:
                    procHandle = proc.as_dict(attrs=['pid', 'name', 'memory_maps'])
                    for memory_map in procHandle.get('memory_maps', []):
                        if 'rw' in memory_map.perms:
                            with suspiciousActionsLock:
                                suspiciousActions += 1
                            logEvent(f"Suspicious memory manipulation detected in process: {procHandle['name']} (PID: {procHandle['pid']})")
                except Exception:
                    continue
        except Exception as e:
            logEvent(f"Error during memory scan: {str(e)}")
        time.sleep(5)

# Dosya tarama
def scanFiles(directory: str):
    global suspiciousActions
    suspiciousPattern = re.compile(r'.*(hack|cheat|exploit|inject|virus|malware).*', re.IGNORECASE)

    try:
        for entry in Path(directory).rglob('*'):  # Tüm dosyaları tara
            try:
                if entry.is_file() and suspiciousPattern.search(str(entry)):  # Tam yol ile kontrol et
                    with suspiciousActionsLock:
                        suspiciousActions += 1
                    logEvent(f"Suspicious file detected: {entry.resolve()}")
            except PermissionError:
                logEvent(f"Permission denied for file: {entry}")
            except Exception as e:
                logEvent(f"Error accessing file: {entry}. Details: {str(e)}")
    except Exception as e:
        logEvent(f"Error scanning directory: {directory}. Details: {str(e)}")

def initializeAntiCheat():
    global loadingComplete
    logEvent("Starting G-AntiCheat...")

    processThread = threading.Thread(target=monitorProcesses, daemon=True)
    memoryThread = threading.Thread(target=dynamicMemoryScan, daemon=True)
    fileThread = threading.Thread(target=lambda: scanFiles(r"C:\\"), daemon=True)

    processThread.start()
    memoryThread.start()
    fileThread.start()

    loadingComplete = True

def on_quit(icon, item):
    global gameRunning
    gameRunning = False
    icon.stop()
    logEvent("G-AntiCheat stopped by user.")


def repair_application():
    def on_retry():
        repair_window.destroy()
        threading.Thread(target=repair_application, daemon=True).start()

    def on_close():
        repair_window.destroy()

    def perform_repair():
        status_label.config(text="Repairing...", fg="red")
        repair_button.config(state="disabled")
        retry_button.pack_forget()  # Retry butonunu gizle

        
        success = True  
        time.sleep(3)

        if success:
            status_label.config(text="Repair successful!", fg="green")
            close_button.pack()
        else:
            status_label.config(text="Repair failed. Please try again.", fg="red")
            retry_button.pack()

    repair_window = Tk()
    repair_window.title("Repair G-Anticheat")
    repair_window.config(bg="#2d2f38")


    screen_width = repair_window.winfo_screenwidth()
    screen_height = repair_window.winfo_screenheight()


    window_width = 300
    window_height = 200

    position_top = (screen_height // 2) - (window_height // 2)
    position_left = (screen_width // 2) - (window_width // 2)

    repair_window.geometry(f'{window_width}x{window_height}+{position_left}+{position_top}')

   
    repair_window.overrideredirect(True)

    status_label = Label(repair_window, text="Click 'Repair' to fix the G-anticheat.", font=("Arial", 12), bg="#2d2f38", fg="white")
    status_label.pack(pady=20)

    repair_button = ttk.Button(repair_window, text="Repair", command=lambda: threading.Thread(target=perform_repair).start())
    repair_button.pack(pady=10)

    retry_button = ttk.Button(repair_window, text="Retry", command=on_retry)
    close_button = ttk.Button(repair_window, text="Close", command=on_close)

    repair_window.mainloop()


def on_settings(icon, item):
    threading.Thread(target=repair_application, daemon=True).start()

def create_tray_icon():
    icon_image = PILImage.open("G-AntiCheat.png")
    icon = Icon("G-AntiCheat")
    icon.icon = icon_image
    icon.menu = Menu(
        MenuItem("Settings", on_settings),
        MenuItem("Quit", on_quit)
    )
    icon.run()


def main():
    global gameRunning
    print("Starting G-AntiCheat...")


    loadingThread = threading.Thread(target=displayLoadingScreen)
    antiCheatThread = threading.Thread(target=initializeAntiCheat)

    antiCheatThread.start()
    loadingThread.start()

    antiCheatThread.join()
    loadingThread.join()

    print("Monitoring for suspicious activity in the background.")

    trayThread = threading.Thread(target=create_tray_icon, daemon=True)
    trayThread.start()

    try:
        while gameRunning:
            time.sleep(10)
    except KeyboardInterrupt:
        gameRunning = False
        logEvent("G-AntiCheat stopped by user.")

if __name__ == "__main__":
    main()



    # Bu kod Gexnys tarafından yazılmıştır.
    # Tüm hakları Gexnys'e aittir.
    # Eklenmesi gereken kodlar için lütfen Gexnys ile iletişime geçin.
    # E-posta adresi : developergokhan@proton.me
