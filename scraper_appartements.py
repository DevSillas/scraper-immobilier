import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pandas as pd
from time import sleep
import re

# --- Scraper ---
def scraper_appartements(nb_pages=1):
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
            print("Aucune annonce trouvée")
            continue

        for container in containers:
            appart_data = {
                'Nbre_de_piece': 'Non spécifié',
                'Prix': 'Non spécifié',
                'Adresse': 'Non spécifié',
                'Image_URL': 'Non disponible'
            }

            try:
                link = container.find('a')
                if not link or 'href' not in link.attrs:
                    continue

                detail_url = urljoin('https://sn.coinafrique.com/', link['href'])
                detail_response = requests.get(detail_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
                detail_response.raise_for_status()
                detail_soup = BeautifulSoup(detail_response.text, 'html.parser')

                pieces_elem = detail_soup.select_one('span:-soup-contains("Nbre de pièces") + span.qt')
                if pieces_elem:
                    appart_data['Nbre_de_piece'] = pieces_elem.get_text(strip=True)

                prix_elem = detail_soup.find('p', class_='price')
                if prix_elem:
                    appart_data['Prix'] = prix_elem.get_text(strip=True).replace(' ', '')

                adresse_elem = detail_soup.select_one('span.valign-wrapper[data-address]')
                if adresse_elem:
                    appart_data['Adresse'] = adresse_elem.get_text(strip=True)

                img_elem = container.find('img', class_='ad__card-img')
                if img_elem and img_elem.has_attr('src'):
                    appart_data['Image_URL'] = img_elem['src']

                df.append(appart_data)

            except Exception as e:
                print(f"Erreur sur une annonce: {str(e)}")
                continue

            sleep(1)
        sleep(2)

    return pd.DataFrame(df)

# --- Nettoyage ---
def clean_price(price):
    if pd.isna(price) or str(price).strip().lower() in ['prixsurdemande', 'non spécifié']:
        return None

    cleaned = re.sub(r'[^\d.,]', '', str(price))
    try:
        price_num = float(cleaned.replace(',', '.'))
        if price_num < 100:
            return None
        return price_num
    except:
        return None

def clean_address(address):
    if pd.isna(address):
        return None

    address = address.replace('"', '').replace("'", "")
    address = re.sub(r',\s*Dakar,\s*S[ée]n[ée]gal$', '', address, flags=re.IGNORECASE)
    address = re.sub(r',\s*S[ée]n[ée]gal$', '', address, flags=re.IGNORECASE)
    return address.strip()

def clean_data(df):
    df['Prix'] = df['Prix'].apply(clean_price)
    df['Adresse'] = df['Adresse'].apply(clean_address)
    df = df.dropna(subset=['Prix', 'Adresse'])
    df = df.drop_duplicates(subset=['Prix', 'Adresse', 'Image_URL'])
    return df[['Nbre_de_piece', 'Prix', 'Adresse', 'Image_URL']]
