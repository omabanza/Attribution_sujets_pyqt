# docs/source/algorithm.rst
Algorithme d'Attribution
========================

Cette section décrit en détail l'algorithme d'attribution utilisé dans le système.

 Présentation générale
========================

**Algorithme d'attribution en cascade** avec tirage au sort pour les égalités.

Objectifs :
1. **Maximiser** le nombre de stagiaires ayant un sujet
2. **Respecter** les préférences dans la mesure du possible
3. **Gérer** les surcapacités équitablement
4. **Créer** des listes d'attente transparentes

Données d'entrée
===================

### 1. Sujets disponibles

.. code-block:: python

   sujets = [
       {
           'id': 1,
           'titre': 'Projet Réseau',
           'capacite': 3,      # Nombre maximum de stagiaires
           'actif': True
       },
       # ...
   ]

### 2. Choix des utilisateurs

.. code-block:: python

   choix = [
       {
           'user_id': 1,
           'sujet_id': 1,
           'ordre': 1          # 1 = premier choix
       },
       # ...
   ]

### 3. Règles de validation

* **Date limite** : Seuls les sujets dont la date limite est passée sont éligibles
* **Activation** : Seuls les sujets actifs sont considérés
* **Choix uniques** : Un utilisateur ne peut pas choisir le même sujet plusieurs fois

 Algorithme détaillé
======================

Phase 1 : Attribution des premiers choix
----------------------------------------

### Étape 1.1 : Préparation

1. **Trier les utilisateurs** par nombre de choix (priorité à ceux qui ont fait plus de choix)
2. **Pour chaque utilisateur**, prendre son premier choix

### Étape 1.2 : Attribution

Pour chaque premier choix :

1. **Vérifier la capacité** du sujet :
   
   * Si **capacité disponible** → Attribuer
   * Si **capacité dépassée** → Tirage au sort
   
2. **Tirage au sort** (en cas de surcapacité) :
   
   * Mélanger aléatoirement tous les candidats
   * Garder les N premiers (N = capacité)
   * Mettre les autres en liste d'attente

### Étape 1.3 : Liste d'attente

Les utilisateurs non retenus lors du tirage au sort :
* Sont placés en **liste d'attente** pour ce sujet
* Avec une **position** (1 = premier en attente)

Phase 2 : Cascade vers les choix suivants
------------------------------------------

### Étape 2.1 : Identification

Identifier les utilisateurs **sans attribution** après la phase 1.

### Étape 2.2 : Parcours des choix

Pour chaque utilisateur sans attribution :

1. **Parcourir ses choix** dans l'ordre (2ème, 3ème, etc.)
2. Pour chaque choix :
   
   * Vérifier si le sujet a de la **capacité disponible**
   * Si oui → Attribuer et arrêter
   * Si non → Passer au choix suivant
   
3. Si tous les choix sont épuisés → L'utilisateur reste sans attribution

### Étape 2.3 : Fin de cascade

L'algorithme s'arrête quand :
* Tous les utilisateurs ont un sujet
* OU tous les choix ont été examinés

 Sauvegarde des résultats
===========================

### Structure des résultats

.. code-block:: python

   resultats = {
       1: {  # ID sujet
           'titre': 'Projet Réseau',
           'capacite': 3,
           'attribues': [  # Liste des attributions
               {
                   'user_id': 1,
                   'nom': 'Dupont',
                   'prenom': 'Jean',
                   'ordre_preference': 1
               }
           ],
           'liste_attente': [  # Liste d'attente
               {
                   'user_id': 4,
                   'nom': 'Martin',
                   'prenom': 'Luc',
                   'ordre_preference': 1,
                   'position': 1
               }
           ]
       }
   }

### Tables de la base

.. list-table:: Résultats sauvegardés
   :widths: 30 70
   :header-rows: 1
   
   * - Table
     - Contenu
   * - ``resultats_attribution``
     - Tous les résultats
   * - Colonne ``statut``
     - 'attribue' ou 'attente'
   * - Colonne ``position_liste_attente``
     - Position (NULL si attribué)

 Statistiques calculées
=========================

### 1. Métriques globales

.. code-block:: python

   stats = {
       'nb_attributions': 25,           # Nombre total d'attributions
       'nb_en_attente': 10,             # Nombre en liste d'attente
       'nb_utilisateurs_traites': 30,   # Utilisateurs avec résultat
       'nb_total_utilisateurs': 35,     # Total des utilisateurs
       'taux_satisfaction': '73.3%'     # % de 1ers choix obtenus
   }

### 2. Métriques par sujet

Pour chaque sujet :
* **Nombre de choix** reçus
* **Nombre d'attributions** effectuées
* **Taux de remplissage** (attribués / capacité)
* **Taille de la liste d'attente**

### 3. Métriques par utilisateur

Pour chaque utilisateur :
* **Nombre de choix** effectués
* **Ordre du choix obtenu** (1 = premier choix)
* **Statut** (attribué/en attente/sans attribution)
* **Position** dans les listes d'attente

 Analyse de l'algorithme
==========================

### Complexité

* **Temps** : O(U × C) où U = nombre d'utilisateurs, C = nombre de choix moyen
* **Mémoire** : O(S + U) où S = nombre de sujets

### Équité

L'algorithme garantit :

1. **Transparence** : Les règles sont claires et documentées
2. **Équité** : Tirage au sort pour les égalités
3. **Non-discrimination** : Basé uniquement sur les préférences

### Limitations

1. **Date limite** : Nécessite qu'au moins un sujet ait sa date passée
2. **Capacités fixes** : Ne gère pas l'ajustement dynamique des capacités
3. **Choix limités** : Un utilisateur ne peut choisir que N sujets

 Améliorations possibles
