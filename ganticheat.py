import os
import time
import threading
import random
import re
import psutil
from pathlib import Path
from tkinter import Canvas, Tk, Label, IntVar, ttk
from PIL import Image, ImageTk
from typing import Set

# Global variables
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

# Yükleme ekranı
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
    root.geometry("300x150")
    root.overrideredirect(True)  
    root.config(bg="#2d2f38")

    # Logo
    try:
        logo_image = Image.open("G-AntiCheat.png")
        logo_image = logo_image.resize((300, 150), Image.ANTIALIAS)
        logo_photo = ImageTk.PhotoImage(logo_image)
        logo_label = Label(root, image=logo_photo, bg="#2d2f38")
        logo_label.image = logo_photo
        logo_label.pack(pady=20)
    except Exception:
        Label(root, text="G-AntiCheat", font=("Arial", 16, "bold"), bg="#2d2f38", fg="white").pack(pady=20)

    # İlerleme çubuğu
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
        for entry in Path(directory).rglob('*'):
            try:
                if entry.is_file() and suspiciousPattern.search(entry.name):
                    with suspiciousActionsLock:
                        suspiciousActions += 1
                    logEvent(f"Suspicious file detected: {entry.resolve()}")
            except PermissionError:
                logEvent(f"Permission denied for file: {entry}")
            except Exception as e:
                logEvent(f"Error accessing file: {entry}. Details: {str(e)}")
    except Exception as e:
        logEvent(f"Error scanning directory: {directory}. Details: {str(e)}")

# Anti-hileyi başlat
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

# Ana fonksiyon
def main():
    global gameRunning
    print("Starting G-AntiCheat...")

    # Yükleme ekranı ve anti-hileyi paralel başlat
    loadingThread = threading.Thread(target=displayLoadingScreen)
    antiCheatThread = threading.Thread(target=initializeAntiCheat)

    antiCheatThread.start()
    loadingThread.start()

    antiCheatThread.join()
    loadingThread.join()

    print("Monitoring for suspicious activity in the background. Press Ctrl+C to stop.")

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