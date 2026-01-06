# docs/source/api.rst
API Documentation
=================

Cette section documente l'API du système, incluant les protocoles de communication
et les fonctions disponibles.

.. toctree::
   :maxdepth: 2
   
   api_admin
   api_algorithm
   api_client
   api_server

API Administrateur
==================

Protocole de communication
--------------------------

Le serveur répond aux commandes suivantes :

.. list-table:: Commandes Administrateur
   :widths: 30 70
   :header-rows: 1
   
   * - Commande
     - Description
   * - ``GET_ALL_SUBJECTS``
     - Récupère tous les sujets
   * - ``GET_ALL_USERS``
     - Récupère tous les utilisateurs
   * - ``ADD_SUBJECT:titre:description:capacite:date``
     - Ajoute un nouveau sujet
   * - ``UPDATE_SUBJECT:id:titre:description:capacite:date:actif``
     - Modifie un sujet existant
   * - ``DELETE_SUBJECT:id``
     - Supprime un sujet
   * - ``RUN_ATTRIBUTION``
     - Lance l'algorithme d'attribution
   * - ``GET_ADVANCED_STATS``
     - Récupère les statistiques avancées

Réponses du serveur
-------------------

.. list-table:: Réponses Administrateur
   :widths: 30 70
   :header-rows: 1
   
   * - Réponse
     - Signification
   * - ``SUJETS:[liste]``
     - Liste des sujets au format Python
   * - ``UTILISATEURS:[liste]``
     - Liste des utilisateurs
   * - ``SUBJECT_ADDED``
     - Sujet ajouté avec succès
   * - ``SUBJECT_UPDATED``
     - Sujet modifié avec succès
   * - ``SUBJECT_DELETED``
     - Sujet supprimé avec succès
   * - ``ATTRIBUTION_DONE``
     - Attribution terminée
   * - ``ATTRIBUTION_FAILED``
     - Échec de l'attribution
   * - ``ADVANCED_STATS:[dict]``
     - Statistiques avancées

API Client (Stagiaire)
======================

Commandes de connexion
----------------------

.. list-table:: Commandes Client
   :widths: 30 70
   :header-rows: 1
   
   * - Commande
     - Description
   * - ``login:password``
     - Connexion simple
   * - ``REGISTER:nom:prenom:login:mdp``
     - Inscription
   * - ``CHANGE_PASSWORD:login:nouveau_mdp``
     - Changement de mot de passe
   * - ``DELETE_ACCOUNT:login``
     - Suppression de compte
   * - ``GET_ACTIVE_SUBJECTS``
     - Récupère les sujets actifs
   * - ``PREFERENCES:login:id1=ordre1,id2=ordre2,...``
     - Envoie les préférences
   * - ``GET_RESULTS:login``
     - Récupère les résultats

Réponses client
---------------

.. list-table:: Réponses Client
   :widths: 30 70
   :header-rows: 1
   
   * - Réponse
     - Signification
   * - ``OK``
     - Connexion réussie (stagiaire)
   * - ``ADMIN_OK``
     - Connexion réussie (admin)
   * - ``NOK``
     - Identifiants incorrects
   * - ``INSCRIPTION_OK``
     - Inscription réussie
   * - ``LOGIN_EXISTE``
     - Login déjà utilisé
   * - ``PASSWORD_CHANGED``
     - Mot de passe changé
   * - ``ACCOUNT_DELETED``
     - Compte supprimé
   * - ``ACTIVE_SUBJECTS:[liste]``
     - Sujets actifs
   * - ``PREFERENCES_ENREGISTREES``
     - Préférences enregistrées
   * - ``RESULTS:[dict]``
     - Résultats d'attribution
   * - ``NO_RESULTS``
     - Aucun résultat disponible

API Algorithme
==============

Fonctions principales
---------------------

.. autofunction:: Algorithme_attribution.lancer_attribution

.. autoclass:: Algorithme_attribution.AlgorithmeAttribution
   :members:
   :private-members:

Paramètres d'entrée
-------------------

* **Choix utilisateurs** : Liste ordonnée de préférences
* **Sujets disponibles** : Avec capacités maximales
* **Date limite** : Vérification des éligibilités

Sorties
-------

* **Attributions** : Sujets attribués à chaque utilisateur
* **Listes d'attente** : Positions pour les sujets complets
* **Statistiques** : Métriques d'évaluation

Exemple d'utilisation
---------------------

.. code-block:: python

   from Algorithme_attribution import lancer_attribution
   
   success, sujets_dict, utilisateurs_dict = lancer_attribution()
   
   if success:
       print("Attribution réussie")
       for sujet_id, data in sujets_dict.items():
           print(f"Sujet {data['titre']}:")
           for attrib in data['attribues']:
               print(f"  - {attrib['prenom']} {attrib['nom']}")

API Base de données
===================

Fonctions principales
---------------------

.. automodule:: module_Attribution_sujets_pyqt
   :members:
   :undoc-members:

Tables de la base
-----------------

.. list-table:: Tables SQLite
   :widths: 30 70
   :header-rows: 1
   
   * - Table
     - Description
   * - ``users``
     - Informations des utilisateurs
   * - ``sujets``
     - Sujets disponibles
   * - ``choix_utilisateurs``
     - Préférences des utilisateurs
   * - ``resultats_attribution``
     - Résultats d'attribution

Schéma de la base
-----------------

.. code-block:: sql

   -- Table users
   CREATE TABLE users (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       nom TEXT NOT NULL,
       prenom TEXT NOT NULL,
       login TEXT UNIQUE NOT NULL,
       password TEXT NOT NULL
   );
   
   -- Table sujets
   CREATE TABLE sujets (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       titre TEXT NOT NULL,
       description TEXT,
       capacite_max INTEGER DEFAULT 1,
       date_limite DATE,
       actif BOOLEAN DEFAULT 1
   );
   
   -- Table choix_utilisateurs
   CREATE TABLE choix_utilisateurs (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       user_id INTEGER NOT NULL,
       sujet_id INTEGER NOT NULL,
       ordre_preference INTEGER NOT NULL,
       FOREIGN KEY (user_id) REFERENCES users(id),
       FOREIGN KEY (sujet_id) REFERENCES sujets(id),
       UNIQUE(user_id, sujet_id)
   );
   
   -- Table resultats_attribution
   CREATE TABLE resultats_attribution (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       sujet_id INTEGER NOT NULL,
       user_id INTEGER NOT NULL,
       nom TEXT,
       prenom TEXT,
       ordre_preference INTEGER,
       statut TEXT,
       position_liste_attente INTEGER,
       date_attribution TIMESTAMP DEFAULT CURRENT_TIMESTAMP
   );