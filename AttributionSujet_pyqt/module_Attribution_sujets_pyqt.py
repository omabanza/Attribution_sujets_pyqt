"""
Module de gestion de base de données pour le système d'attribution de sujets.

Ce module gère toutes les opérations de base de données SQLite pour :
- L'initialisation de la base de données
- La gestion des utilisateurs
- La gestion des sujets
- L'enregistrement des choix et préférences
- Le stockage des résultats d'attribution
- Les statistiques et rapports
"""

import sqlite3
import os
from datetime import datetime

# ============================
# CONFIGURATION DES CHEMINS
# ============================

# Déterminer si on est dans AttributionSujet_pyqt
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)

# Si le répertoire parent s'appelle "Attribution_sujets_pyqt", mettre data là
if os.path.basename(parent_dir) == "Attribution_sujets_pyqt":
    BASE_DIR = parent_dir
else:
    BASE_DIR = current_dir  # Fallback

# Définir les chemins
DB_PATH = os.path.join(BASE_DIR, "data", "base.sqlite")
DATA_DIR = os.path.join(BASE_DIR, "data")

# Création du dossier data s'il n'existe pas
os.makedirs(DATA_DIR, exist_ok=True)

print(f"DB_PATH: {DB_PATH}")
print(f"Data dir: {DATA_DIR}")

# ============================
# FONCTIONS DE BASE DE DONNÉES
# ============================

