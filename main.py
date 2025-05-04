import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import threading
import time, sys, os
import winsound

from traiter_m3u8 import download_movie
from get_playlist_url_from_web import extract_m3u8_from_nested_iframe
from search_movie import find_film_link

bg_color = "#636363"
fg_color = "#807e7e"

root = tk.Tk()
root.title("Legal movie downloader")
root.geometry("1000x600")
root.resizable(width=False, height=False)

root.config(background=bg_color)

if len(sys.orig_argv) == 2:
    root.iconbitmap("icon.ico")
else:
    for element in os.listdir():
        if(os.path.isdir(element)):
            root.iconbitmap(element + "\icon.ico")


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
    elif movie_input.get() == None or movie_input.get() == "":
        log_to_textbox("You need to fill in the movie title or the url")
        messagebox.showwarning("Movie entry null", "You need to fill in the movie title or the url for download the movie")
        return
    else:
        #log_to_textbox("❌ Fonction de recherche non encore implémentée.")
        matches = find_film_link(search_name=movie_input.get())
        if len(matches) == 1:
            log_to_textbox(f"Movie found : {matches[0][1]}, starting download")
            playlist_url = matches[0][2]
        elif len(matches) > 1 :
            log_to_textbox(f"We found multiple movies, select one please \n {matches}")

            


        else :
            log_to_textbox("Movie not found ! Try to write just de main title(Sonic, Avengers), not with the extra (Sonic 2, Avengers Infinity war, ...)")
            messagebox.showerror(title="Movie not found", message="Movie not found ! Try to write just de main title(Sonic, Avengers), not with the extra (Sonic 2, Avengers Infinity war, ...)")
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
        messagebox.showinfo("Movie Download", "The movie has been successfully downloaded")

    download_thread = threading.Thread(target=task)
    download_thread.start()

def cancel_download():
    global stop_download
    stop_download = True
    log_to_textbox("🛑 Téléchargement annulé par l'utilisateur.")

def multiple_movie_message_box():
    #messagebox.showinfo(title="Multiple Movies Founds", message="We found multiple movie with the keyword : " + movie_input.get())
    messagebox.showerror(title="No Mobie found", message="We didnt found movie with the keyword : " + movie_input.get())

# UI
tk.Label(root,background=bg_color, text="Legal movie downloader", font=("Arial", 30)).pack(pady=10)

movie_input = ttk.Entry(root, background=fg_color, font=("Arial", 16), width=80)
movie_input.pack(pady=10)

download_btn = tk.Button(root, background=fg_color, text="Download Movie", command=search_and_download_movie).pack(pady=5)
stop_download_btn = tk.Button(root, background=fg_color, text="Annuler", command=cancel_download).pack(pady=5)

log_text_box = tk.Text(root, background="#b5b3b3", height=15, width=120, state="normal")
log_text_box.bind("<Key>", lambda e: "break")
log_text_box.pack(pady=10)

progress_frame = tk.Frame(root, bg=fg_color)
progress_frame.pack(pady=5)

download_progress_bar = ttk.Progressbar(progress_frame, length=700)
download_progress_bar.pack(side=tk.LEFT)

progress_label = tk.Label(progress_frame, text="0/0.ts | Temps écoulé : 0s | ETA : ...", width=50, bg=fg_color)
progress_label.pack(side=tk.LEFT, padx=10)

root.mainloop()
