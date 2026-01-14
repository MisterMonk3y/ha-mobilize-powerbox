# Guide de Contribution

Merci de votre intérêt pour contribuer à l'intégration Mobilize PowerBox pour Home Assistant ! 🎉

## 🤝 Comment Contribuer

### Signaler un Bug 🐛

Si vous trouvez un bug, veuillez :

1. Vérifier qu'il n'a pas déjà été signalé dans les [Issues](https://github.com/MisterMonk3y/ha-mobilize-powerbox/issues)
2. Créer une nouvelle issue avec :
   - Un titre clair et descriptif
   - Les étapes pour reproduire le problème
   - Le comportement attendu vs observé
   - Votre version de Home Assistant
   - Les diagnostics de l'intégration (si possible)

### Proposer une Fonctionnalité 💡

Pour proposer une nouvelle fonctionnalité :

1. Vérifiez qu'elle n'a pas déjà été proposée
2. Créez une issue avec le label `enhancement`
3. Décrivez clairement :
   - Le problème que cela résout
   - Comment vous imaginez la solution
   - Des exemples d'utilisation

### Soumettre du Code 🔧

1. **Fork** le projet
2. **Créez une branche** pour votre fonctionnalité :
   ```bash
   git checkout -b feature/ma-super-fonctionnalite
   ```
3. **Committez** vos changements :
   ```bash
   git commit -am 'Ajout de ma super fonctionnalité'
   ```
4. **Pushez** vers votre fork :
   ```bash
   git push origin feature/ma-super-fonctionnalite
   ```
5. **Créez une Pull Request** sur le dépôt principal

## 📝 Standards de Code

### Style Python

- Suivez [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Utilisez des noms de variables explicites
- Commentez le code complexe
- Ajoutez des docstrings pour les fonctions

### Structure des Commits

Utilisez des messages de commit clairs :

```
type(scope): description courte

Description détaillée si nécessaire
```

**Types :**
- `feat`: Nouvelle fonctionnalité
- `fix`: Correction de bug
- `docs`: Documentation
- `style`: Formatage
- `refactor`: Refactorisation
- `test`: Tests
- `chore`: Maintenance

**Exemples :**
```
feat(sensor): ajout capteur température
fix(config): correction validation IP
docs(readme): mise à jour installation
```

## 🧪 Tests

Avant de soumettre une PR :

1. Testez votre code localement
2. Vérifiez qu'il n'y a pas d'erreurs dans les logs Home Assistant
3. Assurez-vous que tous les capteurs fonctionnent

## 📚 Documentation

Si vous ajoutez une fonctionnalité :

1. Mettez à jour le `README.md`
2. Ajoutez des exemples d'utilisation
3. Mettez à jour le `CHANGELOG.md`
4. Ajoutez des traductions (FR/EN) dans `strings.json`

## 🌐 Traductions

Pour ajouter une langue :

1. Créez `translations/[code_langue].json`
2. Traduisez tous les champs de `strings.json`
3. Testez dans Home Assistant

## ⚖️ Licence

En contribuant, vous acceptez que vos contributions soient sous licence Apache 2.0.

## 🙏 Merci !

Chaque contribution, petite ou grande, est appréciée ! 💚