def init_db():
    """
    Initialise la base de données avec toutes les tables nécessaires.
    
    Cette fonction :
    1. Crée les tables si elles n'existent pas
    2. Ajoute des données par défaut
    3. Crée un compte administrateur par défaut
    4. Gère la compatibilité avec les versions antérieures
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Table des utilisateurs (stagières)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            prenom TEXT NOT NULL,
            login TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    
    # Table des sujets (projets)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sujets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titre TEXT NOT NULL,
            description TEXT,
            capacite_max INTEGER DEFAULT 1,
            date_limite DATE,
            actif BOOLEAN DEFAULT 1,
            date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Table des choix des utilisateurs - MODIFIÉE POUR INCLURE L'ORDRE DE PRÉFÉRENCE
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS choix_utilisateurs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            sujet_id INTEGER NOT NULL,
            ordre_preference INTEGER NOT NULL,  -- NOUVELLE COLONNE : 1, 2, 3...
            date_choix TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (sujet_id) REFERENCES sujets(id) ON DELETE CASCADE,
            UNIQUE(user_id, sujet_id)
        )
    ''')
    
    # Ajouter la colonne ordre_preference si elle n'existe pas déjà
    # Ceci permet la compatibilité avec les versions antérieures
    try:
        cursor.execute("ALTER TABLE choix_utilisateurs ADD COLUMN ordre_preference INTEGER DEFAULT 1")
        print(" Colonne 'ordre_preference' ajoutée à la table choix_utilisateurs")
    except sqlite3.OperationalError:
        # La colonne existe déjà, c'est normal
        pass
    
    # Table des résultats d'attribution
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS resultats_attribution (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            sujet_id INTEGER NOT NULL,
            ordre_preference INTEGER NOT NULL,  -- L'ordre initial choisi par l'utilisateur
            statut TEXT NOT NULL,  -- 'attribue', 'attente', 'refuse'
            position_liste_attente INTEGER,  -- Position dans la liste d'attente si statut = 'attente'
            date_attribution TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (sujet_id) REFERENCES sujets(id) ON DELETE CASCADE,
            UNIQUE(user_id, sujet_id)
        )
    ''')
    
    # Insérer des données par défaut si les tables sont vides
    cursor.execute("SELECT COUNT(*) FROM sujets")
    count = cursor.fetchone()[0]
    
    if count == 0:
        sujets_defaut = [
            ("Projet Réseau", "Déployer une infrastructure réseau complète", 3, "2024-12-31"),
            ("Projet Dev", "Créer une application PyQt avec base de données", 3, "2024-12-31"),
            ("Cybersécurité", "Audit & pentest d'un système d'information", 2, "2024-12-31"),
        ]
        
        for titre, desc, capacite, date_limite in sujets_defaut:
            try:
                cursor.execute("""
                    INSERT INTO sujets (titre, description, capacite_max, date_limite)
                    VALUES (?, ?, ?, ?)
                """, (titre, desc, capacite, date_limite))
            except sqlite3.IntegrityError:
                pass  # Ignorer les erreurs d'intégrité (duplicates)
    
    # Vérifier et créer un admin par défaut
    cursor.execute("SELECT COUNT(*) FROM users WHERE login = 'admin'")
    admin_count = cursor.fetchone()[0]
    
    if admin_count == 0:
        try:
            cursor.execute("""
                INSERT INTO users (nom, prenom, login, password)
                VALUES (?, ?, ?, ?)
            """, ("Admin", "System", "admin", "admin123"))
            print("Compte admin créé par défaut")
        except sqlite3.IntegrityError:
            pass  # Le compte existe déjà
    
    conn.commit()
    conn.close()
    
    print("Base de données initialisée avec les tables nécessaires")

# ============================
# FONCTIONS POUR LES SUJETS (ADMIN)
# ============================

def get_tous_sujets():
    """
    Récupère tous les sujets de la base de données.
    
    Returns:
        list: Liste de tuples contenant toutes les informations des sujets
              Format: (id, titre, description, capacite_max, date_limite, actif)
    """
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("""
            SELECT id, titre, description, capacite_max, 
                   date_limite, actif 
            FROM sujets 
            ORDER BY titre
        """)
        return c.fetchall()

def ajouter_sujet(titre, description, capacite_max, date_limite):
    """
    Ajoute un nouveau sujet dans la base de données.
    
    Args:
        titre (str): Titre du sujet
        description (str): Description détaillée du sujet
        capacite_max (int): Nombre maximum d'étudiants pouvant choisir ce sujet
        date_limite (str): Date limite de choix au format 'YYYY-MM-DD'
    
    Returns:
        bool: True si l'ajout a réussi, False sinon
    """
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute("""
                INSERT INTO sujets (titre, description, capacite_max, date_limite)
                VALUES (?, ?, ?, ?)
            """, (titre, description, capacite_max, date_limite))
            return True
    except Exception as e:
        print(f"Erreur lors de l'ajout du sujet: {e}")
        return False

def modifier_sujet(sujet_id, titre, description, capacite_max, date_limite, actif):
    """
    Modifie un sujet existant dans la base de données.
    
    Args:
        sujet_id (int): ID du sujet à modifier
        titre (str): Nouveau titre
        description (str): Nouvelle description
        capacite_max (int): Nouvelle capacité maximale
        date_limite (str): Nouvelle date limite
        actif (bool): Nouveau statut actif/inactif
    
    Returns:
        bool: True si la modification a réussi, False sinon
    """
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute("""
                UPDATE sujets 
                SET titre = ?, description = ?, capacite_max = ?, 
                    date_limite = ?, actif = ?
                WHERE id = ?
            """, (titre, description, capacite_max, date_limite, actif, sujet_id))
            return c.rowcount > 0  # Retourne True si au moins une ligne a été modifiée
    except Exception as e:
        print(f"Erreur lors de la modification du sujet: {e}")
        return False

def supprimer_sujet(sujet_id):
    """
    Supprime un sujet de la base de données.
    
    Args:
        sujet_id (int): ID du sujet à supprimer
    
    Returns:
        bool: True si la suppression a réussi, False sinon
    """
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute("DELETE FROM sujets WHERE id = ?", (sujet_id,))
            return c.rowcount > 0  # Retourne True si au moins une ligne a été supprimée
    except Exception as e:
        print(f"Erreur lors de la suppression du sujet: {e}")
        return False

def get_sujet_par_id(sujet_id):
    """
    Récupère un sujet spécifique par son ID.
    
    Args:
        sujet_id (int): ID du sujet à récupérer
    
    Returns:
        tuple: Tuple contenant toutes les informations du sujet, ou None si non trouvé
    """
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM sujets WHERE id = ?", (sujet_id,))
        return c.fetchone()

def get_tous_utilisateurs():
    """
    Récupère tous les utilisateurs avec leur nombre de choix.
    
    Returns:
        list: Liste de tuples contenant les informations utilisateur et nombre de choix
              Format: (id, nom, prenom, login, nb_choix)
    """
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("""
            SELECT u.id, u.nom, u.prenom, u.login,
                   COUNT(c.id) as nb_choix
            FROM users u
            LEFT JOIN choix_utilisateurs c ON u.id = c.user_id
            GROUP BY u.id
            ORDER BY u.nom, u.prenom
        """)
        return c.fetchall()

def get_nb_choix_utilisateur(user_id):
    """
    Récupère le nombre de choix d'un utilisateur.
    
    Args:
        user_id (int): ID de l'utilisateur
    
    Returns:
        int: Nombre de choix effectués par l'utilisateur
    """
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM choix_utilisateurs WHERE user_id = ?", (user_id,))
        return c.fetchone()[0]

# ============================
# FONCTIONS EXISTANTES (maintenues pour compatibilité)
# ============================

def register_user(nom, prenom, login, password):
    """
    Enregistre un nouvel utilisateur dans la base de données.
    
    Args:
        nom (str): Nom de famille
        prenom (str): Prénom
        login (str): Identifiant unique (email)
        password (str): Mot de passe
    
    Returns:
        bool: True si l'enregistrement a réussi, False sinon (login déjà existant)
    """
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute(
                "INSERT INTO users (nom, prenom, login, password) VALUES (?, ?, ?, ?)",
                (nom, prenom, login, password),
            )
        return True
    except sqlite3.IntegrityError:
        return False  # Login déjà existant

def verifier_identifiants(login, password):
    """
    Vérifie si les identifiants sont valides.
    
    Args:
        login (str): Identifiant de l'utilisateur
        password (str): Mot de passe
    
    Returns:
        bool: True si les identifiants sont valides, False sinon
    """
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("SELECT 1 FROM users WHERE login=? AND password=? LIMIT 1", (login, password))
        row = c.fetchone()
    return row is not None

def login_user(login, password):
    """
    Alias pour verifier_identifiants (maintenu pour compatibilité).
    
    Args:
        login (str): Identifiant de l'utilisateur
        password (str): Mot de passe
    
    Returns:
        bool: True si les identifiants sont valides, False sinon
    """
    return verifier_identifiants(login, password)

def changer_mot_de_passe(login, nouveau_password):
    """
    Change le mot de passe d'un utilisateur.
    
    Args:
        login (str): Identifiant de l'utilisateur
        nouveau_password (str): Nouveau mot de passe
    
    Returns:
        bool: True si le changement a réussi, False sinon
    """
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute(
                "UPDATE users SET password = ? WHERE login = ?",
                (nouveau_password, login)
            )
            if c.rowcount > 0:
                return True
            return False  # Aucun utilisateur trouvé avec ce login
    except Exception as e:
        print(f"Erreur lors du changement de mot de passe: {e}")
        return False

def supprimer_compte(login):
    """
    Supprime définitivement un compte utilisateur.
    
    Args:
        login (str): Identifiant de l'utilisateur à supprimer
    
    Returns:
        bool: True si la suppression a réussi, False sinon
    """
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute("DELETE FROM users WHERE login = ?", (login,))
            if c.rowcount > 0:
                return True
            return False  # Aucun utilisateur trouvé avec ce login
    except Exception as e:
        print(f"Erreur lors de la suppression du compte: {e}")
        return False

def get_subjects():
    """
    Récupère tous les sujets actifs (pour l'interface stagiaire).
    
    Returns:
        list: Liste de tuples contenant les informations des sujets actifs
              Format: (id, titre, description)
    """
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("""
            SELECT id, titre, description 
            FROM sujets 
            WHERE actif = 1
            ORDER BY titre
        """)
        return c.fetchall()

def enregistrer_choix_sujets(login, sujets_ids):
    """
    Enregistre les choix de sujets pour un utilisateur (ancienne méthode avec ordre implicite).
    
    Args:
        login (str): Identifiant de l'utilisateur
        sujets_ids (list): Liste des IDs des sujets choisis (ordre de la liste = ordre de préférence)
    
    Returns:
        bool: True si l'enregistrement a réussi, False sinon
    """
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            
            # Récupérer l'ID de l'utilisateur
            c.execute("SELECT id FROM users WHERE login = ?", (login,))
            user_row = c.fetchone()
            
            if not user_row:
                return False  # Utilisateur non trouvé
                
            user_id = user_row[0]
            
            # Supprimer les anciens choix
            c.execute("DELETE FROM choix_utilisateurs WHERE user_id = ?", (user_id,))
            
            # Ajouter les nouveaux choix avec ordre implicite (1, 2, 3...)
            for ordre, sujet_id in enumerate(sujets_ids, 1):
                c.execute("""
                    INSERT INTO choix_utilisateurs (user_id, sujet_id, ordre_preference)
                    VALUES (?, ?, ?)
                """, (user_id, sujet_id, ordre))
            
            return True
    except Exception as e:
        print(f"Erreur enregistrement choix: {e}")
        return False

def enregistrer_preferences_sujets(login, preferences_dict):
    """
    Enregistre les préférences de sujets pour un utilisateur avec ordres spécifiques.
    
    Args:
        login (str): Identifiant de l'utilisateur
        preferences_dict (dict): Dictionnaire {sujet_id: ordre_preference}
                                Exemple: {1: 3, 2: 1, 3: 2}
    
    Returns:
        bool: True si l'enregistrement a réussi, False sinon
    """
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            
            # Récupérer l'ID de l'utilisateur
            c.execute("SELECT id FROM users WHERE login = ?", (login,))
            user_row = c.fetchone()
            
            if not user_row:
                print(f"Utilisateur {login} non trouvé")
                return False
                
            user_id = user_row[0]
            
            # Supprimer les anciens choix
            c.execute("DELETE FROM choix_utilisateurs WHERE user_id = ?", (user_id,))
            
            # Ajouter les nouveaux choix avec les ordres spécifiés
            for sujet_id, ordre in preferences_dict.items():
                c.execute("""
                    INSERT INTO choix_utilisateurs (user_id, sujet_id, ordre_preference)
                    VALUES (?, ?, ?)
                """, (user_id, sujet_id, ordre))
            
            print(f" Préférences enregistrées pour {login}: {preferences_dict}")
            return True
    except Exception as e:
        print(f" Erreur enregistrement préférences: {e}")
        return False

# ============================
# FONCTIONS POUR LES RÉSULTATS D'ATTRIBUTION
# ============================

def creer_table_resultats():
    """
    Crée la table des résultats d'attribution si elle n'existe pas.
    
    Cette fonction garantit que la table existe avant d'être utilisée.
    """
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("""
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
        print("Table resultats_attribution créée/vérifiée")

def get_resultats_par_utilisateur(login):
    """
    Récupère tous les résultats d'attribution pour un utilisateur spécifique.
    
    Args:
        login (str): Identifiant de l'utilisateur
    
    Returns:
        dict: Dictionnaire contenant:
            - 'attributions': Liste des sujets attribués
            - 'attente': Liste des sujets en attente
            - 'statistiques': Statistiques personnelles de l'utilisateur
    """
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        
        # Récupérer l'ID de l'utilisateur
        c.execute("SELECT id, nom, prenom FROM users WHERE login = ?", (login,))
        user_row = c.fetchone()
        
        if not user_row:
            return {'attributions': [], 'attente': [], 'statistiques': {}}
        
        user_id, nom, prenom = user_row
        
        # Vérifier si des résultats existent
        c.execute("SELECT COUNT(*) FROM resultats_attribution")
        if c.fetchone()[0] == 0:
            return {'attributions': [], 'attente': [], 'statistiques': {}}
        
        # Sujets attribués
        c.execute("""
            SELECT 
                s.titre,
                s.description,
                r.ordre_preference,
                r.statut,
                strftime('%d/%m/%Y %H:%M', r.date_attribution) as date_formatee
            FROM resultats_attribution r
            JOIN sujets s ON r.sujet_id = s.id
            WHERE r.user_id = ? AND r.statut = 'attribue'
            ORDER BY r.ordre_preference
        """, (user_id,))
        
        attributions = []
        for row in c.fetchall():
            attributions.append([
                row[0],  # titre
                row[1] or "Pas de description",  # description
                row[2],  # ordre_preference
                " Attribué",  # statut formaté
                row[4]   # date
            ])
        
        # Sujets en attente
        c.execute("""
            SELECT 
                s.titre,
                s.description,
                r.ordre_preference,
                r.position_liste_attente,
                s.capacite_max
            FROM resultats_attribution r
            JOIN sujets s ON r.sujet_id = s.id
            WHERE r.user_id = ? AND r.statut = 'attente'
            ORDER BY r.position_liste_attente
        """, (user_id,))
        
        attente = []
        for row in c.fetchall():
            # Calculer l'estimation de chances en fonction de la position
            position = row[3]
            capacite = row[4]
            if position <= capacite:
                estimation = "Chance élevée"
            elif position <= capacite * 2:
                estimation = "Chance moyenne"
            else:
                estimation = "Chance faible"
            
            attente.append([
                row[0],  # titre
                row[1] or "Pas de description",  # description
                row[2],  # ordre_preference
                row[3],  # position
                row[4],  # capacite_max
                estimation
            ])
        
        # Statistiques personnelles
        c.execute("""
            SELECT 
                COUNT(*) as nb_total,
                SUM(CASE WHEN statut = 'attribue' THEN 1 ELSE 0 END) as nb_attribues,
                SUM(CASE WHEN statut = 'attente' THEN 1 ELSE 0 END) as nb_en_attente,
                MIN(CASE WHEN statut = 'attribue' THEN ordre_preference END) as meilleur_choix
            FROM resultats_attribution
            WHERE user_id = ?
        """, (user_id,))
        stats_row = c.fetchone()
        
        c.execute("""
            SELECT COUNT(*) as premier_choix
            FROM resultats_attribution
            WHERE user_id = ? AND statut = 'attribue' AND ordre_preference = 1
        """, (user_id,))
        premier_row = c.fetchone()
        
        # Calcul des statistiques
        nb_total = stats_row[0] if stats_row else 0
        nb_attribues = stats_row[1] if stats_row else 0
        nb_en_attente = stats_row[2] if stats_row else 0
        meilleur_choix = stats_row[3] if stats_row and stats_row[3] else "N/A"
        premier_choix_obtenu = bool(premier_row and premier_row[0] > 0)
        
        # Calcul du taux de réussite
        taux_reussite = f"{(nb_attribues / nb_total * 100):.1f}%" if nb_total > 0 else "0%"
        
        stats = {
            'nb_choix_total': nb_total,
            'nb_attribues': nb_attribues,
            'nb_en_attente': nb_en_attente,
            'taux_reussite': taux_reussite,
            'meilleur_choix': meilleur_choix,
            'premier_choix_obtenu': premier_choix_obtenu,
            'position_moyenne': "N/A"
        }
        
        return {
            'attributions': attributions,
            'attente': attente,
            'statistiques': stats
        }

def sauvegarder_resultats(attributions, listes_attente):
    """
    Sauvegarde les résultats d'attribution dans la base de données.
    
    Args:
        attributions (dict): Dictionnaire des attributions par sujet
                           Format: {sujet_id: {'attribues': [list_of_users]}}
        listes_attente (dict): Dictionnaire des listes d'attente par sujet
                              Format: {sujet_id: [list_of_users_in_waiting]}
    
    Returns:
        bool: True si la sauvegarde a réussi, False sinon
    """
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            
            # Vider la table des anciens résultats
            c.execute("DELETE FROM resultats_attribution")
            
            # Insérer les attributions
            for sujet_id, sujet_data in attributions.items():
                for i, attribution in enumerate(sujet_data['attribues']):
                    c.execute("""
                        INSERT INTO resultats_attribution 
                        (sujet_id, user_id, nom, prenom, ordre_preference, statut, position_liste_attente)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        sujet_id,
                        attribution['user_id'],
                        attribution['nom'],
                        attribution['prenom'],
                        attribution['ordre_preference'],
                        'attribue',
                        None  # Pas de position en liste d'attente pour les attribués
                    ))
            
            # Insérer les listes d'attente
            for sujet_id, liste_attente in listes_attente.items():
                for i, attente in enumerate(liste_attente):
                    c.execute("""
                        INSERT INTO resultats_attribution 
                        (sujet_id, user_id, nom, prenom, ordre_preference, statut, position_liste_attente)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        sujet_id,
                        attente['user_id'],
                        attente['nom'],
                        attente['prenom'],
                        attente['ordre_preference'],
                        'attente',
                        i + 1  # Position commence à 1
                    ))
            
            conn.commit()
            print(f" {c.rowcount} résultats sauvegardés")
            return True
    except Exception as e:
        print(f" Erreur lors de la sauvegarde des résultats: {e}")
        return False

