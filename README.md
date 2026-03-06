# 📢 OFROU Press Monitor

Surveillance automatique des communiqués de presse de la filiale OFROU d'Estavayer-le-Lac.

## 🚀 Mise en place

### 1. Créer le repo GitHub

1. Va sur [github.com/new](https://github.com/new)
2. Nom du repo : `ofrou-monitor` (ou ce que tu veux)
3. Laisse-le **public** (ou private, les deux marchent)
4. Crée le repo

### 2. Ajouter les fichiers

Clone ton repo et ajoute les fichiers :

```bash
git clone https://github.com/TON-USERNAME/ofrou-monitor.git
cd ofrou-monitor

# Copie les fichiers check_press.py et .github/workflows/check-press.yml
# (structure ci-dessous)

git add .
git commit -m "Initial setup"
git push
```

Structure finale :
```
ofrou-monitor/
├── .github/
│   └── workflows/
│       └── check-press.yml
├── check_press.py
└── README.md
```

### 3. Autoriser GitHub Actions à push

1. Va dans **Settings** → **Actions** → **General**
2. Dans "Workflow permissions", sélectionne **Read and write permissions**
3. Sauvegarde

### 4. Installer ntfy sur ton téléphone

1. Installe l'app **ntfy** ([Android](https://play.google.com/store/apps/details?id=io.heckel.ntfy) / [iOS](https://apps.apple.com/app/ntfy/id1625396347))
2. Abonne-toi au topic : `ofrou-estavayer`

### 5. Tester

1. Va dans l'onglet **Actions** de ton repo
2. Clique sur "Check OFROU Press Releases"
3. Clique "Run workflow" → "Run workflow"
4. Vérifie que ça passe ✅

## 📱 Topic ntfy

- **Topic** : `ofrou-estavayer`
- **URL** : https://ntfy.sh/ofrou-estavayer

## ⏰ Fréquence

Le script tourne toutes les heures. Pour changer :

Dans `.github/workflows/check-press.yml`, modifie le cron :
- `'*/15 * * * *'` → toutes les 15 min
- `'0 * * * *'` → toutes les heures (actuel)
- `'0 */6 * * *'` → toutes les 6 heures

## 🔧 Personnalisation

Pour surveiller une autre filiale, modifie `URL` dans `check_press.py`.

Pour changer le topic ntfy, modifie `NTFY_TOPIC` dans `check_press.py`.
