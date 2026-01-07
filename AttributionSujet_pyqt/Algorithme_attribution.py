"""
Module d'algorithme d'attribution des sujets.

Ce module implémente un algorithme d'attribution des sujets aux utilisateurs basé sur
leurs préférences. Il utilise un système en cascade avec tirage au sort en cas d'égalité
et génère des listes d'attente pour les sujets sur-souscrits.
"""

import random
from datetime import datetime
import sqlite3
from collections import defaultdict
import os

# ============================
# CONFIGURATION DES CHEMINS
# ============================

# Déterminer si on est dans AttributionSujet_pyqt
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)

# Par cette version plus robuste :
if os.path.basename(parent_dir) == "Attribution_sujets_pyqt":
    BASE_DIR = parent_dir
else:
    # Remonter d'un niveau supplémentaire si nécessaire
    grandparent_dir = os.path.dirname(parent_dir)
    if os.path.basename(grandparent_dir) == "Attribution_sujets_pyqt":
        BASE_DIR = grandparent_dir
    else:
        BASE_DIR = current_dir  # Fallback

print(f"[DEBUG] Chemin déterminé: BASE_DIR={BASE_DIR}")

# Définir les chemins
DB_PATH = os.path.join(BASE_DIR, "data", "base.sqlite")
DATA_DIR = os.path.join(BASE_DIR, "data")

# Création du dossier data s'il n'existe pas
os.makedirs(DATA_DIR, exist_ok=True)

print(f"[ALGORITHME] DB_PATH: {DB_PATH}")
print(f"[ALGORITHME] Data dir: {DATA_DIR}")

# Importez votre module existant
import module_Attribution_sujets_pyqt as db_module