def get_statistiques_avancees():
    """
    Récupère les statistiques avancées sur l'attribution.
    
    Returns:
        dict: Dictionnaire contenant diverses statistiques :
            - 'nb_attribues': Nombre d'utilisateurs ayant reçu une attribution
            - 'nb_en_attente': Nombre d'utilisateurs en liste d'attente
            - 'sujets_populaires': Liste des sujets les plus choisis
            - 'sujets_moins_demandes': Liste des sujets les moins choisis
            - 'moyenne_choix': Nombre moyen de choix par utilisateur
            - 'taux_satisfaction': Pourcentage d'utilisateurs ayant obtenu leur premier choix
    """
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        
        # Statistiques générales
        c.execute("SELECT COUNT(DISTINCT user_id) FROM resultats_attribution WHERE statut = 'attribue'")
        nb_attribues = c.fetchone()[0]
        
        c.execute("SELECT COUNT(DISTINCT user_id) FROM resultats_attribution WHERE statut = 'attente'")
        nb_en_attente = c.fetchone()[0]
        
        # Sujets les plus populaires (top 3)
        c.execute("""
            SELECT 
                s.titre,
                COUNT(r.id) as nb_choix
            FROM sujets s
            LEFT JOIN resultats_attribution r ON s.id = r.sujet_id
            WHERE s.actif = 1
            GROUP BY s.id
            ORDER BY nb_choix DESC
            LIMIT 3
        """)
        sujets_populaires = c.fetchall()
        
        # Sujets les moins demandés (bottom 3)
        c.execute("""
            SELECT 
                s.titre,
                COUNT(r.id) as nb_choix
            FROM sujets s
            LEFT JOIN resultats_attribution r ON s.id = r.sujet_id
            WHERE s.actif = 1
            GROUP BY s.id
            ORDER BY nb_choix ASC
            LIMIT 3
        """)
        sujets_moins_demandes = c.fetchall()
        
        # Nombre moyen de choix par personne
        c.execute("""
            SELECT AVG(nb_choix) 
            FROM (
                SELECT COUNT(*) as nb_choix
                FROM choix_utilisateurs
                GROUP BY user_id
            )
        """)
        moyenne_choix = c.fetchone()[0] or 0
        
        # Taux de satisfaction (1er choix obtenu)
        c.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN ordre_preference = 1 AND statut = 'attribue' THEN 1 ELSE 0 END) as premier_choix
            FROM resultats_attribution
        """)
        taux_row = c.fetchone()
        taux_satisfaction = f"{(taux_row[1] / taux_row[0] * 100):.1f}%" if taux_row and taux_row[0] > 0 else "0%"
        
        return {
            'nb_attribues': nb_attribues,
            'nb_en_attente': nb_en_attente,
            'sujets_populaires': ', '.join([s[0] for s in sujets_populaires]) if sujets_populaires else "Aucun",
            'sujets_moins_demandes': ', '.join([s[0] for s in sujets_moins_demandes]) if sujets_moins_demandes else "Aucun",
            'moyenne_choix': round(moyenne_choix, 2),
            'taux_satisfaction': taux_satisfaction
        }

# ============================
# INITIALISATION DE LA TABLE DES RÉSULTATS
# ============================
# S'assure que la table des résultats existe au démarrage
creer_table_resultats()