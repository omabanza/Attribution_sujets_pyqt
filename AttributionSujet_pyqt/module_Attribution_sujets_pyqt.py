import sqlite3, os

DB_PATH = os.path.join("data", "base.sqlite")

os.makedirs("data", exist_ok=True)

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        
        c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            prenom TEXT NOT NULL,
            login TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
        """)
    

def register_user(nom, prenom, login, password):
    # use context manager so commit/close are automatic
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

# Add alias expected by other modules (data/mettre_data, etc.)
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

def get_subjects():
    # Tu pourras l’utiliser plus tard
    return [
        (1, "Projet Réseau", "Déployer une infra"),
        (2, "Projet Dev", "Créer une application PyQt"),
        (3, "CyberSécurité", "Audit & pentest d'un SI"),
        # --- LES SUJETS QUI ÉTAIENT DANS FenetreChoixSujets ---
        (100, "IA et Machine Learning", "Créer un modèle prédictif"),
        (101, "Bases de données", "Concevoir un schéma et requêtes"),
        (102, "Web Dev", "Développement d'un site interactif"),

        # celui que tu insérais au milieu
        (999, "Projet Réseaux", "Déployer une infrastructure")
    ]
