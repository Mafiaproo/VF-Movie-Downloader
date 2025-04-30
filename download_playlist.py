import subprocess, requests

def check_ffmpeg():
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except FileNotFoundError:
        return False

def download_m3u8(url, output):
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
        print("❌ Erreur :", e)

def get_ts_files_from_m3u8(m3u8_url):
    response = requests.get(m3u8_url)
    if response.status_code == 200:
        return [line.strip() for line in response.text.splitlines() if line.endswith('.ts')]
    return []
