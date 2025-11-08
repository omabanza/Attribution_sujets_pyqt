import sqlite3, os

DB_PATH = os.path.join("data", "base.sqlite")

os.makedirs("data", exist_ok=True)

def init_db():
    conn = sqlite3.connect(DB_PATH)
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
    
    conn.commit()
    conn.close()


def register_user(nom, prenom, login, password):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    try:
        c.execute("INSERT INTO users (nom, prenom, login, password) VALUES (?, ?, ?, ?)",
                  (nom, prenom, login, password))
        conn.commit()
        conn.close()
        return True

    except sqlite3.IntegrityError:
        conn.close()
        return False


def verifier_identifiants(login, password):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("SELECT * FROM users WHERE login=? AND password=?", (login, password))
    row = c.fetchone()

    conn.close()
    return row is not None


def get_subjects():
    # Tu pourras l’utiliser plus tard
    return [
        (1, "Projet Réseau", "Déployer une infra"),
        (2, "Projet Dev", "Créer une application PyQt"),
        (3, "CyberSécurité", "Audit & pentest d'un SI")
    ]
