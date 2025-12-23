import sqlite3, os
from datetime import datetime

DB_PATH = os.path.join("data", "base.sqlite")

os.makedirs("data", exist_ok=True)

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        
        # Table utilisateurs (existante)
        c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            prenom TEXT NOT NULL,
            login TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            date_inscription TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Table sujets (NOUVELLE table pour stocker les sujets)
        c.execute("""
        CREATE TABLE IF NOT EXISTS sujets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titre TEXT NOT NULL,
            description TEXT,
            capacite_max INTEGER DEFAULT 3,
            date_limite TEXT,
            actif BOOLEAN DEFAULT 1,
            date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Table choix des stagiaires (pour plus tard)
        c.execute("""
        CREATE TABLE IF NOT EXISTS choix_utilisateurs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            sujet_id INTEGER,
            ordre_preference INTEGER,
            date_choix TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (sujet_id) REFERENCES sujets(id)
        )
        """)
        
        # Insérer quelques sujets par défaut
        sujets_defaut = [
            ("Projet Réseau", "Déployer une infrastructure réseau complète", 3, "2024-12-31"),
            ("Projet Dev", "Créer une application PyQt avec base de données", 3, "2024-12-31"),
            ("Cybersécurité", "Audit & pentest d'un système d'information", 2, "2024-12-31"),
        ]
        
        for titre, desc, capacite, date_limite in sujets_defaut:
            c.execute("""
                INSERT OR IGNORE INTO sujets (titre, description, capacite_max, date_limite)
                VALUES (?, ?, ?, ?)
            """, (titre, desc, capacite, date_limite))
        
        print(f"✅ Base de données initialisée avec succès (tables: users, sujets, choix_utilisateurs)")

# ============================
# NOUVEAU : Initialiser la base de données au démarrage
# ============================
init_db()

# ============================
# FONCTIONS POUR LES SUJETS (ADMIN)
# ============================

def get_tous_sujets():
    """Récupère tous les sujets de la base de données"""
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
    """Ajoute un nouveau sujet dans la base"""
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
    """Modifie un sujet existant"""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute("""
                UPDATE sujets 
                SET titre = ?, description = ?, capacite_max = ?, 
                    date_limite = ?, actif = ?
                WHERE id = ?
            """, (titre, description, capacite_max, date_limite, actif, sujet_id))
            return c.rowcount > 0
    except Exception as e:
        print(f"Erreur lors de la modification du sujet: {e}")
        return False

def supprimer_sujet(sujet_id):
    """Supprime un sujet de la base"""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute("DELETE FROM sujets WHERE id = ?", (sujet_id,))
            return c.rowcount > 0
    except Exception as e:
        print(f"Erreur lors de la suppression du sujet: {e}")
        return False

def get_sujet_par_id(sujet_id):
    """Récupère un sujet spécifique par son ID"""
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM sujets WHERE id = ?", (sujet_id,))
        return c.fetchone()

def get_tous_utilisateurs():
    """Récupère tous les utilisateurs"""
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("""
            SELECT id, nom, prenom, login
            FROM users 
            ORDER BY nom, prenom
        """)
        return c.fetchall()

def get_nb_choix_utilisateur(user_id):
    """Récupère le nombre de choix d'un utilisateur"""
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM choix_utilisateurs WHERE user_id = ?", (user_id,))
        return c.fetchone()[0]

# ============================
# FONCTIONS EXISTANTES (maintenues pour compatibilité)
# ============================

def register_user(nom, prenom, login, password):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute(
                "INSERT INTO users (nom, prenom, login, password) VALUES (?, ?, ?, ?)",
                (nom, prenom, login, password),
            )
        return True
    except sqlite3.IntegrityError:
        return False

def verifier_identifiants(login, password):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("SELECT 1 FROM users WHERE login=? AND password=? LIMIT 1", (login, password))
        row = c.fetchone()
    return row is not None

def login_user(login, password):
    return verifier_identifiants(login, password)

def changer_mot_de_passe(login, nouveau_password):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute(
                "UPDATE users SET password = ? WHERE login = ?",
                (nouveau_password, login)
            )
            if c.rowcount > 0:
                return True
            return False
    except Exception as e:
        print(f"Erreur lors du changement de mot de passe: {e}")
        return False

def supprimer_compte(login):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute("DELETE FROM users WHERE login = ?", (login,))
            if c.rowcount > 0:
                return True
            return False
    except Exception as e:
        print(f"Erreur lors de la suppression du compte: {e}")
        return False

# Fonction existante maintenue pour compatibilité
def get_subjects():
    """Pour l'interface stagiaire - récupère les sujets actifs"""
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
    """Enregistre les choix de sujets pour un utilisateur"""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            
            # Récupérer l'ID de l'utilisateur
            c.execute("SELECT id FROM users WHERE login = ?", (login,))
            user_row = c.fetchone()
            
            if not user_row:
                return False
                
            user_id = user_row[0]
            
            # Supprimer les anciens choix
            c.execute("DELETE FROM choix_utilisateurs WHERE user_id = ?", (user_id,))
            
            # Ajouter les nouveaux choix
            for ordre, sujet_id in enumerate(sujets_ids, 1):
                c.execute("""
                    INSERT INTO choix_utilisateurs (user_id, sujet_id, ordre_preference)
                    VALUES (?, ?, ?)
                """, (user_id, sujet_id, ordre))
            
            return True
    except Exception as e:
        print(f"Erreur enregistrement choix: {e}")
        return False