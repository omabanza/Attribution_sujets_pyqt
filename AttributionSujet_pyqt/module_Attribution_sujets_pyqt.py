import sqlite3, os
from datetime import datetime

DB_PATH = os.path.join("data", "base.sqlite")

os.makedirs("data", exist_ok=True)

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        
        # Table utilisateurs
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
        
        # Table sujets (configuration)
        c.execute("""
        CREATE TABLE IF NOT EXISTS sujets_config (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titre TEXT NOT NULL,
            description TEXT,
            personnes_max INTEGER DEFAULT 3,
            date_limite TIMESTAMP,
            actif BOOLEAN DEFAULT 1
        )
        """)
        
        # Table choix des stagiaires
        c.execute("""
        CREATE TABLE IF NOT EXISTS choix_sujets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            sujet_id INTEGER,
            ordre_preference INTEGER,
            date_choix TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (sujet_id) REFERENCES sujets_config(id)
        )
        """)
        
        # Table configuration générale
        c.execute("""
        CREATE TABLE IF NOT EXISTS config_generale (
            id INTEGER PRIMARY KEY,
            nb_choix_par_personne INTEGER DEFAULT 3,
            actif BOOLEAN DEFAULT 1
        )
        """)
        
        # Insérer configuration par défaut
        c.execute("INSERT OR IGNORE INTO config_generale (id, nb_choix_par_personne) VALUES (1, 3)")
        
        # Insérer quelques sujets par défaut
        sujets_defaut = [
            ("Projet Réseau", "Déployer une infrastructure réseau complète", 3),
            ("Projet Dev", "Créer une application PyQt avec base de données", 3),
            ("CyberSécurité", "Audit & pentest d'un système d'information", 2),
            ("IA et Machine Learning", "Créer un modèle prédictif avec Python", 3),
            ("Bases de données", "Concevoir un schéma et requêtes avancées", 2),
            ("Web Dev", "Développement d'un site interactif avec Django", 3),
        ]
        
        for titre, desc, max_personnes in sujets_defaut:
            c.execute("""
                INSERT OR IGNORE INTO sujets_config (titre, description, personnes_max)
                VALUES (?, ?, ?)
            """, (titre, desc, max_personnes))
        

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

# ============================
# Fonctions d'administration
# ============================

def est_administrateur(login):
    """Vérifie si l'utilisateur est administrateur"""
    # Pour l'instant, on vérifie juste le login statique
    # Vous pourriez ajouter une colonne 'role' dans la table users
    return login == "admin"

def get_tous_utilisateurs():
    """Récupère tous les utilisateurs"""
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("""
            SELECT id, nom, prenom, login, date_inscription 
            FROM users 
            ORDER BY nom, prenom
        """)
        return c.fetchall()

def ajouter_sujet(titre, description, personnes_max, date_limite):
    """Ajoute un nouveau sujet"""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute("""
                INSERT INTO sujets_config (titre, description, personnes_max, date_limite)
                VALUES (?, ?, ?, ?)
            """, (titre, description, personnes_max, date_limite))
            return True
    except Exception as e:
        print(f"Erreur ajout sujet: {e}")
        return False

def modifier_sujet(sujet_id, titre, description, personnes_max, date_limite, actif):
    """Modifie un sujet existant"""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute("""
                UPDATE sujets_config 
                SET titre = ?, description = ?, personnes_max = ?, 
                    date_limite = ?, actif = ?
                WHERE id = ?
            """, (titre, description, personnes_max, date_limite, actif, sujet_id))
            return c.rowcount > 0
    except Exception as e:
        print(f"Erreur modification sujet: {e}")
        return False

def supprimer_sujet(sujet_id):
    """Supprime un sujet"""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute("DELETE FROM sujets_config WHERE id = ?", (sujet_id,))
            return c.rowcount > 0
    except Exception as e:
        print(f"Erreur suppression sujet: {e}")
        return False

def get_tous_sujets():
    """Récupère tous les sujets"""
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("""
            SELECT id, titre, description, personnes_max, 
                   date_limite, actif 
            FROM sujets_config 
            ORDER BY titre
        """)
        return c.fetchall()

def get_config_generale():
    """Récupère la configuration générale"""
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("SELECT nb_choix_par_personne, actif FROM config_generale WHERE id = 1")
        return c.fetchone()

def update_config_generale(nb_choix_par_personne, actif):
    """Met à jour la configuration générale"""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute("""
                UPDATE config_generale 
                SET nb_choix_par_personne = ?, actif = ?
                WHERE id = 1
            """, (nb_choix_par_personne, actif))
            return True
    except Exception as e:
        print(f"Erreur update config: {e}")
        return False

def enregistrer_choix(user_id, sujets_ids):
    """Enregistre les choix d'un utilisateur"""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            
            # Supprimer les anciens choix
            c.execute("DELETE FROM choix_sujets WHERE user_id = ?", (user_id,))
            
            # Ajouter les nouveaux choix
            for ordre, sujet_id in enumerate(sujets_ids, 1):
                c.execute("""
                    INSERT INTO choix_sujets (user_id, sujet_id, ordre_preference)
                    VALUES (?, ?, ?)
                """, (user_id, sujet_id, ordre))
            
            return True
    except Exception as e:
        print(f"Erreur enregistrement choix: {e}")
        return False

def get_choix_utilisateur(user_id):
    """Récupère les choix d'un utilisateur"""
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("""
            SELECT cs.sujet_id, s.titre, s.description, cs.ordre_preference
            FROM choix_sujets cs
            JOIN sujets_config s ON cs.sujet_id = s.id
            WHERE cs.user_id = ?
            ORDER BY cs.ordre_preference
        """, (user_id,))
        return c.fetchall()

def get_statistiques():
    """Récupère les statistiques"""
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        
        # Sujets les plus/moins choisis
        c.execute("""
            SELECT s.id, s.titre, COUNT(cs.sujet_id) as nb_choix
            FROM sujets_config s
            LEFT JOIN choix_sujets cs ON s.id = cs.sujet_id
            GROUP BY s.id, s.titre
            ORDER BY nb_choix DESC
        """)
        stats_sujets = c.fetchall()
        
        # Nombre moyen de choix par personne
        c.execute("""
            SELECT AVG(nb_choix) 
            FROM (
                SELECT user_id, COUNT(*) as nb_choix
                FROM choix_sujets
                GROUP BY user_id
            )
        """)
        moyenne_choix = c.fetchone()[0] or 0
        
        # Nombre total d'utilisateurs ayant fait des choix
        c.execute("SELECT COUNT(DISTINCT user_id) FROM choix_sujets")
        nb_utilisateurs_choix = c.fetchone()[0]
        
        return {
            'stats_sujets': stats_sujets,
            'moyenne_choix': round(moyenne_choix, 2),
            'nb_utilisateurs_choix': nb_utilisateurs_choix
        }

# Fonction existante maintenue pour compatibilité
def get_subjects():
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("SELECT id, titre, description FROM sujets_config WHERE actif = 1")
        return c.fetchall()