==========================

### 1. Algorithme optimisé

Implémenter l'**algorithme hôpital-résident** (Gale-Shapley) pour :

* **Stabilité** : Aucun utilisateur ne préfère un autre sujet attribué
* **Optimum** : Maximise le nombre de préférences satisfaites

### 2. Capacités dynamiques

Permettre aux administrateurs de :
* **Ajuster les capacités** après les choix
* **Créer des groupes** supplémentaires si forte demande

### 3. Contraintes supplémentaires

Ajouter des contraintes comme :
* **Parité** homme/femme dans les groupes
* **Niveaux** mélangés (débutants/avancés)
* **Compétences** spécifiques requises

 Tests et validation
======================

### Scénarios de test

1. **Cas simple** : Plus de places que de demandes
2. **Surcapacité** : Plus de demandes que de places
3. **Choix multiples** : Utilisateurs avec plusieurs préférences
4. **Dates limites** : Mix de sujets éligibles et non éligibles

### Validation

Pour valider l'algorithme :

.. code-block:: python

   def test_algorithme():
       # 1. Préparer les données de test
       # 2. Exécuter l'algorithme
       # 3. Vérifier les invariants :
       #    - Aucun sujet ne dépasse sa capacité
       #    - Aucun utilisateur n'a plusieurs sujets
       #    - Les listes d'attente sont cohérentes
       # 4. Calculer les métriques
       pass

 Exemple complet
==================

### Données d'entrée

.. code-block:: python

   # Sujets
   sujets = [
       {'id': 1, 'titre': 'Réseau', 'capacite': 2},
       {'id': 2, 'titre': 'Dev', 'capacite': 3},
   ]
   
   # Utilisateurs et choix
   utilisateurs = [
       {'id': 1, 'nom': 'Dupont', 'choix': [{'sujet_id': 1, 'ordre': 1}]},
       {'id': 2, 'nom': 'Martin', 'choix': [{'sujet_id': 1, 'ordre': 1}]},
       {'id': 3, 'nom': 'Durand', 'choix': [{'sujet_id': 1, 'ordre': 1}]},
   ]

### Exécution

**Phase 1** :
* Dupont → Réseau (attribué)
* Martin → Réseau (attribué)
* Durand → Réseau (capacité dépassée → tirage au sort)

**Tirage au sort** :
* Position aléatoire : [Durand, Martin, Dupont]
* Garde les 2 premiers : Durand, Martin
* Liste d'attente : Dupont (position 1)

**Phase 2** :
* Dupont (sans attribution) → Pas d'autre choix → reste en attente

### Résultats

.. code-block:: python

   resultats = {
       1: {
           'titre': 'Réseau',
           'attribues': [
               {'user_id': 3, 'nom': 'Durand', 'ordre': 1},
               {'user_id': 2, 'nom': 'Martin', 'ordre': 1}
           ],
           'liste_attente': [
               {'user_id': 1, 'nom': 'Dupont', 'ordre': 1, 'position': 1}
           ]
       }
   }

Utilisation avancée
======================

### API Python

.. code-block:: python

   from Algorithme_attribution import AlgorithmeAttribution
   
   # 1. Initialisation
   algo = AlgorithmeAttribution()
   
   # 2. Récupération des données
   choix = algo.get_choix_utilisateurs()
   sujets = algo.get_sujets_disponibles()
   
   # 3. Exécution
   resultats = algo.attribution_cascade()
   
   # 4. Statistiques
   stats = algo.get_statistiques()

### Personnalisation

Pour adapter l'algorithme :

1. **Modifier la priorité** : Changer l'ordre de traitement des utilisateurs
2. **Ajouter des contraintes** : Implémenter des règles métier supplémentaires
3. **Changer le tirage au sort** : Utiliser une autre méthode d'égalité

### Logs et débogage

L'algorithme produit des logs détaillés :

.. code-block:: text

   === PHASE 1: Attribution des premiers choix ===
   Jean Dupont → Projet Réseau (1er choix)
    Capacité dépassée pour Projet Dev
    Luc Martin → Liste d'attente pour Projet Dev

 Références
=============

### Algorithmes similaires

1. **Gale-Shapley** (1962) : Algorithme des mariages stables
2. **Boston Mechanism** : Utilisé pour les affectations scolaires
3. **DA Algorithm** : Algorithme d'admission différée

### Lectures recommandées

* "Two-Sided Matching: A Study in Game-Theoretic Modeling and Analysis" - Roth & Sotomayor
* "School Choice: A Mechanism Design Approach" - Abdulkadiroğlu & Sönmez

### Code source

* **Fichier principal** : ``Algorithme_attribution.py``
* **Fonction principale** : ``lancer_attribution()``
* **Classe principale** : ``AlgorithmeAttribution``

🛠️ Développement
=================

### Structure du code

.. code-block:: python

   class AlgorithmeAttribution:
       def __init__(self): ...
       def get_choix_utilisateurs(self): ...
       def get_sujets_disponibles(self): ...
       def attribution_cascade(self): ...
       def sauvegarder_resultats(self): ...
       def get_statistiques(self): ...

### Tests unitaires

Pour ajouter des tests :

.. code-block:: python

   import unittest
   
   class TestAlgorithme(unittest.TestCase):
       def test_attribution_simple(self):
           # Test avec données simples
           pass
       
       def test_surcapacite(self):
           # Test avec plus de demandes que de places
           pass

### Contribution

Pour contribuer à l'algorithme :

1. **Forkez** le dépôt
2. **Créez une branche** pour votre amélioration
3. **Écrivez des tests**
4. **Soumettez une Pull Request**