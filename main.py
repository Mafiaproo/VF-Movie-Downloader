import tkinter as tk
from tkinter import ttk
import threading
import time

from traiter_m3u8 import download_movie
from get_playlist_url_from_web import extract_m3u8_from_nested_iframe

root = tk.Tk()
root.title("Legal movie downloader")
root.iconbitmap("icon.ico")
root.geometry("1000x600")

# Contrôle
stop_download = False
download_thread = None
start_time = None

# Callbacks
def log_to_textbox(msg):
    log_text_box.insert(tk.END, msg + "\n")
    log_text_box.see(tk.END)

def update_progress(progress, infos=""):
    download_progress_bar['value'] = progress * 100
    progress_label.config(text=infos)
    root.update_idletasks()

def search_and_download_movie():
    global stop_download, download_thread, start_time
    stop_download = False

    playlist_url = ""
    if "https://" in movie_input.get():
        playlist_url = extract_m3u8_from_nested_iframe(movie_input.get())
    else:
        log_to_textbox("❌ Fonction de recherche non encore implémentée.")
        return

    if not playlist_url:
        log_to_textbox("❌ Aucun lien m3u8 détecté.")
        return

    def task():
        global start_time
        start_time = time.time()
        download_movie(
            playlist_url,
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

# UI
tk.Label(root, text="Legal movie downloader", font=("Arial", 30)).pack(pady=10)

movie_input = ttk.Entry(root, font=("Arial", 16), width=80)
movie_input.pack(pady=10)

ttk.Button(root, text="Download Movie", command=search_and_download_movie).pack(pady=5)
ttk.Button(root, text="Annuler", command=cancel_download).pack(pady=5)

log_text_box = tk.Text(root, height=15, width=120, state="disabled")
log_text_box.pack(pady=10)

progress_frame = ttk.Frame(root)
progress_frame.pack(pady=5)

download_progress_bar = ttk.Progressbar(progress_frame, length=700)
download_progress_bar.pack(side=tk.LEFT)

progress_label = ttk.Label(progress_frame, text="0/0.ts | Temps écoulé : 0s | ETA : ...", width=50)
progress_label.pack(side=tk.LEFT, padx=10)

root.mainloop()
