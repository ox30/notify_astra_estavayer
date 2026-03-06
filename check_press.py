#!/usr/bin/env python3
"""
Surveillance des communiqués de presse OFROU - Filiale Estavayer-le-Lac
Envoie une notification ntfy.sh quand un nouveau communiqué est publié.
"""

import requests
from bs4 import BeautifulSoup
import hashlib
import os

# Configuration
URL = "https://www.astra.admin.ch/astra/fr/home/themes/routes-nationales/chantiers/communiques-de-presse-des-filiales-de-l-ofrou/communiques-de-presse-de-la-filiale-d-estavayer-le-lac.html"
NTFY_TOPIC = "ofrou-estavayer"
HASH_FILE = "last_hash.txt"


def get_press_releases():
    """Récupère la liste des communiqués de presse."""
    response = requests.get(URL, timeout=30)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Les communiqués sont dans des balises h3 avec des liens
    releases = []
    for h3 in soup.find_all('h3'):
        link = h3.find('a')
        if link and link.get('title'):
            releases.append(link.get('title'))
    
    return releases


def get_content_hash(releases):
    """Génère un hash du contenu des communiqués."""
    content = "\n".join(releases)
    return hashlib.md5(content.encode()).hexdigest()


def load_previous_hash():
    """Charge le hash précédent depuis le fichier."""
    if os.path.exists(HASH_FILE):
        with open(HASH_FILE, 'r') as f:
            return f.read().strip()
    return None


def save_hash(hash_value):
    """Sauvegarde le hash actuel dans le fichier."""
    with open(HASH_FILE, 'w') as f:
        f.write(hash_value)


def send_notification(latest_release):
    """Envoie une notification via ntfy.sh."""
    requests.post(
        "https://ntfy.sh/",
        json={
            "topic": NTFY_TOPIC,
            "title": "Nouveau communiqué OFROU",
            "message": f"📢 {latest_release}",
            "tags": ["construction", "road"],
            "click": URL
        }
    )
    print(f"✅ Notification envoyée: {latest_release}")


def main():
    print("🔍 Vérification des communiqués de presse OFROU...")
    
    # Récupérer les communiqués
    releases = get_press_releases()
    if not releases:
        print("❌ Aucun communiqué trouvé")
        return
    
    print(f"📋 {len(releases)} communiqués trouvés")
    
    # Calculer le hash actuel
    current_hash = get_content_hash(releases)
    previous_hash = load_previous_hash()
    
    # Comparer
    if previous_hash is None:
        print("🆕 Premier lancement - sauvegarde de l'état initial")
        save_hash(current_hash)
    elif current_hash != previous_hash:
        print("🚨 Changement détecté!")
        send_notification(releases[0])  # Le plus récent est en premier
        save_hash(current_hash)
    else:
        print("✓ Pas de changement")


if __name__ == "__main__":
    main()
