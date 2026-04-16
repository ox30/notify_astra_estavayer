#!/usr/bin/env python3
"""
Surveillance des communiqués de presse OFROU - Toutes les filiales
Envoie une notification ntfy.sh quand un nouveau communiqué est publié.
"""

import requests
from bs4 import BeautifulSoup
import hashlib
import json
import os
import time

# ============================================================================
# CONFIGURATION
# ============================================================================

NTFY_TOPIC = "ofrou-vmz-7k9x2"  # Topic privé
HASH_FILE = "last_hashes.json"

# Headers pour simuler un navigateur (évite les blocages)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "fr-CH,fr;q=0.9,en;q=0.8",
}

# Toutes les filiales OFROU (URLs officielles)
FILIALES = {
    "Estavayer": {
        "url": "https://www.astra.admin.ch/astra/fr/home/themes/routes-nationales/chantiers/communiques-de-presse-des-filiales-de-l-ofrou/communiques-de-presse-de-la-filiale-d-estavayer-le-lac.html",
        "emoji": "🇨🇭"
    },
    "Thoune": {
        "url": "https://www.astra.admin.ch/astra/fr/home/themes/routes-nationales/chantiers/communiques-de-presse-des-filiales-de-l-ofrou/communiques-de-presse-de-la-filiale-de-thoune.html",
        "emoji": "🏔️"
    },
    "Zofingue": {
        "url": "https://www.astra.admin.ch/astra/fr/home/themes/routes-nationales/chantiers/communiques-de-presse-des-filiales-de-l-ofrou/communiques-de-presse-de-la-filiale-de-zofingue.html",
        "emoji": "🏭"
    },
    "Winterthur": {
        "url": "https://www.astra.admin.ch/astra/fr/home/themes/routes-nationales/chantiers/communiques-de-presse-des-filiales-de-l-ofrou/communiques-de-presse-de-la-filiale-de-winterthur.html",
        "emoji": "🌄"
    },
    "Bellinzone": {
        "url": "https://www.astra.admin.ch/astra/fr/home/themes/routes-nationales/chantiers/communiques-de-presse-des-filiales-de-l-ofrou/communiques-de-presse-de-la-filiale-de-bellinzone.html",
        "emoji": "🌴"
    }
}


# ============================================================================
# FONCTIONS
# ============================================================================

def get_press_releases(url: str, max_retries: int = 3) -> list[str]:
    """Récupère la liste des communiqués de presse d'une filiale."""
    
    for attempt in range(max_retries):
        try:
            response = requests.get(
                url, 
                headers=HEADERS, 
                timeout=60,  # Timeout plus long
            )
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            releases = []
            for h3 in soup.find_all('h3'):
                link = h3.find('a')
                if link and link.get('title'):
                    releases.append(link.get('title'))
            
            return releases
            
        except requests.exceptions.Timeout:
            print(f"   ⏱️ Timeout (tentative {attempt + 1}/{max_retries})")
            if attempt < max_retries - 1:
                time.sleep(5)  # Attendre 5s avant de réessayer
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
            if attempt < max_retries - 1:
                time.sleep(3)
    
    return []


def get_content_hash(releases: list[str]) -> str:
    """Génère un hash du contenu des communiqués."""
    content = "\n".join(releases)
    return hashlib.md5(content.encode()).hexdigest()


def load_previous_hashes() -> dict:
    """Charge les hashs précédents depuis le fichier."""
    if os.path.exists(HASH_FILE):
        with open(HASH_FILE, 'r') as f:
            return json.load(f)
    return {}


def save_hashes(hashes: dict):
    """Sauvegarde les hashs actuels dans le fichier."""
    with open(HASH_FILE, 'w') as f:
        json.dump(hashes, f, indent=2)


def send_notification(filiale: str, emoji: str, latest_release: str, url: str):
    """Envoie une notification via ntfy.sh."""
    try:
        requests.post(
            "https://ntfy.sh/",
            json={
                "topic": NTFY_TOPIC,
                "title": f"{emoji} OFROU {filiale}",
                "message": latest_release,
                "tags": ["construction", "road"],
                "click": url
            },
            timeout=30
        )
        print(f"   📱 Notification envoyée!")
    except Exception as e:
        print(f"   ❌ Erreur notification: {e}")


def check_filiale(name: str, config: dict, previous_hashes: dict) -> tuple[str, bool]:
    """
    Vérifie une filiale et retourne (nouveau_hash, a_changé).
    """
    print(f"\n🔍 {name}")
    
    releases = get_press_releases(config['url'])
    if not releases:
        print(f"   ⚠️ Aucun communiqué trouvé")
        return previous_hashes.get(name, ""), False
    
    print(f"   📋 {len(releases)} communiqués")
    
    current_hash = get_content_hash(releases)
    previous_hash = previous_hashes.get(name)
    
    if previous_hash is None:
        print(f"   🆕 Premier check - sauvegarde état initial")
        return current_hash, False
    
    if current_hash != previous_hash:
        print(f"   🚨 Nouveau communiqué détecté!")
        send_notification(name, config['emoji'], releases[0], config['url'])
        return current_hash, True
    
    print(f"   ✓ Pas de changement")
    return current_hash, False


def main():
    print("=" * 60)
    print("🚧 OFROU Press Monitor - Toutes les filiales")
    print("=" * 60)
    
    previous_hashes = load_previous_hashes()
    new_hashes = {}
    changes_count = 0
    errors_count = 0
    
    for name, config in FILIALES.items():
        new_hash, changed = check_filiale(name, config, previous_hashes)
        if new_hash:
            new_hashes[name] = new_hash
        else:
            errors_count += 1
            # Garder l'ancien hash en cas d'erreur
            if name in previous_hashes:
                new_hashes[name] = previous_hashes[name]
        if changed:
            changes_count += 1
        
        # Pause entre les requêtes pour éviter le rate limiting
        time.sleep(2)
    
    # Sauvegarder les nouveaux hashs
    save_hashes(new_hashes)
    
    print("\n" + "=" * 60)
    if errors_count > 0:
        print(f"⚠️ {errors_count} erreur(s) de connexion")
    if changes_count > 0:
        print(f"📊 Résumé: {changes_count} nouvelle(s) notification(s)")
    else:
        print("📊 Résumé: Aucun changement détecté")
    print("=" * 60)


if __name__ == "__main__":
    main()
