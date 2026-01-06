# docs/source/user_guide.rst
Guide Utilisateur
=================

Bienvenue dans AttributionSujet PyQt ! Ce guide vous explique comment utiliser
l'application en tant que stagiaire.

 Interface Utilisateur
=======================

Connexion
---------

1. Lancez l'application : ``python Attribution_sujets_pyqt.py``
2. Remplissez les champs :
   
   * **Login** : Votre identifiant
   * **Mot de passe** : Votre mot de passe
   
3. Cliquez sur **"Se connecter"**

.. image:: _static/login_screen.png
   :alt: Écran de connexion
   :width: 600px

Création de compte
------------------

Si vous n'avez pas de compte :

1. Cliquez sur **"Créez-en un →"** en bas de l'écran
2. Remplissez le formulaire :
   
   * **Nom** : Votre nom de famille
   * **Prénom** : Votre prénom
   * **Login** : Choisissez un identifiant unique
   * **Mot de passe** : Choisissez un mot de passe sécurisé
   
3. Cliquez sur **"Créer mon compte"**

Choix des sujets
----------------

Une fois connecté, vous verrez la liste des sujets disponibles.

### Comment classer vos préférences :

1. **Pour chaque sujet** : Attribuez un numéro dans la colonne "Ordre de préférence"
   
   * **1** = Votre premier choix
   * **2** = Votre deuxième choix
   * etc.
   
2. **Règles importantes** :
   
   * Chaque numéro doit être unique (pas de doublons)
   * Vous pouvez ne pas classer tous les sujets
   * Les sujets non classés (0) ne seront pas pris en compte

3. **Validation** :
   
   * Cliquez sur **" Valider mes choix"**
   * Confirmez votre sélection

### Exemple :

.. list-table:: Exemple de classement
   :widths: 40 30
   :header-rows: 1
   
   * - Sujet
     - Ordre
   * - Projet Réseau
     - 1
   * - Projet Dev
     - 3
   * - Cybersécurité
     - 2
   * - IA & Machine Learning
     - (vide)

Gestion du compte
-----------------

Cliquez sur le bouton ** VotreLogin** pour accéder au menu :

.. image:: _static/user_menu.png
   :alt: Menu utilisateur
   :width: 300px

Options disponibles :

1. ** Changer le mot de passe**
   
   * Entrez votre ancien mot de passe
   * Choisissez un nouveau mot de passe
   * Confirmez le nouveau mot de passe
   
2. ** Supprimer mon compte**
   
   * Attention : Action irréversible !
   * Toutes vos données seront effacées
   * Demande confirmation par mot de passe

3. ** Rafraîchir la liste**
   
   * Met à jour la liste des sujets
   * Utile si l'admin a ajouté/modifié des sujets

4. **  Déconnexion**
   
   * Retour à l'écran de connexion

Consultation des résultats
--------------------------

### Quand consulter les résultats ?

Les résultats sont disponibles **après** que l'administrateur a lancé l'algorithme d'attribution.

### Comment consulter ?

1. Cliquez sur le bouton **"Résultats"** dans l'interface principale
2. Ou attendez la notification automatique

### Types de résultats :

 **Sujets attribués** :
   
   * Vous avez obtenu le sujet
   * Inclut l'ordre de préférence
   * Date d'attribution

 **Liste d'attente** :
   
   * Position dans la file d'attente
   * Nombre total de places
   * Estimation de vos chances

 **Statistiques personnelles** :
   
   * Nombre de choix effectués
   * Taux de réussite
   * Meilleur choix obtenu
   * 1er choix obtenu ou non

### Exemple de résultats :

.. code-block:: text

    VOS RÉSULTATS D'ATTRIBUTION
   
    SUJETS ATTRIBUÉS (1) :
   • Projet Réseau (Choix #2) - Attribué le 15/12/2024
   
    LISTE D'ATTENTE (1) :
   • Cybersécurité - Position #3 sur 2 places
   
    STATISTIQUES :
   • 3 choix effectués
   • 1 sujet attribué (33% de réussite)
   • Meilleur choix : #2
   • 1er choix : Non obtenu

Fonctionnalités avancées
===========================

Rafraîchissement automatique
----------------------------

L'interface des résultats se rafraîchit automatiquement toutes les **30 secondes**.

Notifications
-------------

* Changement de position dans les listes d'attente
* Nouvelle attribution si votre position devient #1
* Messages d'erreur en cas de problème

Export des résultats
--------------------

Vous pouvez :
1. Prendre une capture d'écran
2. Copier le texte des résultats
3. Imprimer la page (Ctrl+P)

 Dépannage
============

Problèmes courants :

### "Serveur non disponible"
   
   * Vérifiez que le serveur est démarré : ``python serveur_tcp_sqlite.py``
   * Vérifiez votre connexion réseau
   * Contactez l'administrateur

### "Identifiants incorrects"
   
   * Vérifiez votre login/mot de passe
   * Essayez de changer votre mot de passe
   * Contactez l'administrateur pour réinitialisation

### "Aucun sujet disponible"
   
   * L'administrateur n'a pas encore ajouté de sujets
   * Les sujets peuvent être désactivés
   * Attendez que l'admin ajoute des sujets

### "Doublons détectés"
   
   * Vous avez attribué le même numéro à plusieurs sujets
   * Corrigez les numéros pour qu'ils soient uniques
   * Réinitialisez et recommencez

### "Résultats non disponibles"
   
   * L'attribution n'a pas encore été lancée
   * L'algorithme est en cours d'exécution
   * Attendez l'annonce de l'administrateur

 Support
==========

En cas de problème :

1. **Consultez ce guide** pour les solutions courantes
2. **Contactez votre administrateur** pour les problèmes techniques
3. **Signalez les bugs** via le système de votre organisation

 Bonnes pratiques
===================

Pour maximiser vos chances :

1. **Faites plusieurs choix** (au moins 3)
2. **Variez vos préférences** (ne mettez pas que des sujets populaires en premier)
3. **Consultez régulièrement** les résultats
4. **Gardez vos informations** à jour
5. **Choisissez un mot de passe sécurisé**