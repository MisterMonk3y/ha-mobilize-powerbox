# Changelog

Toutes les modifications notables de ce projet seront documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/),
et ce projet adhère au [Semantic Versioning](https://semver.org/lang/fr/).

## [1.0.0] - 2026-01-15

### Ajouté
- 🎉 Première release publique
- ✅ Configuration via interface graphique (Config Flow)
- ✅ Support multilingue (FR/EN)
- ✅ Prêt pour HACS
- ✅ 13 capteurs (mesures temps réel, TiC, configuration)
- ✅ Aucun identifiant en clair
- ✅ API locale uniquement (aucune connexion cloud)
- ✅ Diagnostics intégrés pour le debug
- ✅ Options de reconfiguration sans réinstaller
- ✅ Compatible avec le tableau de bord énergétique Home Assistant
- ✅ Icône Mobilize officielle

### Capteurs Disponibles
#### Mesures Temps Réel
- Courant de charge (A)
- Tension (V)
- Puissance instantanée (W)
- Énergie de la session (kWh)
- Énergie totale de la borne (kWh)

#### Téléinformation Client (TiC/Linky)
- Courant phase A (A)
- Puissance apparente (VA)

#### Configuration
- Courant maximum autorisé (A)
- Limite puissance foyer (W)
- Mode gestion dynamique
- Mode de charge
- Pays
- Type d'installation

### Endpoints API Utilisés
- `/v1.0/auth` - Authentification JWT
- `/v1.0/meters` - Mesures temps réel (4 compteurs)
- `/v1.0/configs` - Configuration système

### Compatibilité
- Home Assistant 2023.1+
- PowerBox (tous modèles)
- PowerBox Verso

---

## [Non publié]

### Prévu
- Support des notifications push
- Historique des sessions de charge
- Graphiques de consommation personnalisés
- Support OCPP (si disponible)

---

**Légende :**
- `Ajouté` : Nouvelles fonctionnalités
- `Modifié` : Changements dans les fonctionnalités existantes
- `Déprécié` : Fonctionnalités qui seront supprimées
- `Supprimé` : Fonctionnalités supprimées
- `Corrigé` : Corrections de bugs
- `Sécurité` : Corrections de vulnérabilités