class AlgorithmeAttribution:
    """
    Classe principale pour l'algorithme d'attribution des sujets.
    
    Cette classe gère l'attribution des sujets aux utilisateurs en fonction de leurs
    préférences, avec des mécanismes de tirage au sort et de listes d'attente.
    
    Attributes:
        conn (sqlite3.Connection): Connexion à la base de données SQLite
    """
    
    def __init__(self):
        """
        Initialise l'algorithme d'attribution.
        
        Cette méthode initialise la base de données si nécessaire et établit
        une connexion avec la base de données SQLite.
        """
        # Assurez-vous que la base est initialisée
        db_module.init_db()  # Initialise les tables si elles n'existent pas
        self.conn = sqlite3.connect(DB_PATH)
        # Utilise sqlite3.Row pour accéder aux colonnes par nom
        self.conn.row_factory = sqlite3.Row
    
    def get_choix_utilisateurs(self):
        """
        Récupère tous les choix des utilisateurs avec leurs préférences.
        
        Returns:
            list: Liste des choix des utilisateurs avec les informations des
                  utilisateurs et des sujets, triés par ordre de préférence.
                  
        Note:
            Seuls les sujets actifs sont inclus dans la requête.
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 
                u.id as user_id,
                u.nom,
                u.prenom,
                u.login,
                c.sujet_id,
                c.ordre_preference,
                s.titre,
                s.capacite_max,
                s.actif
            FROM choix_utilisateurs c
            JOIN users u ON c.user_id = u.id
            JOIN sujets s ON c.sujet_id = s.id
            WHERE s.actif = 1
            ORDER BY c.ordre_preference
        """)
        return cursor.fetchall()
    
    def get_sujets_disponibles(self):
        """
        Récupère tous les sujets actifs avec leurs capacités.
        
        Returns:
            list: Liste des sujets actifs avec leurs informations principales.
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, titre, capacite_max, actif
            FROM sujets
            WHERE actif = 1
        """)
        return cursor.fetchall()
    
    def attribution_cascade(self):
        """
        Algorithme d'attribution en cascade avec tirage au sort.
        
        L'algorithme fonctionne en deux phases :
        1. Attribution des premiers choix, avec tirage au sort en cas de sur-souscription
        2. Cascade vers les choix suivants pour les utilisateurs non attribués
        
        Returns:
            tuple: (sujets_dict, utilisateurs_dict) où :
                - sujets_dict: Dictionnaire des sujets avec leurs attributions
                - utilisateurs_dict: Dictionnaire des utilisateurs avec leurs choix
        """
        # Récupérer les données
        choix = self.get_choix_utilisateurs()
        sujets = self.get_sujets_disponibles()
        
        # Initialiser les structures de données
        # Structure pour stocker les informations par sujet
        sujets_dict = {sujet['id']: {
            'titre': sujet['titre'],
            'capacite': sujet['capacite_max'],
            'attribues': [],  # Liste des utilisateurs attribués
            'liste_attente': []  # Liste d'attente pour les sujets complets
        } for sujet in sujets}
        
        # Structure pour stocker les informations par utilisateur
        utilisateurs_dict = {}
        
        # Organiser les choix par utilisateur
        for row in choix:
            user_id = row['user_id']
            if user_id not in utilisateurs_dict:
                utilisateurs_dict[user_id] = {
                    'nom': row['nom'],
                    'prenom': row['prenom'],
                    'login': row['login'],
                    'choix': []  # Liste des choix de l'utilisateur
                }
            
            # Ajouter le choix à la liste de l'utilisateur
            utilisateurs_dict[user_id]['choix'].append({
                'sujet_id': row['sujet_id'],
                'ordre': row['ordre_preference'],
                'titre': row['titre']
            })
        
        # Trier les utilisateurs par nombre de choix (priorité à ceux qui ont fait plus de choix)
        utilisateurs_tries = sorted(utilisateurs_dict.items(), 
                                  key=lambda x: len(x[1]['choix']), 
                                  reverse=True)
        
        # Phase 1: Attribution des premiers choix
        print("=== PHASE 1: Attribution des premiers choix ===")
        for user_id, user_data in utilisateurs_tries:
            # Vérifier si l'utilisateur a fait des choix
            if not user_data['choix']:
                continue
                
            # Trier les choix par ordre de préférence (ordre croissant)
            choix_tries = sorted(user_data['choix'], key=lambda x: x['ordre'])
            premier_choix = choix_tries[0]  # Premier choix (ordre 1)
            sujet_id = premier_choix['sujet_id']
            
            if sujet_id in sujets_dict:
                sujet = sujets_dict[sujet_id]
                # Vérifier si le sujet a encore de la place
                if len(sujet['attribues']) < sujet['capacite']:
                    # Place disponible - attribution directe
                    sujet['attribues'].append({
                        'user_id': user_id,
                        'nom': user_data['nom'],
                        'prenom': user_data['prenom'],
                        'ordre_preference': premier_choix['ordre']
                    })
                    print(f"[SUCCES] {user_data['prenom']} {user_data['nom']} -> {premier_choix['titre']} (1er choix)")
                else:
                    # Capacité dépassée - tirage au sort nécessaire
                    print(f"[EGALITE] Capacité dépassée pour {premier_choix['titre']}")
                    # Ajouter le nouveau candidat à la liste des candidats
                    candidats = sujet['attribues'] + [{
                        'user_id': user_id,
                        'nom': user_data['nom'],
                        'prenom': user_data['prenom'],
                        'ordre_preference': premier_choix['ordre']
                    }]
                    
                    # Tirage au sort pour déterminer qui est attribué
                    random.shuffle(candidats)
                    # Les premiers 'capacite' candidats sont attribués
                    sujet['attribues'] = candidats[:sujet['capacite']]
                    # Les autres vont en liste d'attente
                    sujet['liste_attente'] = candidats[sujet['capacite']:]
                    
                    # Vérifier si l'utilisateur est dans la liste d'attente
                    dans_liste_attente = any(u['user_id'] == user_id for u in sujet['liste_attente'])
                    if dans_liste_attente:
                        print(f"[ATTENTE] {user_data['prenom']} {user_data['nom']} -> Liste d'attente pour {premier_choix['titre']}")
        
        # Phase 2: Cascade pour les choix suivants
        print("\n=== PHASE 2: Cascade vers les choix suivants ===")
        for user_id, user_data in utilisateurs_tries:
            # Vérifier si l'utilisateur n'a pas encore de sujet attribué
            # Cette vérification parcourt tous les sujets attribués
            if any(user_id in [u['user_id'] for sujet in sujets_dict.values() for u in sujet['attribues']]):
                continue
            
            # Chercher dans les choix suivants (à partir du 2ème choix)
            choix_tries = sorted(user_data['choix'], key=lambda x: x['ordre'])
            for choix in choix_tries[1:]:  # Ignorer le premier choix déjà traité
                sujet_id = choix['sujet_id']
                
                if sujet_id in sujets_dict:
                    sujet = sujets_dict[sujet_id]
                    # Vérifier si le sujet a encore de la place
                    if len(sujet['attribues']) < sujet['capacite']:
                        # Attribution du choix suivant
                        sujet['attribues'].append({
                            'user_id': user_id,
                            'nom': user_data['nom'],
                            'prenom': user_data['prenom'],
                            'ordre_preference': choix['ordre']
                        })
                        print(f"[SUCCES] {user_data['prenom']} {user_data['nom']} -> {choix['titre']} (choix #{choix['ordre']})")
                        break  # On sort de la boucle une fois attribué
        
        # Sauvegarder les résultats dans la base de données
        self.sauvegarder_resultats(sujets_dict)
        
        return sujets_dict, utilisateurs_dict
    
    def sauvegarder_resultats(self, sujets_dict):
        """
        Sauvegarde les résultats d'attribution dans la base de données.
        
        Args:
            sujets_dict (dict): Dictionnaire contenant les résultats d'attribution
                                par sujet.
                                
        Note:
            Cette méthode crée la table `resultats_attribution` si elle n'existe pas
            et vide les résultats précédents avant d'insérer les nouveaux.
        """
        cursor = self.conn.cursor()
        
        # Vider la table des résultats précédents
        cursor.execute("DELETE FROM resultats_attribution")
        
        # Créer la table si elle n'existe pas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS resultats_attribution (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sujet_id INTEGER,
                user_id INTEGER,
                nom TEXT,
                prenom TEXT,
                ordre_preference INTEGER,
                statut TEXT,
                position_liste_attente INTEGER,
                date_attribution TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (sujet_id) REFERENCES sujets(id),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        # Insérer les résultats
        for sujet_id, sujet_data in sujets_dict.items():
            # Attributions principales
            for i, attribution in enumerate(sujet_data['attribues']):
                cursor.execute("""
                    INSERT INTO resultats_attribution 
                    (sujet_id, user_id, nom, prenom, ordre_preference, statut, position_liste_attente)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    sujet_id,
                    attribution['user_id'],
                    attribution['nom'],
                    attribution['prenom'],
                    attribution['ordre_preference'],
                    'attribue',  # Statut: attribué
                    None  # Pas de position en liste d'attente
                ))
            
            # Liste d'attente
            for i, attente in enumerate(sujet_data['liste_attente']):
                cursor.execute("""
                    INSERT INTO resultats_attribution 
                    (sujet_id, user_id, nom, prenom, ordre_preference, statut, position_liste_attente)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    sujet_id,
                    attente['user_id'],
                    attente['nom'],
                    attente['prenom'],
                    attente['ordre_preference'],
                    'attente',  # Statut: en attente
                    i + 1  # Position dans la liste d'attente (commence à 1)
                ))
        
        self.conn.commit()
        print("[SUCCES] Résultats sauvegardés dans la base de données")
    
    def get_statistiques(self):
        """
        Calcule les statistiques d'attribution.
        
        Returns:
            dict: Dictionnaire contenant diverses statistiques :
                - nb_attributions: Nombre d'utilisateurs ayant un sujet attribué
                - nb_en_attente: Nombre d'utilisateurs en liste d'attente
                - nb_utilisateurs_traites: Nombre d'utilisateurs ayant un résultat
                - nb_total_utilisateurs: Nombre total d'utilisateurs
                - stats_sujets: Statistiques détaillées par sujet
                - moyenne_choix: Nombre moyen de choix par utilisateur
        """
        cursor = self.conn.cursor()
        
        # Statistiques générales
        cursor.execute("SELECT COUNT(*) FROM resultats_attribution WHERE statut = 'attribue'")
        nb_attributions = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM resultats_attribution WHERE statut = 'attente'")
        nb_en_attente = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT user_id) FROM resultats_attribution")
        nb_utilisateurs_traites = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM users")
        nb_total_utilisateurs = cursor.fetchone()[0]
        
        # Sujets les plus/le moins choisis
        cursor.execute("""
            SELECT 
                s.titre,
                COUNT(c.id) as nb_choix,
                s.capacite_max,
                COUNT(CASE WHEN r.statut = 'attribue' THEN 1 END) as nb_attribues,
                COUNT(CASE WHEN r.statut = 'attente' THEN 1 END) as nb_attente
            FROM sujets s
            LEFT JOIN choix_utilisateurs c ON s.id = c.sujet_id
            LEFT JOIN resultats_attribution r ON s.id = r.sujet_id
            WHERE s.actif = 1
            GROUP BY s.id
            ORDER BY nb_choix DESC
        """)
        stats_sujets = cursor.fetchall()
        
        # Nombre moyen de choix par personne
        cursor.execute("""
            SELECT 
                AVG(nb_choix) as moyenne_choix
            FROM (
                SELECT 
                    u.id,
                    COUNT(c.id) as nb_choix
                FROM users u
                LEFT JOIN choix_utilisateurs c ON u.id = c.user_id
                GROUP BY u.id
            )
        """)
        moyenne_choix = cursor.fetchone()[0] or 0
        
        return {
            'nb_attributions': nb_attributions,
            'nb_en_attente': nb_en_attente,
            'nb_utilisateurs_traites': nb_utilisateurs_traites,
            'nb_total_utilisateurs': nb_total_utilisateurs,
            'stats_sujets': stats_sujets,
            'moyenne_choix': round(moyenne_choix, 2)
        }
    
    def close(self):
        """
        Ferme la connexion à la base de données.
        
        Cette méthode doit être appelée lorsque l'objet n'est plus nécessaire
        pour libérer les ressources de la base de données.
        """
        self.conn.close()


