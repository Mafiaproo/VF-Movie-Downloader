# telecharger.py

import os
import sys
import datetime
import time
import shutil
import requests
from tqdm import tqdm
from download_playlist import check_ffmpeg, get_ts_files_from_m3u8

# Fonction pour calculer le temps estimé d'arrivée (ETA)
def calculate_eta(start_time, downloaded_size, speed, total_size):
    elapsed_time = time.time() - start_time
    remaining_size = total_size - downloaded_size
    remaining_time = (remaining_size / speed) if speed > 0 else 0
    eta = datetime.timedelta(seconds=remaining_time)
    return eta

# Fonction pour télécharger un fichier avec une barre de progression
def download_ts_file(ts_url, output_file):
    response = requests.get(ts_url, stream=True)
    total_size = int(response.headers.get('Content-Length', 0))
    
    # Utilisation de tqdm pour la barre de progression
    with tqdm(total=total_size, unit='B', unit_scale=True, desc=f'Téléchargement de {ts_url}') as pbar:
        with open(output_file, 'wb') as f:
            start_time = time.time()
            downloaded_size = 0
            
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
                    downloaded_size += len(chunk)
                    pbar.update(len(chunk))
                    
                    # Calcul de l'ETA
                    elapsed_time = time.time() - start_time
                    speed = downloaded_size / elapsed_time if elapsed_time > 0 else 0
                    eta = calculate_eta(start_time, downloaded_size, speed, total_size)
                    pbar.set_postfix(ETA=str(eta), speed=f"{speed / 1024:.2f} KB/s")

# Fonction pour assembler les fichiers .ts avec ffmpeg
def assemble_ts_files(ts_files, output_file):
    ts_file_list = os.path.join("temp", "ts_files.txt")
    
    # Créer un fichier de liste de fichiers .ts pour ffmpeg
    with open(ts_file_list, 'w') as f:
        for ts_file in ts_files:
            f.write(f"file '{os.path.join('temp', ts_file)}'\n")
    
    # Utiliser ffmpeg pour assembler les fichiers .ts en une seule vidéo
    os.system(f"ffmpeg -f concat -safe 0 -i {ts_file_list} -c copy {output_file}")
    
    # Supprimer le fichier de liste après l'assemblage
    os.remove(ts_file_list)

# Lecture de l'URL depuis les arguments
if len(sys.argv) < 2:
    print("❌ Veuillez fournir l'URL du fichier .m3u8 en argument.")
    sys.exit(1)

m3u8_url = sys.argv[1]

# Création du dossier de sortie
output_dir = "out"
os.makedirs(output_dir, exist_ok=True)

# Création du dossier temporaire pour les fichiers .ts
temp_dir = "temp"
os.makedirs(temp_dir, exist_ok=True)

# Génération du nom de fichier sécurisé pour la sortie finale
output_file = os.path.join(
    output_dir,
    datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".mp4"
)

if not check_ffmpeg():
    print("❌ ffmpeg n'est pas installé ou introuvable dans le PATH.")
else:
    # Récupérer les fichiers .ts à partir de l'URL m3u8
    ts_files = get_ts_files_from_m3u8(m3u8_url)
    
    if not ts_files:
        print("❌ Impossible de récupérer les fichiers .ts à partir de l'URL .m3u8.")
        sys.exit(1)

    print(f"📥 Téléchargement des segments .ts en cours...")

    # Télécharger chaque fichier .ts dans le dossier temp/
    for ts_file in ts_files:
        ts_url = m3u8_url.rsplit('/', 1)[0] + '/' + ts_file  # Construit l'URL complète du fichier .ts
        ts_output_file = os.path.join(temp_dir, ts_file)  # Chemin vers le dossier temp/
        
        # Télécharger le fichier .ts avec la barre de progression
        download_ts_file(ts_url, ts_output_file)

    print("✅ Téléchargement terminé !")

    # Assembler les fichiers .ts en une vidéo finale et la sauvegarder dans le dossier out/
    print(f"🎬 Assemblage des fichiers .ts en une vidéo : {output_file}")
    assemble_ts_files(ts_files, output_file)

    # Après l'assemblage, vider le dossier temp/
    print("🧹 Nettoyage du dossier temp...")
    for ts_file in ts_files:
        ts_file_path = os.path.join(temp_dir, ts_file)
        if os.path.exists(ts_file_path):
            os.remove(ts_file_path)

    print("✅ Dossier temp vidé.")
    print(f"🎥 Vidéo finale enregistrée dans : {output_file}")
