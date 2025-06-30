import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pandas as pd
from time import sleep
import re
import undetected_chromedriver as uc

# Initialisation du DataFrame
def scraper_terrains(nb_pages=1):
    options = uc.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = uc.Chrome(
    options=options,
    driver_executable_path="driver\chromedriver-win64\chromedriver.exe"
    
    )

    df = []
    for page in range(1, nb_pages + 1):
        print(f"Traitement de la page {page}...")
        url = f'https://sn.coinafrique.com/categorie/appartements?page={page}'

        try:
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
            response.raise_for_status()
        except Exception as e:
            print(f"Erreur lors de l'accès à {url}: {str(e)}")
            continue

        soup = BeautifulSoup(response.text, 'html.parser')
        containers = soup.find_all('div', class_='col s6 m4 l3')

        if not containers:
            print("Aucune annonce trouvée - structure HTML modifiée?")
            continue

        for container in containers:
            terrain_data = {
                'Superficie': 'Non spécifié',
                'Prix': 'Non spécifié',
                'Adresse': 'Non spécifié',
                'Image_URL': 'Non disponible'
            }

            try:
                # Extraction du lien de détail
                link = container.find('a')
                if not link or 'href' not in link.attrs:
                    continue

                detail_url = urljoin('https://sn.coinafrique.com/', link['href'])

                # Récupération de la page de détail
                try:
                    detail_response = requests.get(detail_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
                    detail_response.raise_for_status()
                    detail_soup = BeautifulSoup(detail_response.text, 'html.parser')
                except:
                    continue

                # Extraction des informations depuis la page de détail
                # Superficie
                superficie_elem = detail_soup.select_one('span:-soup-contains("Superficie") + span.qt')
                if superficie_elem:
                    terrain_data['Superficie'] = superficie_elem.get_text(strip=True)
                
                # Prix
                prix_elem = detail_soup.find('p', class_='price')
                if prix_elem:
                    terrain_data['Prix'] = prix_elem.get_text(strip=True).replace(' ', '')

                # Adresse
                adresse_elem = detail_soup.select_one('span.valign-wrapper[data-address]')
                if adresse_elem:
                    terrain_data['Adresse'] = adresse_elem.get_text(strip=True)

                # Image
                img_elem = container.find('img', class_='ad__card-img')
                if img_elem and img_elem.has_attr('src'):
                    terrain_data['Image_URL'] = img_elem['src']

                df.append(terrain_data)
            except Exception as e:
                print(f"Erreur sur une annonce: {str(e)}")
                continue

            sleep(1)  # Pause entre les annonces

        sleep(2)  # Pause entre les pages

    driver.quit()
    df = pd.DataFrame(df)
    return df

# Fonctions de nettoyage des données
def clean_price(price):
    """Nettoyer et convertir les prix"""
    if pd.isna(price) or str(price).strip().lower() in ['prixsurdemande', 'non spécifié']:
        return None

    cleaned = re.sub(r'[^\d.,]', '', str(price))
    try:
        price_num = float(cleaned.replace(',', '.'))
        if price_num < 100:  # Filtre les prix anormalement bas
            return None
        return price_num
    except:
        return None

def clean_surface(text):
    """Extraire la superficie du texte"""
    if pd.isna(text):
        return None

    patterns = [
        r'(\d+)\s*m[²2]',
        r'(\d+)\s*ha',
        r'(\d+)\s*hectares',
        r'(\d+)\s*metros',
        r'(\d+)\s*㎡'
    ]

    for pattern in patterns:
        match = re.search(pattern, str(text), re.IGNORECASE)
        if match:
            return int(match.group(1))

    return None

def clean_address(address):
    """Nettoyer les adresses"""
    if pd.isna(address):
        return None

    address = address.replace('"', '').replace("'", "")
    address = re.sub(r',\s*Dakar,\s*S[ée]n[ée]gal$', '', address, flags=re.IGNORECASE)
    address = re.sub(r',\s*S[ée]n[ée]gal$', '', address, flags=re.IGNORECASE)
    return address.strip()

def clean_data(df):
    """Fonction principale de nettoyage"""
    df['Prix'] = df['Prix'].apply(clean_price)
    df['Superficie_m2'] = df['Superficie'].apply(clean_surface)
    df['Adresse'] = df['Adresse'].apply(clean_address)
    df = df.dropna(subset=['Prix', 'Adresse'])
    df = df.drop_duplicates(subset=['Superficie', 'Prix', 'Adresse', 'Image_URL'])
    cols = ['Superficie', 'Superficie_m2', 'Prix', 'Adresse', 'Image_URL']
    return df[cols]

