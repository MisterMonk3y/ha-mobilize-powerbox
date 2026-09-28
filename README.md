<p align="center">
  <img src="images/logo.png" alt="Mobilize Logo" width="200"/>
</p>

# Mobilize PowerBox - Intégration Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge)](https://github.com/custom-components/hacs)
[![GitHub Release](https://img.shields.io/github/release/MisterMonk3y/ha-mobilize-powerbox.svg?style=for-the-badge&color=blue)](https://github.com/MisterMonk3y/ha-mobilize-powerbox/releases)
[![License](https://img.shields.io/github/license/MisterMonk3y/ha-mobilize-powerbox.svg?style=for-the-badge&color=green)](LICENSE)
[![GitHub Activity](https://img.shields.io/github/commit-activity/m/MisterMonk3y/ha-mobilize-powerbox.svg?style=for-the-badge)](https://github.com/MisterMonk3y/ha-mobilize-powerbox/commits/main)

> [!NOTE]
> ## À Propos de cette Intégration
> Cette intégration **officieuse** permet de suivre votre borne de recharge **Mobilize PowerBox** dans Home Assistant.
>
> **Compatible avec :** PowerBox Verso, PowerBox Uno
>
> **Type d'intégration :** Polling local (aucune connexion cloud)

> [!WARNING]
> ## Avertissement Général
> **Cette intégration n'est pas officiellement supportée par Mobilize/Renault**, et son utilisation pourrait avoir des conséquences inattendues.
>
> Veuillez noter que je développe cette intégration du mieux que je peux, mais **je ne peux donner aucune garantie**. Utilisez cette intégration **à vos propres risques** !
>
> _Je ne suis en aucun cas affilié à Mobilize ou Renault Group._

## 🎉 Fonctionnalités

- ✅ **Configuration via l'interface graphique** (Config Flow)
- ✅ **Aucun mot de passe en clair** dans les fichiers
- ✅ **Support multilingue** (FR/EN)
- ✅ **Prête pour HACS**
- ✅ **24 capteurs** dont mesures temps réel, V2G et TiC
- ✅ **Diagnostics intégrés** pour le debug
- ✅ **Options de reconfiguration** sans réinstaller
- ✅ **API locale uniquement** (aucune connexion cloud)

### Mesures en Temps Réel (toutes les 30s)
- 🔌 Courant de charge (A)
- ⚡ Tension (V)
- 💡 Puissance instantanée (W)
- 🔋 Énergie de la session (kWh)
- 📊 Énergie totale de la borne (kWh)
- 🔁 Puissance réactive / apparente réseau, facteur de puissance
- ⬆️ Énergie injectée totale (V2G / surplus)

### Téléinformation Client (TiC/Linky)
- 📡 Courant phase A
- ⚡ Puissance apparente

### Configuration
- ⚙️ Courant maximum autorisé
- 🏠 Limite puissance foyer
- 🔄 Mode gestion dynamique (Off/TiC/SiteConsumption)
- 🚗 Mode de charge (FreeAccess/OCPP)
- 🌍 Pays et type d'installation
- 🔋 Contrat V2G, profil / topologie réseau
- 🛑 Arrêt d'urgence, courant max hors ligne, déséquilibre de phases
- 📐 Puissance de conception
---

## 📦 Installation

> [!TIP]
> ### Installation Rapide via HACS
> Cliquez sur le bouton ci-dessous pour ajouter automatiquement le dépôt dans HACS :
>
> [![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=MisterMonk3y&repository=ha-mobilize-powerbox&category=integration)

### Méthode 1 : HACS (Recommandée)

1. Ouvrez **HACS** dans Home Assistant
2. Allez dans **Intégrations**
3. Cliquez sur les **3 points** en haut à droite → **Dépôts personnalisés**
4. Ajoutez : `https://github.com/MisterMonk3y/ha-mobilize-powerbox`
5. Catégorie : **Integration**
6. Cherchez "**Mobilize PowerBox**" et cliquez sur **Télécharger**
7. **Redémarrez Home Assistant**

### Méthode 2 : Manuelle

1. Téléchargez la [dernière version](https://github.com/MisterMonk3y/ha-mobilize-powerbox/releases)
2. Extrayez et copiez le dossier `custom_components/mobilize_powerbox` dans `/config/custom_components/`
3. **Redémarrez Home Assistant**

---

## ⚙️ Configuration

> [!IMPORTANT]
> ### Configuration Rapide
> Cliquez sur le bouton ci-dessous pour démarrer la configuration automatiquement :
>
> [![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=mobilize_powerbox)

### Configuration Manuelle

1. Allez dans **Configuration** → **Appareils et Services**
2. Cliquez sur **+ Ajouter une intégration**
3. Cherchez "**Mobilize PowerBox**"
4. Renseignez les informations :

| Champ | Description | Exemple |
|-------|-------------|---------|
| **Adresse IP** | IP locale de votre PowerBox | `192.168.1.50` |
| **Nom d'utilisateur** | Utilisateur interface web | `installer` |
| **Mot de passe** | Mot de passe interface | `votre_mdp` |
| **Nom** | Nom personnalisé (optionnel) | `PowerBox Garage` |
| **Vérifier SSL** | Laissez **décoché** | ❌ |

5. Cliquez sur **Soumettre**

> [!TIP]
> ### 🔍 Comment Trouver l'Adresse IP de votre PowerBox ?
>
> **Méthode 1 : Via votre Box Internet** (recommandé)
> 1. Connectez-vous à votre box (Freebox, Livebox, etc.)
> 2. Allez dans "Équipements" ou "Périphériques réseau"
> 3. Cherchez "PowerBox", "Mobilize" ou "IoTecha"
> 4. Notez l'adresse IP (ex: `192.168.1.50`)
>
> **Méthode 2 : Scanner réseau**
> - Utilisez **Fing** (Android/iOS) ou **Advanced IP Scanner** (Windows)
> - Scannez votre réseau local
> - Cherchez un appareil "IoTecha" ou "PowerBox"
>
> 💡 **L'IP commence généralement par** : `192.168.0.x` ou `192.168.1.x`

---

## 📊 Capteurs Créés

L'intégration crée automatiquement **24 entités** :

### Mesures Temps Réel
- `sensor.powerbox_courant` - Courant de charge (A)
- `sensor.powerbox_tension` - Tension (V)
- `sensor.powerbox_puissance` - Puissance (W)
- `sensor.powerbox_energie_session` - Énergie session (kWh)
- `sensor.powerbox_energie_totale` - Énergie totale borne (kWh)
- `sensor.powerbox_puissance_reactive` - Puissance réactive (var)
- `sensor.powerbox_puissance_apparente_reseau` - Puissance apparente réseau (VA)
- `sensor.powerbox_facteur_de_puissance` - Facteur de puissance
- `sensor.powerbox_energie_injectee_totale` - Énergie injectée (kWh)

### Téléinformation (TiC)
- `sensor.powerbox_courant_tic` - Courant Linky phase A (A)
- `sensor.powerbox_puissance_tic` - Puissance Linky (VA)

### Configuration
- `sensor.powerbox_courant_maximum` - Courant max configuré
- `sensor.powerbox_limite_puissance_foyer` - Limite puissance
- `sensor.powerbox_mode_gestion_dynamique` - Mode délestage
- `sensor.powerbox_mode_de_charge` - Mode charge
- `sensor.powerbox_pays` - Pays configuré
- `sensor.powerbox_type_d_installation` - Type installation
- `sensor.powerbox_contrat_v2g` - Contrat V2G
- `sensor.powerbox_profil_reseau` - Profil réseau
- `sensor.powerbox_arret_d_urgence` - Arrêt d'urgence
- `sensor.powerbox_topologie_reseau` - Topologie réseau
- `sensor.powerbox_puissance_de_conception` - Puissance de conception
- `sensor.powerbox_courant_max_hors_ligne` - Courant max hors ligne
- `sensor.powerbox_desequilibre_de_phases` - Déséquilibre de phases

---

> [!NOTE]
> ## 🔋 Tableau de Bord Énergétique
>
> Le capteur **`sensor.powerbox_energie_totale`** est **100% compatible** avec le tableau de bord énergétique de Home Assistant !
>
> Le capteur **`sensor.powerbox_energie_injectee_totale`** peut être utilisé comme source d'énergie **retournée au réseau** (V2G / surplus).
>
> ### Configuration Rapide
>
> [![Open your Home Assistant instance and show your energy configuration panel.](https://my.home-assistant.io/badges/config_energy.svg)](https://my.home-assistant.io/redirect/config_energy/)
>
> ### Configuration Manuelle
>
> 1. **Configuration** → **Tableaux de bord** → **Énergie**
> 2. Cliquez sur **Ajouter une consommation**
> 3. Section **"Consommation individuelle de l'appareil"**
> 4. Sélectionnez : **`sensor.powerbox_energie_totale`**
> 5. **Enregistrer**
>
> Home Assistant calculera automatiquement :
> - ✅ Consommation journalière / mensuelle / annuelle
> - ✅ Graphiques d'évolution temporelle
> - ✅ Coûts énergétiques (si tarif configuré)
> - ✅ Comparaisons périodiques
>
> 💡 **Le capteur utilise le type `total_increasing`** - Home Assistant gère automatiquement les différences pour calculer les consommations périodiques.

---

## 🎨 Exemples d'Utilisation

### Dashboard Lovelace

```yaml
type: vertical-stack
cards:
  - type: entities
    title: ⚡ Charge en Cours
    entities:
      - sensor.powerbox_puissance
      - sensor.powerbox_courant
      - sensor.powerbox_energie_session
  
  - type: gauge
    entity: sensor.powerbox_puissance
    min: 0
    max: 7400
    name: Puissance
    
  - type: history-graph
    title: Historique 24h
    hours_to_show: 24
    entities:
      - sensor.powerbox_puissance
      - sensor.powerbox_courant
```

### Automatisation

```yaml
automation:
  - alias: "Notification début charge"
    trigger:
      - platform: numeric_state
        entity_id: sensor.powerbox_puissance
        above: 500
    action:
      - service: notify.mobile_app
        data:
          message: "Charge démarrée : {{ states('sensor.powerbox_puissance') }}W"
```

---

## 🔧 Dépannage

### La borne n'est pas détectée

1. Vérifiez que l'IP est correcte : `ping 192.168.0.40`
2. Vérifiez les identifiants (nom d'utilisateur : `installer`)
3. Assurez-vous que "Vérifier SSL" est décoché

### Les capteurs restent à 0

C'est normal si **aucune voiture n'est en charge**. Les valeurs s'actualiseront dès qu'une charge démarre.

### Erreur "Cannot connect"

- Vérifiez l'adresse IP de la borne
- Testez : `ping 192.168.0.40`
- Assurez-vous que "Vérifier SSL" est décoché
- Utilisez le script de diagnostic : `python test_connectivity.py`

### Erreur "Invalid credentials"

- Vérifiez le mot de passe (sensible à la casse)
- Nom d'utilisateur par défaut : `installer`

### Problèmes de connexion / Déconnexions

L'intégration gère automatiquement les erreurs temporaires :
- Retry automatique (3 tentatives)
- Conservation des dernières valeurs
- Adaptation de la fréquence en cas de problème

Si la PowerBox est instable, l'intervalle de mise à jour augmente automatiquement pour réduire la charge.

---

## ⚙️ Options et Diagnostics

### Modifier la Configuration

Vous pouvez reconfigurer l'intégration sans la désinstaller :

1. **Configuration** → **Appareils et Services**
2. Cliquez sur **Mobilize PowerBox Verso**
3. Cliquez sur **Configurer**
4. Modifiez le nom ou l'option SSL
5. Enregistrez

### Diagnostics

Pour faciliter le debug, l'intégration fournit des diagnostics détaillés :

1. **Configuration** → **Appareils et Services**
2. Cliquez sur **Mobilize PowerBox Verso**
3. Cliquez sur **Télécharger les diagnostics**
4. Un fichier JSON sera généré avec toutes les informations (identifiants masqués)

Ces diagnostics sont utiles pour signaler un problème sur GitHub.

---

> [!NOTE]
> ## 🌐 API Utilisée
>
> Cette intégration utilise l'**API REST locale** de la PowerBox :
> - `POST /v1.0/auth` - Authentification JWT
> - `GET /v1.0/meters` - Mesures temps réel (4 compteurs)
> - `GET /v1.0/configs` - Configuration système
>
> **✅ Aucune connexion cloud** - Tout fonctionne en **100% local** !  
> **✅ Aucune donnée envoyée** à Mobilize ou des tiers  
> **✅ Contrôle total** de vos données

---

## 🤝 Contribution

Les contributions sont les bienvenues ! Consultez [CONTRIBUTING.md](CONTRIBUTING.md) pour plus de détails.

1. **Fork** le projet
2. Créez une **branche** (`git checkout -b feature/amelioration`)
3. **Commit** vos changements (`git commit -am 'feat: ajout fonctionnalité'`)
4. **Push** vers votre fork (`git push origin feature/amelioration`)
5. Créez une **Pull Request**

---

## 📝 Changelog

Voir [CHANGELOG.md](CHANGELOG.md) pour l'historique complet des versions.

### v1.4.0 (2026-09-28) - ✨ Capteurs étendus
- ✅ +11 capteurs (réactive, apparente, cos φ, énergie injectée, V2G, profil réseau…)
- ✅ Diagnostics HA corrigés
- ✅ 24 capteurs au total

### v1.3.0 (2026-02-18) - 🔧 Stabilité et Résilience
- ✅ Intervalles optimisés (30s au lieu de 10s) - Réduction de 66% de la charge
- ✅ Retry automatique avec backoff progressif (3 tentatives)
- ✅ Conservation des dernières valeurs en cas d'erreur temporaire
- ✅ Adaptation dynamique : mode dégradé automatique si problèmes répétés
- ✅ Timeout augmenté à 20 secondes (plus tolérant)
- ✅ Gestion améliorée des ConnectionResetError
- ✅ Logs plus détaillés pour diagnostic
- ✅ Fermeture propre des sessions HTTP

### v1.2.0 (2026-01-14) - 🏗️ Refactoring Architecture
- ✅ Architecture refactorisée selon les standards Home Assistant
- ✅ Nouveau fichier `coordinator.py` avec coordinateurs séparés
- ✅ Pattern `CoordinatorEntity` standard
- ✅ Logs professionnels structurés
- ✅ Code plus maintenable et modulaire

### v1.1.0 (2026-01-14) - 🎉 Première Release Officielle
- ✅ Configuration via interface graphique (Config Flow)
- ✅ Support multilingue (FR/EN)
- ✅ Prêt pour HACS
- ✅ 13 capteurs (mesures temps réel, TiC, configuration)
- ✅ Aucun identifiant en clair
- ✅ API locale uniquement (aucune connexion cloud)
- ✅ Compatible tableau de bord énergétique

---

## 📄 Licence

Ce projet est sous licence **Apache 2.0** - voir le fichier [LICENSE](LICENSE) pour plus de détails.

---

## 🙏 Remerciements

- **[Communauté Home Assistant HACF](https://forum.hacf.fr/t/interfacer-home-assistant-avec-la-borne-mobilize-powerbox-uno/56726)** - Pour le support et les idées
- **[@audrenfr-rgb](https://github.com/audrenfr-rgb)** - Proposition de capteurs additionnels ([#1](https://github.com/MisterMonk3y/ha-mobilize-powerbox/issues/1))
- **Contributeurs** - Pour les améliorations et corrections
- **Utilisateurs testeurs** - Pour les retours et suggestions
- **Mobilize** - Pour avoir créé la PowerBox ⚡

---

## ⭐ Support du Projet

Si cette intégration vous est utile, vous pouvez me soutenir de plusieurs façons :

- ⭐ **Star le projet** sur GitHub
- 🐛 **Signaler des bugs** ou proposer des fonctionnalités
- 🔄 **Partager** l'intégration avec d'autres utilisateurs
- 📖 **Améliorer la documentation**
- 💬 **Répondre aux questions** d'autres utilisateurs

**Merci à tous ceux qui contribuent au projet ! 💚**
