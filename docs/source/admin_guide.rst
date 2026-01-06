# docs/source/admin_guide.rst
Guide Administrateur
====================

Ce guide est destiné aux administrateurs du système AttributionSujet PyQt.

 Connexion Administrateur
===========================

1. Lancez l'application : ``python admin_interface.py``
   OU
   Connectez-vous depuis l'interface utilisateur avec :
   
   * **Login** : ``admin``
   * **Mot de passe** : ``admin123``

2. L'interface administrateur s'ouvre en plein écran

.. image:: _static/admin_dashboard.png
   :alt: Dashboard administrateur
   :width: 800px

 Tableau de bord
==================

L'interface admin est organisée en onglets :

1. ** Sujets** - Gestion des sujets
2. ** Utilisateurs** - Gestion des stagiaires
3. ** Configuration** - Paramètres système
4. ** Statistiques** - Métriques globales
5. ** Algorithme** - Lancement de l'attribution

Gestion des sujets
==================

### Ajouter un sujet

1. Cliquez sur **" Sujets"**
2. Cliquez sur **" Ajouter"**
3. Remplissez le formulaire :
   
   * **Titre** : Nom du sujet
   * **Description** : Détails du sujet
   * **Capacité max** : Nombre maximum de stagiaires
   * **Date limite** : Date butoir pour les choix
   
4. Cliquez sur **"Ajouter"**

### Modifier un sujet

1. Sélectionnez un sujet dans la table
2. Cliquez sur **" Modifier"**
3. Modifiez les champs nécessaires
4. Cliquez sur **"Enregistrer"**

### Supprimer un sujet

1. Sélectionnez un sujet dans la table
2. Cliquez sur **" Supprimer"**
3. Confirmez la suppression

### Activer/Désactiver un sujet

Dans la modification d'un sujet :
* Cochez **"Sujet actif"** pour l'activer
* Décochez pour le désactiver

Gestion des utilisateurs
========================

### Visualiser les utilisateurs

1. Cliquez sur **" Utilisateurs"**
2. La table affiche tous les stagiaires avec :
   
   * Nom et prénom
   * Login
   * Nombre de choix effectués

### Rafraîchir la liste

Cliquez sur **" Actualiser"** pour mettre à jour.

### Export des données

Pour exporter la liste des utilisateurs :
1. Faites **Ctrl+A** pour tout sélectionner
2. **Ctrl+C** pour copier
3. Collez dans Excel ou un fichier texte

Configuration du système
========================

### Paramètres disponibles

1. **Nombre maximum de choix par personne** :
   
   * Définit combien de choix chaque stagiaire peut faire
   * Valeur recommandée : 3-5
   
2. **Système actif** :
   
   * Quand désactivé, les stagiaires ne peuvent pas faire leurs choix
   * Utile pendant les périodes de maintenance

### Sauvegarder la configuration

1. Modifiez les paramètres
2. Cliquez sur **" Sauvegarder la configuration"**

Algorithme d'attribution
========================

### Pré-requis

Avant de lancer l'attribution :

1. **Vérifiez les dates limites** :
   
   * Au moins un sujet doit avoir sa date limite passée
   * Ou forcez l'attribution si nécessaire
   
2. **Vérifiez les choix** :
   
   * Les stagiaires doivent avoir fait leurs choix
   * Vérifiez dans l'onglet **" Utilisateurs"**
   
3. **Vérifiez les capacités** :
   
   * Les sujets doivent avoir des capacités définies
   * Ajustez si nécessaire

### Lancer l'attribution

1. Allez dans l'onglet **"Algorithme"**
2. Cliquez sur **" Lancer l'attribution"**
3. Confirmez l'action

### Processus d'attribution

L'algorithme fonctionne en 2 phases :

**Phase 1 : Attribution des premiers choix**
   
   * Traite tous les 1ers choix
   * Tirage au sort en cas de surcapacité
   * Crée les listes d'attente

**Phase 2 : Cascade vers les choix suivants**
   
   * Pour les stagiaires sans attribution
   * Cherche dans leurs choix suivants
   * Répète jusqu'à attribution ou épuisement des choix

### Résultats

Après l'attribution :

1. **Les résultats sont automatiquement sauvegardés**
2. **Les stagiaires peuvent consulter leurs résultats**
3. **Les statistiques sont mises à jour**

### Forcer l'attribution

Si la date limite n'est pas passée :
* Vous pouvez forcer l'attribution dans l'algorithme
* Utilisez avec précaution

Statistiques
============

### Statistiques globales

Dans l'onglet **" Statistiques"** :

