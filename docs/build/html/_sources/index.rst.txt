# docs/source/index.rst
.. AttributionSujet PyQt documentation master file

==================================
AttributionSujet PyQt - Documentation
==================================

**Système d'attribution automatisée de sujets pour stagiaires**

.. toctree::
   :maxdepth: 2
   :caption:  Guide Utilisateur
   
   user_guide
   admin_guide
   algorithm

.. toctree::
   :maxdepth: 2
   :caption:  Documentation Technique
   
   modules
   api

.. toctree::
   :maxdepth: 2
   :caption:  Référence API
   
   api_admin
   api_algorithm
   api_client
   api_server

 Introduction
===============

**AttributionSujet PyQt** est une application complète de gestion d'attribution de sujets pour stagiaires, développée en Python avec PyQt5.

**Fonctionnalités principales :**

 **Interface utilisateur** (stagiaires) :
   - Connexion sécurisée
   - Consultation des sujets disponibles
   - Classement par ordre de préférence
   - Visualisation des résultats

 **Interface administrateur** :
   - Gestion complète des sujets
   - Gestion des utilisateurs
   - Configuration du système
   - Lancement de l'algorithme d'attribution
   - Statistiques en temps réel

**Système client-serveur** :
   - Communication TCP/IP sécurisée
   - Base de données SQLite
   - Architecture multi-utilisateurs

 **Algorithme d'attribution** :
   - Attribution en cascade
   - Gestion des listes d'attente
   - Tirage au sort en cas d'égalité
   - Sauvegarde des résultats

 Démarrage rapide
===================

1. **Installation :**
   
   .. code-block:: bash
      
      pip install -r requirements.txt

2. **Lancer le serveur :**
   
   .. code-block:: bash
      
      python serveur_tcp_sqlite.py

3. **Lancer l'interface client :**
   
   .. code-block:: bash
      
      python Attribution_sujets_pyqt.py

4. **Lancer l'interface admin :**
   
   Connectez-vous avec : ``admin`` / ``admin123``

 Structure du projet
======================

.. code-block:: text

   AttributionSujet_pyqt/
   ├── AttributionSujet/              # Code source principal
   │   ├── admin_interface.py        # Interface administrateur
   │   ├── Algorithme_attribution.py # Algorithme d'attribution
   │   ├── Attribution_sujets_pyqt.py # Interface utilisateur
   │   ├── module_Attribution_sujets.py # Module principal
   │   ├── resultats_interface.py    # Interface résultats
   │   └── serveur_tcp_sqlite.py     # Serveur TCP
   ├── data/                         # Base de données
   ├── docs/                         # Documentation
   └── requirements.txt              # Dépendances

 Contribution
===============

Pour contribuer au projet :

1. Forkez le dépôt
2. Créez une branche pour votre fonctionnalité
3. Committez vos changements
4. Ouvrez une Pull Request

 Support
==========

- **Email** : orlane.mabanza@etu-univ-poitiers.fr
- **GitHub** : https://github.com/Attribution_sujets_pyqt

Licence
==========

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

.. Indices et tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`