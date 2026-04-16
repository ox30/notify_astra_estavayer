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

# ============================================================================
# CONFIGURATION
# ============================================================================

NTFY_TOPIC = "ofrou-vmz-7k9x2"  # Topic privé
HASH_FILE = "last_hashes.json"

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

def get_press_releases(url: str) -> list[str]:
    """Récupère la liste des communiqués de presse d'une filiale."""
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        releases = []
        for h3 in soup.find_all('h3'):
            link = h3.find('a')
            if link and link.get('title'):
                releases.append(link.get('title'))
        
        return releases
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
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
    requests.post(
        "https://ntfy.sh/",
        json={
            "topic": NTFY_TOPIC,
            "title": f"{emoji} OFROU {filiale}",
            "message": latest_release,
            "tags": ["construction", "road"],
            "click": url
        }
    )
    print(f"   📱 Notification envoyée!")


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
    
    for name, config in FILIALES.items():
        new_hash, changed = check_filiale(name, config, previous_hashes)
        new_hashes[name] = new_hash
        if changed:
            changes_count += 1
    
    # Sauvegarder les nouveaux hashs
    save_hashes(new_hashes)
    
    print("\n" + "=" * 60)
    if changes_count > 0:
        print(f"📊 Résumé: {changes_count} nouvelle(s) notification(s)")
    else:
        print("📊 Résumé: Aucun changement détecté")
    print("=" * 60)


if __name__ == "__main__":
    main()
