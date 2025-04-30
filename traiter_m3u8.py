import os
import datetime
import time
import requests
from download_playlist import check_ffmpeg, get_ts_files_from_m3u8

def calculate_eta(start_time, downloaded_size, speed, total_size):
    remaining = total_size - downloaded_size
    return datetime.timedelta(seconds=(remaining / speed)) if speed > 0 else "..."

def download_ts_file(ts_url, output_file, log_callback=print, stop_flag=lambda: False):
    response = requests.get(ts_url, stream=True)
    total_size = int(response.headers.get('Content-Length', 0))

    with open(output_file, 'wb') as f:
        start_time = time.time()
        downloaded = 0
        for chunk in response.iter_content(chunk_size=1024):
            if stop_flag():
                log_callback("🛑 Téléchargement interrompu.")
                return False
            if chunk:
                f.write(chunk)
                downloaded += len(chunk)
    return True

def assemble_ts_files(ts_files, output_file):
    list_path = os.path.join("temp", "ts_files.txt")
    with open(list_path, 'w') as f:
        for ts_file in ts_files:
            f.write(f"file '{os.path.abspath(os.path.join('temp', ts_file))}'\n")

    os.system(f'ffmpeg -y -f concat -safe 0 -i "{list_path}" -c copy "{output_file}"')
    os.remove(list_path)

def download_movie(m3u8_url, log_callback=print, progress_callback=lambda p, info="": None, stop_flag=lambda: False):
    output_dir = "out"
    temp_dir = "temp"
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(temp_dir, exist_ok=True)

    output_file = os.path.join(
        output_dir,
        datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".mp4"
    )

    if not check_ffmpeg():
        log_callback("❌ ffmpeg n'est pas installé.")
        return

    ts_files = get_ts_files_from_m3u8(m3u8_url)
    if not ts_files:
        log_callback("❌ Aucun segment trouvé.")
        return

    log_callback(f"📥 {len(ts_files)} segments détectés. Téléchargement...")

    start_time = time.time()
    total_files = len(ts_files)

    for idx, ts_file in enumerate(ts_files, start=1):
        if stop_flag():
            log_callback("🛑 Téléchargement annulé.")
            return

        ts_url = m3u8_url.rsplit('/', 1)[0] + '/' + ts_file
        ts_output_file = os.path.join(temp_dir, ts_file)

        success = download_ts_file(ts_url, ts_output_file, log_callback, stop_flag)
        if not success:
            return

        elapsed = datetime.timedelta(seconds=int(time.time() - start_time))
        elapsed_seconds = time.time() - start_time
        avg_time_per_file = elapsed_seconds / idx if idx > 0 else 0
        remaining_files = total_files - idx
        eta_seconds = avg_time_per_file * remaining_files
        eta = datetime.timedelta(seconds=int(eta_seconds))

        progress_callback(
            idx / total_files,
            f"{idx}/{total_files}.ts | Temps écoulé : {elapsed} | ETA : {eta}"
        )


    log_callback("✅ Tous les segments sont téléchargés.")
    log_callback("🎬 Assemblage avec ffmpeg...")
    assemble_ts_files(ts_files, output_file)

    # Nettoyage
    for ts_file in ts_files:
        try:
            os.remove(os.path.join(temp_dir, ts_file))
        except Exception:
            pass

    log_callback("🧹 temp/ nettoyé.")
    log_callback(f"🎥 Vidéo sauvegardée : {output_file}")
