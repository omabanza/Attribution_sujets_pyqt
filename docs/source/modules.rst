# docs/source/modules.rst
Modules du Projet
==================

Voici la liste complète des modules Python du projet :

.. toctree::
   :maxdepth: 2

   modules/admin_interface
   modules/algorithm
   modules/client
   modules/server
   modules/database

Module admin_interface
----------------------

.. automodule:: admin_interface
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__

   Description
   ~~~~~~~~~~~
   Interface d'administration complète pour gérer les sujets, utilisateurs,
   et lancer l'algorithme d'attribution.

   Classes principales
   ~~~~~~~~~~~~~~~~~~~
   .. autoclass:: AdminPanel
      :members:
      :special-members: __init__

   Fonctions principales
   ~~~~~~~~~~~~~~~~~~~~~
   .. autofunction:: lancer_attribution

Module Algorithme_attribution
------------------------------

.. automodule:: Algorithme_attribution
   :members:
   :undoc-members:
   :show-inheritance:

   Description
   ~~~~~~~~~~~
   Implémente l'algorithme d'attribution en cascade avec tirage au sort.

   Classes principales
   ~~~~~~~~~~~~~~~~~~~
   .. autoclass:: AlgorithmeAttribution
      :members:
      :special-members: __init__

   Fonctions principales
   ~~~~~~~~~~~~~~~~~~~~~
   .. autofunction:: lancer_attribution

Module Attribution_sujets_pyqt
-------------------------------

.. automodule:: Attribution_sujets_pyqt
   :members:
   :undoc-members:
   :show-inheritance:

   Description
   ~~~~~~~~~~~
   Interface utilisateur principale avec connexion, choix de sujets,
   et gestion des comptes.

   Classes principales
   ~~~~~~~~~~~~~~~~~~~
   .. autoclass:: FenetreConnexion
      :members:
      :special-members: __init__
   
   .. autoclass:: FenetreChoixSujets
      :members:
      :special-members: __init__

Module module_Attribution_sujets_pyqt
--------------------------------------

.. automodule:: module_Attribution_sujets_pyqt
   :members:
   :undoc-members:
   :show-inheritance:

   Description
   ~~~~~~~~~~~
   Module principal contenant les fonctions de base de données
   et les opérations CRUD.

   Fonctions principales
   ~~~~~~~~~~~~~~~~~~~~~
   .. autofunction:: init_db
   .. autofunction:: register_user
   .. autofunction:: verifier_identifiants
   .. autofunction:: enregistrer_preferences_sujets

Module serveur_tcp_sqlite
--------------------------

.. automodule:: serveur_tcp_sqlite
   :members:
   :undoc-members:
   :show-inheritance:

   Description
   ~~~~~~~~~~~
   Serveur TCP qui gère les communications entre clients et base de données.

   Fonctions principales
   ~~~~~~~~~~~~~~~~~~~~~
   .. autofunction:: main
   .. autofunction:: gerer_client

Module resultats_interface
---------------------------

.. automodule:: resultats_interface
   :members:
   :undoc-members:
   :show-inheritance:

   Description
   ~~~~~~~~~~~
   Interface de visualisation des résultats d'attribution.

   Classes principales
   ~~~~~~~~~~~~~~~~~~~
   .. autoclass:: ResultatsInterface
      :members:
      :special-members: __init__