def lancer_attribution():
    """
    Fonction principale pour lancer l'attribution.
    
    Cette fonction coordonne l'ensemble du processus d'attribution :
    1. Vérification des conditions préalables (dates limites, choix existants)
    2. Exécution de l'algorithme d'attribution
    3. Sauvegarde des résultats
    4. Affichage des statistiques
    
    Returns:
        tuple: (success, sujets_dict, utilisateurs_dict) où :
            - success: Booléen indiquant si l'attribution a réussi
            - sujets_dict: Dictionnaire des résultats par sujet (si succès)
            - utilisateurs_dict: Dictionnaire des utilisateurs (si succès)
    """
    print("[DEBUT] Lancement de l'algorithme d'attribution...")
    print("=" * 60)
    
    # Initialiser l'algorithme
    algo = AlgorithmeAttribution()
    
    # Vérifier si AU MOINS UN sujet a sa date limite passée
    cursor = algo.conn.cursor()
    
    # DÉBUG : Afficher toutes les dates pour comprendre
    cursor.execute("""
        SELECT titre, date_limite, actif,
               date('now') as aujourdhui,
               julianday(date('now')) - julianday(date_limite) as jours_ecart
        FROM sujets 
        WHERE actif = 1
    """)
    
    dates_info = cursor.fetchall()
    print("\n=== DÉBUG : VÉRIFICATION DES DATES ===")
    for row in dates_info:
        print(f"  * {row['titre']}: date_limite={row['date_limite']}, aujourd'hui={row['aujourdhui']}, écart={row['jours_ecart']} jours")
    
    # Requête corrigée pour vérifier les dates limites
    # Un sujet est éligible si sa date limite est passée ou nulle
    cursor.execute("""
        SELECT COUNT(*) as nb_sujets_eligibles 
        FROM sujets 
        WHERE actif = 1 
        AND (date_limite IS NULL OR date(date_limite) <= date('now'))
    """)
    
    nb_sujets_eligibles = cursor.fetchone()['nb_sujets_eligibles']
    
    # Vérification des dates limites
    if nb_sujets_eligibles == 0:
        print("\n[ATTENTION] Aucun sujet n'a sa date limite passée !")
        print("   L'attribution ne peut être lancée que pour les sujets dont la date limite est atteinte.")
        
        # Informer sur les dates limites des sujets actifs
        cursor.execute("""
            SELECT titre, date_limite, actif
            FROM sujets 
            WHERE actif = 1 
            ORDER BY date_limite
        """)
        sujets_info = cursor.fetchall()
        
        print("\n   Dates limites des sujets actifs :")
        for sujet in sujets_info:
            try:
                date_limite = datetime.strptime(sujet['date_limite'], '%Y-%m-%d')
                aujourdhui = datetime.now()
                statut = "[PASSEE]" if date_limite.date() <= aujourdhui.date() else "[FUTURE]"
                print(f"   * {sujet['titre']} : {sujet['date_limite']} {statut}")
            except:
                print(f"   * {sujet['titre']} : {sujet['date_limite']} (Format invalide)")
        
        # Option pour forcer l'attribution (utile pour les tests)
        reponse = input("\nVoulez-vous forcer l'attribution quand même ? (oui/non): ")
        if reponse.lower() == 'oui':
            print("[FORCAGE] Forçage de l'attribution...")
            # On continue même si les dates ne sont pas passées
            nb_sujets_eligibles = 1
        else:
            algo.close()
            return False, None, None
    
    print(f"\n[SUCCES] {nb_sujets_eligibles} sujet(s) avec date limite passée ou forcée")
    
    # VÉRIFIER D'ABORD SI DES CHOIX EXISTENT
    cursor.execute("SELECT COUNT(*) as nb_choix FROM choix_utilisateurs")
    nb_choix_total = cursor.fetchone()['nb_choix']
    
    if nb_choix_total == 0:
        print("[ERREUR] Aucun choix enregistré par les utilisateurs !")
        print("   Les utilisateurs doivent d'abord sélectionner des sujets.")
        algo.close()
        return False, None, None
    
    print(f"[SUCCES] {nb_choix_total} choix(s) enregistrés par les utilisateurs\n")
    
    try:
        # OPTION : Inclure tous les sujets actifs, indépendamment de la date limite
        cursor.execute("""
            SELECT id, titre, capacite_max, actif, date_limite
            FROM sujets
            WHERE actif = 1
        """)
        sujets_eligibles = cursor.fetchall()
        sujets_eligibles_ids = [s['id'] for s in sujets_eligibles]
        
        print(f"[SUCCES] {len(sujets_eligibles)} sujet(s) actif(s) inclus dans l'attribution")
        
        # DEBUG: Afficher les sujets inclus
        for sujet in sujets_eligibles:
            print(f"   * {sujet['titre']} (ID: {sujet['id']}, Date limite: {sujet['date_limite']})")
        
        # DEBUG: Vérifier les choix pour ces sujets
        cursor.execute(f"""
            SELECT COUNT(*) as nb_choix_eligibles
            FROM choix_utilisateurs
            WHERE sujet_id IN ({','.join(['?']*len(sujets_eligibles_ids))})
        """, sujets_eligibles_ids)
        nb_choix_eligibles = cursor.fetchone()['nb_choix_eligibles']
        
        print(f"[SUCCES] {nb_choix_eligibles} choix pour les sujets éligibles")
        
        # Vérification finale avant lancement
        if nb_choix_eligibles == 0:
            print("[ERREUR] Aucun choix enregistré pour les sujets actifs")
            print("   Les utilisateurs n'ont pas sélectionné de sujets actifs.")
            algo.close()
            return False, None, None
        
        print(f"\n[SUCCES] Lancement de l'attribution...\n")
        
        # Initialisation des structures pour l'attribution
        sujets_dict = {sujet['id']: {
            'titre': sujet['titre'],
            'capacite': sujet['capacite_max'],
            'attribues': [],
            'liste_attente': []
        } for sujet in sujets_eligibles}
        
        utilisateurs_dict = {}
        
        # Récupérer les choix seulement pour les sujets éligibles
        cursor.execute(f"""
            SELECT 
                u.id as user_id,
                u.nom,
                u.prenom,
                u.login,
                c.sujet_id,
                c.ordre_preference,
                s.titre,
                s.capacite_max,
                s.actif
            FROM choix_utilisateurs c
            JOIN users u ON c.user_id = u.id
            JOIN sujets s ON c.sujet_id = s.id
            WHERE s.actif = 1 
            AND s.id IN ({','.join(['?']*len(sujets_eligibles_ids))})
            ORDER BY c.ordre_preference
        """, sujets_eligibles_ids)
        choix = cursor.fetchall()
        
        # Organiser les choix par utilisateur
        for row in choix:
            user_id = row['user_id']
            if user_id not in utilisateurs_dict:
                utilisateurs_dict[user_id] = {
                    'nom': row['nom'],
                    'prenom': row['prenom'],
                    'login': row['login'],
                    'choix': []
                }
            
            utilisateurs_dict[user_id]['choix'].append({
                'sujet_id': row['sujet_id'],
                'ordre': row['ordre_preference'],
                'titre': row['titre']
            })
        
        # Trier les utilisateurs par nombre de choix (priorité à ceux qui ont fait plus de choix)
        utilisateurs_tries = sorted(utilisateurs_dict.items(), 
                                  key=lambda x: len(x[1]['choix']), 
                                  reverse=True)
        
        # Phase 1: Attribution des premiers choix (identique à la méthode attribution_cascade)
        print("=== PHASE 1: Attribution des premiers choix ===")
        for user_id, user_data in utilisateurs_tries:
            if not user_data['choix']:
                continue
                
            choix_tries = sorted(user_data['choix'], key=lambda x: x['ordre'])
            premier_choix = choix_tries[0]
            sujet_id = premier_choix['sujet_id']
            
            if sujet_id in sujets_dict:
                sujet = sujets_dict[sujet_id]
                if len(sujet['attribues']) < sujet['capacite']:
                    sujet['attribues'].append({
                        'user_id': user_id,
                        'nom': user_data['nom'],
                        'prenom': user_data['prenom'],
                        'ordre_preference': premier_choix['ordre']
                    })
                    print(f"[SUCCES] {user_data['prenom']} {user_data['nom']} -> {premier_choix['titre']} (1er choix)")
                else:
                    print(f"[EGALITE] Capacité dépassée pour {premier_choix['titre']}")
                    candidats = sujet['attribues'] + [{
                        'user_id': user_id,
                        'nom': user_data['nom'],
                        'prenom': user_data['prenom'],
                        'ordre_preference': premier_choix['ordre']
                    }]
                    
                    random.shuffle(candidats)
                    sujet['attribues'] = candidats[:sujet['capacite']]
                    sujet['liste_attente'] = candidats[sujet['capacite']:]
                    
                    dans_liste_attente = any(u['user_id'] == user_id for u in sujet['liste_attente'])
                    if dans_liste_attente:
                        print(f"[ATTENTE] {user_data['prenom']} {user_data['nom']} -> Liste d'attente pour {premier_choix['titre']}")
        
        # Phase 2: Cascade pour les choix suivants
        print("\n=== PHASE 2: Cascade vers les choix suivants ===")
        for user_id, user_data in utilisateurs_tries:
            # Vérifier si l'utilisateur n'a pas encore de sujet attribué
            # Modification Ligne 500 : comparaison directe au lieu d'utilisation de 'in'
            if any(user_id == u['user_id'] for sujet in sujets_dict.values() for u in sujet['attribues']):
                continue
            
            choix_tries = sorted(user_data['choix'], key=lambda x: x['ordre'])
            for choix in choix_tries[1:]:
                sujet_id = choix['sujet_id']
                
                if sujet_id in sujets_dict:
                    sujet = sujets_dict[sujet_id]
                    if len(sujet['attribues']) < sujet['capacite']:
                        sujet['attribues'].append({
                            'user_id': user_id,
                            'nom': user_data['nom'],
                            'prenom': user_data['prenom'],
                            'ordre_preference': choix['ordre']
                        })
                        print(f"[SUCCES] {user_data['prenom']} {user_data['nom']} -> {choix['titre']} (choix #{choix['ordre']})")
                        break
        
        # Sauvegarder les résultats dans la base de données
        algo.sauvegarder_resultats(sujets_dict)
        
        # Afficher les résultats
        print("\n" + "=" * 60)
        print("RESULTATS DE L'ATTRIBUTION")
        print("=" * 60)
        
        for sujet_id, sujet_data in sujets_dict.items():
            print(f"\nSujet: {sujet_data['titre']} (Capacité: {sujet_data['capacite']})")
            print("   Attribués :")
            for attrib in sujet_data['attribues']:
                print(f"     * {attrib['prenom']} {attrib['nom']} (Choix #{attrib['ordre_preference']})")
            
            if sujet_data['liste_attente']:
                print("   Liste d'attente :")
                for i, attente in enumerate(sujet_data['liste_attente'], 1):
                    print(f"     {i}. {attente['prenom']} {attente['nom']}")
        
        # Calculer les statistiques
        stats = algo.get_statistiques()
        print("\n" + "=" * 60)
        print("STATISTIQUES")
        print("=" * 60)
        print(f"* Utilisateurs avec attribution : {stats['nb_attributions']}/{stats['nb_total_utilisateurs']}")
        print(f"* Utilisateurs en liste d'attente : {stats['nb_en_attente']}")
        print(f"* Nombre moyen de choix par personne : {stats['moyenne_choix']}")
        
        # Fermer la connexion et retourner les résultats
        algo.close()
        return True, sujets_dict, utilisateurs_dict
        
    except Exception as e:
        # Gestion des erreurs
        print(f"[ERREUR] Erreur lors de l'attribution : {e}")
        import traceback
        traceback.print_exc()
        algo.close()
        return False, None, None


if __name__ == "__main__":
    """
    Point d'entrée pour l'exécution directe du module.
    
    Lorsque ce module est exécuté directement (et non importé), il lance
    l'algorithme d'attribution et affiche les résultats dans la console.
    """
    lancer_attribution()