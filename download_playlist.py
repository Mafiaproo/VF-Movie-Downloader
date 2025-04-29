# ffmpeg_tools.py

import subprocess, requests

# Vérifie si ffmpeg est installé
def check_ffmpeg():
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except FileNotFoundError:
        return False

# Téléchargement via ffmpeg
def download_m3u8(url, output):
    print(f"Téléchargement de la vidéo depuis : {url}")
    command = [
        "ffmpeg",
        "-y",
        "-i", url,
        "-c", "copy",
        "-bsf:a", "aac_adtstoasc",
        output
    ]
    try:
        subprocess.run(command, check=True)
        print(f"✅ Téléchargement terminé : {output}")
    except subprocess.CalledProcessError as e:
        print("❌ Erreur lors du téléchargement :", e)


def get_ts_files_from_m3u8(m3u8_url):
    response = requests.get(m3u8_url)
    if response.status_code == 200:
        # Parser le fichier m3u8 et récupérer les fichiers .ts
        ts_files = []
        for line in response.text.splitlines():
            if line.endswith('.ts'):
                ts_files.append(line.strip())
        return ts_files
    return []