* **Nombre total d'utilisateurs**
* **Nombre total de sujets**
* **Total des choix effectués**
* **Choix moyens par utilisateur**

### Statistiques avancées

Dans l'onglet **" Algorithme"** :

* **Sujets les plus populaires**
* **Sujets les moins demandés**
* **Taux de satisfaction (1er choix)**
* **Nombre d'attributions vs listes d'attente**

Export des données
==================

### Export manuel

1. **Utilisateurs** : Copiez la table
2. **Sujets** : Copiez la table
3. **Résultats** : Consultez la base de données

### Base de données

La base est dans : ``data/base.sqlite``

Tables disponibles :

.. code-block:: sql

   SELECT * FROM users;           -- Tous les utilisateurs
   SELECT * FROM sujets;          -- Tous les sujets
   SELECT * FROM choix_utilisateurs; -- Tous les choix
   SELECT * FROM resultats_attribution; -- Tous les résultats

Maintenance
===========

### Sauvegarde régulière

1. **Copiez le fichier** ``data/base.sqlite``
2. **Stockez dans un endroit sécurisé**
3. **Planifiez des sauvegardes automatiques**

### Nettoyage de la base

Pour supprimer les anciennes données :

.. code-block:: sql

   -- Supprimer les résultats d'attribution
   DELETE FROM resultats_attribution;
   
   -- Supprimer tous les choix
   DELETE FROM choix_utilisateurs;
   
   -- Réinitialiser les sujets (attention !)
   UPDATE sujets SET actif = 1;

### Logs du serveur

Le serveur affiche les logs en temps réel :

* Connexions/déconnexions
* Requêtes reçues
* Erreurs éventuelles

Dépannage
=========

### "Aucun sujet disponible"

* Ajoutez des sujets dans l'onglet **" Sujets"**
* Activez les sujets existants

### "Aucun utilisateur inscrit"

* Les stagiaires doivent créer leur compte
* OU importez des utilisateurs manuellement dans la base

### "L'attribution a échoué"

* Vérifiez les logs du serveur
* Vérifiez que des choix ont été effectués
* Vérifiez les dates limites

### "Erreur de connexion à la base"

* Vérifiez que le fichier ``data/base.sqlite`` existe
* Vérifiez les permissions
* Redémarrez le serveur

### "Le serveur ne répond pas"

* Vérifiez que le serveur est démarré
* Vérifiez le port 55555
* Vérifiez le firewall

Sécurité
========

### Recommandations

1. **Changez le mot de passe admin par défaut**
   
   .. code-block:: sql
      
      UPDATE users SET password = 'nouveau_mdp_hashé' 
      WHERE login = 'admin';
   
2. **Limitez l'accès au serveur**
   
   * Configurez le firewall
   * Utilisez une IP interne
   
3. **Sauvegardez régulièrement**
   
4. **Monitorer les logs**
   
5. **Mettez à jour régulièrement**

### Audit

Pour auditer l'utilisation :

.. code-block:: sql

   -- Dernières connexions
   SELECT * FROM users ORDER BY id DESC;
   
   -- Choix par utilisateur
   SELECT u.nom, u.prenom, COUNT(c.id) as nb_choix
   FROM users u
   LEFT JOIN choix_utilisateurs c ON u.id = c.user_id
   GROUP BY u.id;
   
   -- Sujets non choisis
   SELECT s.titre, COUNT(c.id) as nb_choix
   FROM sujets s
   LEFT JOIN choix_utilisateurs c ON s.id = c.sujet_id
   GROUP BY s.id
   HAVING nb_choix = 0;

API d'administration
====================

Le serveur répond aux commandes TCP. Voir la **Documentation Technique**
pour les commandes disponibles.

Scripts utiles
==============

### Réinitialisation complète

.. code-block:: bash

   # Arrêter le serveur
   # Supprimer la base
   rm data/base.sqlite
   
   # Redémarrer
   python serveur_tcp_sqlite.py
   # La base sera recréée automatiquement

### Export CSV

.. code-block:: python

   import sqlite3
   import csv
   
   conn = sqlite3.connect('data/base.sqlite')
   
   # Export utilisateurs
   cursor = conn.execute("SELECT * FROM users")
   with open('utilisateurs.csv', 'w', newline='') as f:
       writer = csv.writer(f)
       writer.writerow([i[0] for i in cursor.description])
       writer.writerows(cursor)
   
   conn.close()

Support technique
=================

Pour assistance :

1. **Consultez cette documentation**
2. **Vérifiez les logs du serveur**
3. **Contactez le développeur**
4. **Consultez le code source sur GitHub**