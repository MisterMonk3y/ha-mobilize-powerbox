# Changelog

Toutes les modifications notables de ce projet seront documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/),
et ce projet adhère au [Semantic Versioning](https://semver.org/lang/fr/).

---

## [1.3.0] - 2026-02-18

### 🔧 Améliorations de Stabilité

#### Ajouté
- Retry automatique avec backoff progressif (3 tentatives pour l'authentification)
- Conservation des dernières valeurs connues en cas d'erreur temporaire
- Adaptation dynamique de la fréquence de mise à jour selon l'état de la borne
- Mode dégradé automatique (2 minutes) si problèmes répétés
- Compteur d'erreurs consécutives pour détecter l'instabilité
- Gestion spécifique des erreurs `ConnectionResetError`
- Gestion des erreurs `Timeout`
- Méthode `close()` pour fermeture propre des sessions HTTP
- Logs détaillés pour le diagnostic des problèmes

#### Modifié
- Intervalle de mise à jour temps réel : **10s → 30s** (réduction de 66% de la charge)
- Intervalle de mise à jour configuration : **5min → 10min** (réduction de 50% de la charge)
- Timeout des requêtes augmenté : **10s → 20s** (plus tolérant)
- Délai entre les retries augmenté : **2s → 3s** (plus espacé)
- Session HTTP réutilisée avec `Connection: close` pour éviter les problèmes de keep-alive
- Amélioration des messages d'erreur dans les logs

#### Corrigé
- Erreur `Connection reset by peer` causant des échecs d'authentification
- Capteurs devenant "unavailable" lors de micro-coupures
- Surcharge de la PowerBox avec trop de requêtes simultanées
- Absence de gestion des timeouts
- Sessions HTTP non fermées proprement lors du déchargement

### 🔄 Impact

**Charge réseau réduite :**
- Conditions normales : 360 req/h → 120 req/h (-67%)
- Mode dégradé : 360 req/h → 30 req/h (-92%)

**Résilience améliorée :**
- Les erreurs temporaires sont gérées automatiquement
- Les données restent disponibles pendant les déconnexions courtes
- Adaptation automatique pour ne pas surcharger une borne instable

---

## [1.2.0] - 2026-01-14

### 🏗️ Refactoring Architecture

#### Ajouté
- Nouveau fichier `coordinator.py` avec architecture modulaire
- Classe `PowerBoxAPIClient` pour centraliser les appels API
- Classe `PowerBoxRealtimeCoordinator` pour les mesures temps réel
- Classe `PowerBoxConfigCoordinator` pour la configuration
- Dataclass `PowerBoxData` pour structurer les données
- Logs professionnels avec préfixes `[Realtime]` et `[Config]`
- Méthodes utilitaires `get_meter_value()` et `get_config_value()`

#### Modifié
- Refonte complète de `sensor.py` avec pattern `CoordinatorEntity`
- Utilisation de `_handle_coordinator_update()` pour mises à jour automatiques
- Code plus propre et maintenable
- Amélioration de la gestion des erreurs
- Séparation claire des responsabilités

#### Améliorations Techniques
- Pattern standard Home Assistant pour les coordinateurs
- Callbacks optimisés pour les mises à jour d'entités
- Architecture facilitant la maintenance et les évolutions futures
- Conformité aux meilleures pratiques 2024

---

## [1.1.0] - 2026-01-14

### 🎉 Première Release Officielle

#### Ajouté
- Configuration via l'interface graphique (Config Flow)
- Support multilingue (Français / Anglais)
- 13 capteurs :
  - Mesures temps réel : courant, tension, puissance, énergie session, énergie totale
  - Téléinformation Client (TiC/Linky) : courant, puissance
  - Configuration : courant max, limite puissance, modes de charge
- Diagnostics intégrés pour le debug
- Options de reconfiguration sans réinstaller
- Prêt pour HACS
- Compatible tableau de bord énergétique Home Assistant
- Script de test `test_powerbox_api.py`

#### Caractéristiques
- API locale uniquement (aucune connexion cloud)
- Aucun mot de passe en clair dans les fichiers
- Polling optimisé (10s pour temps réel, 5min pour config)
- Support SSL avec option de désactivation
- Device info complet pour Home Assistant

---

## Format des Versions

### Types de Changements

- **Ajouté** : Nouvelles fonctionnalités
- **Modifié** : Changements dans les fonctionnalités existantes
- **Déprécié** : Fonctionnalités qui seront supprimées
- **Supprimé** : Fonctionnalités supprimées
- **Corrigé** : Corrections de bugs
- **Sécurité** : Corrections de vulnérabilités

### Numérotation

- **MAJOR** (1.x.x) : Changements incompatibles avec les versions précédentes
- **MINOR** (x.1.x) : Nouvelles fonctionnalités compatibles
- **PATCH** (x.x.1) : Corrections de bugs compatibles

---

## Liens

- [Projet GitHub](https://github.com/MisterMonk3y/ha-mobilize-powerbox)
- [Signaler un bug](https://github.com/MisterMonk3y/ha-mobilize-powerbox/issues)
- [Guide de contribution](CONTRIBUTING.md)
