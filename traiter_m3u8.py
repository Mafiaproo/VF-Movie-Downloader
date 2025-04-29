import os
import sys
import datetime
import time
import shutil
import requests
from download_playlist import check_ffmpeg, get_ts_files_from_m3u8

def calculate_eta(start_time, downloaded_size, speed, total_size):
    elapsed_time = time.time() - start_time
    remaining_size = total_size - downloaded_size
    remaining_time = (remaining_size / speed) if speed > 0 else 0
    return datetime.timedelta(seconds=remaining_time)

def download_ts_file(ts_url, output_file, log_callback=print, stop_flag=lambda: False):
    response = requests.get(ts_url, stream=True)
    total_size = int(response.headers.get('Content-Length', 0))
    
    with open(output_file, 'wb') as f:
        start_time = time.time()
        downloaded_size = 0
        
        for chunk in response.iter_content(chunk_size=1024):
            if stop_flag():
                log_callback("🛑 Téléchargement interrompu.")
                return False
            if chunk:
                f.write(chunk)
                downloaded_size += len(chunk)
                
                elapsed_time = time.time() - start_time
                speed = downloaded_size / elapsed_time if elapsed_time > 0 else 0
                eta = calculate_eta(start_time, downloaded_size, speed, total_size)
                
                log_callback(f"📦 {os.path.basename(output_file)}: {downloaded_size}/{total_size} | ETA: {eta} | Speed: {speed/1024:.2f} KB/s")
    return True


def assemble_ts_files(ts_files, output_file):
    ts_file_list = os.path.join("temp", "ts_files.txt")
    with open(ts_file_list, 'w') as f:
        for ts_file in ts_files:
            f.write(f"file '{os.path.join('temp', ts_file)}'\n")
    
    os.system(f"ffmpeg -f concat -safe 0 -i {ts_file_list} -c copy {output_file}")
    os.remove(ts_file_list)

def download_movie(m3u8_url, log_callback=print, progress_callback=lambda x: None, stop_flag=lambda: False):
    output_dir = "out"
    temp_dir = "temp"
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(temp_dir, exist_ok=True)

    output_file = os.path.join(
        output_dir,
        datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".mp4"
    )

    if not check_ffmpeg():
        log_callback("❌ ffmpeg n'est pas installé ou introuvable.")
        return

    ts_files = get_ts_files_from_m3u8(m3u8_url)
    if not ts_files:
        log_callback("❌ Impossible de récupérer les fichiers .ts.")
        return

    log_callback(f"📥 {len(ts_files)} segments détectés. Téléchargement...")

    total_files = len(ts_files)
    for idx, ts_file in enumerate(ts_files, start=1):
        if stop_flag():
            log_callback("🛑 Téléchargement annulé.")
            return
        ts_url = m3u8_url.rsplit('/', 1)[0] + '/' + ts_file
        ts_output_file = os.path.join(temp_dir, ts_file)
        log_callback(f"⬇️ [{idx}/{total_files}] {ts_file}")
        success = download_ts_file(ts_url, ts_output_file, log_callback=log_callback, stop_flag=stop_flag)
        if not success:
            return
        progress_callback(idx / total_files)

    log_callback("✅ Tous les segments sont téléchargés.")
    log_callback("🎬 Assemblage avec ffmpeg...")
    assemble_ts_files(ts_files, output_file)

    for ts_file in ts_files:
        try:
            os.remove(os.path.join(temp_dir, ts_file))
        except Exception:
            pass

    log_callback("🧹 temp/ nettoyé.")
    log_callback(f"🎥 Vidéo sauvegardée : {output_file}")
