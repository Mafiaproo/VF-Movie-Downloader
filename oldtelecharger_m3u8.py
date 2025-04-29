import subprocess
import os, sys, datetime

# URL du fichier .m3u8
#m3u8_url = "https://exemple.com/chemin/flux.m3u8"
m3u8_url = sys.argv[1]
# Nom de sortie
output_file = "out/" + str(datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")).replace(" ", "_") + ".mp4"

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
        "-y",  # overwrite if exists
        "-i", url,
        "-c", "copy",  # pas de ré-encodage
        "-bsf:a", "aac_adtstoasc",
        output
    ]

    try:
        subprocess.run(command, check=True)
        print(f"✅ Téléchargement terminé : {output}")
    except subprocess.CalledProcessError as e:
        print("❌ Erreur lors du téléchargement :", e)

if __name__ == "__main__":
    if not check_ffmpeg():
        print("❌ ffmpeg n'est pas installé ou introuvable dans le PATH.")
    else:
        download_m3u8(m3u8_url, output_file)
