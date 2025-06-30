import requests
import zipfile
import os
import sys
import shutil
import subprocess
import re

def get_chrome_version():
    """Récupère la version installée de Google Chrome (Windows uniquement)"""
    try:
        output = subprocess.check_output(
            r'reg query "HKEY_CURRENT_USER\Software\Google\Chrome\BLBeacon" /v version',
            shell=True, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL)
        version = re.search(r"[\d.]+", output.decode()).group(0)
        print(f"✅ Chrome installé : {version}")
        return version
    except Exception:
        print("❌ Impossible de récupérer la version de Chrome.")
        return None

def download_chromedriver(version, dest_dir="driver"):
    """Télécharge le ChromeDriver correspondant"""
    major_version = version.split('.')[0]
    print(f"🔽 Téléchargement du ChromeDriver pour Chrome {version}...")

    # Récupération du dernier driver compatible
    meta_url = f"https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json"
    response = requests.get(meta_url)
    if response.status_code != 200:
        print("❌ Erreur lors de l'accès au metadata ChromeDriver.")
        return None

    drivers = response.json()
    target_version = None
    for entry in drivers["channels"]["Stable"]["downloads"]["chromedriver"]:
        if entry["platform"] == "win64":
            target_version = drivers["channels"]["Stable"]["version"]
            url = entry["url"]
            break

    if not url:
        print("❌ URL introuvable pour ChromeDriver.")
        return None

    os.makedirs(dest_dir, exist_ok=True)
    zip_path = os.path.join(dest_dir, "chromedriver.zip")

    with open(zip_path, "wb") as f:
        f.write(requests.get(url).content)

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(dest_dir)

    os.remove(zip_path)
    print(f"✅ ChromeDriver extrait dans : {dest_dir}")
    return os.path.join(dest_dir, "chromedriver.exe")

if __name__ == "__main__":
    version = get_chrome_version()
    if version:
        chromedriver_path = download_chromedriver(version)
        if chromedriver_path:
            print(f"🚀 Prêt à utiliser ChromeDriver depuis : {chromedriver_path}")
        else:
            print("❌ Échec de l'installation de ChromeDriver.")
