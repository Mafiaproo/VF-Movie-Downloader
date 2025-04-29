import tkinter as tk
from tkinter import *
from tkinter import ttk
import threading

from traiter_m3u8 import download_movie

root = Tk()

# Paramètres fenêtre
root.title("Legal movie downloader")
root.iconbitmap("icon.ico")
root.geometry("1000x600")

# Variables de contrôle
stop_download = False
download_thread = None

# Fonctions de rappel
def log_to_textbox(msg):
    log_text_box.insert(END, msg + "\n")
    log_text_box.see(END)

def update_progress(progress):
    download_progress_bar['value'] = progress * 100
    root.update_idletasks()

def search_and_download_movie():
    global stop_download, download_thread
    stop_download = False

    url = movie_input.get()
    if not url:
        log_to_textbox("❌ Aucun lien fourni.")
        return

    def task():
        download_movie(
            url,
            log_callback=log_to_textbox,
            progress_callback=update_progress,
            stop_flag=lambda: stop_download
        )

    download_thread = threading.Thread(target=task)
    download_thread.start()

def cancel_download():
    global stop_download
    stop_download = True
    log_to_textbox("🛑 Téléchargement annulé par l'utilisateur.")

# Interface utilisateur
title = Label(root, text="Legal movie downloader", font=("Arial", 30))
title.pack()

movie_input = Entry(master=root, font=("Arial", 20))
movie_input.pack(pady=10)

download_btn = Button(root, font=("Arial", 10), text="Download Movie", command=search_and_download_movie)
download_btn.pack(pady=5)

cancel_btn = Button(root, font=("Arial", 10), text="Annuler", command=cancel_download)
cancel_btn.pack(pady=5)

log_text_box = Text(root, height=20, width=100)
log_text_box.pack(pady=15)

download_progress_bar = ttk.Progressbar(root, length=700)
download_progress_bar.pack(pady=10)

root.mainloop()
