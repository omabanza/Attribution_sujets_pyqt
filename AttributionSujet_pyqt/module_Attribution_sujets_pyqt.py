import sqlite3
import os

# Nom de la base locale
DB_PATH = os.path.join("data", "base.sqlite")

def init_db():
    """Créer la base et les tables si elles n'existent pas"""
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Création des tables si besoin
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT,
        Prenom TEXT,
        login TEXT UNIQUE,
        password TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS subjects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        description TEXT
    )
    """)

    # Ajouter des sujets de test s’il n’y en a pas
    c.execute("SELECT COUNT(*) FROM subjects")
    if c.fetchone()[0] == 0:
        sujets = [
            ("Projet Réseau", "Configuration d’un routeur Cisco"),
            ("Application Python", "Développement client/serveur"),
            ("Cybersécurité", "Analyse de paquets avec Wireshark")
        ]
        c.executemany("INSERT INTO subjects (title, description) VALUES (?, ?)", sujets)
        conn.commit()
    conn.close()

def register_user(login, password, prenom, nom):
    """Ajoute un utilisateur"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
       c.execute("INSERT INTO users (nom, prenom, login, password) VALUES (?, ?)", (nom, prenom, login, password))
       conn.commit()
       return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def login_user(login, password):
    """Vérifie la connexion"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE login=? AND password=?", (login, password))
    user = c.fetchone()
    conn.close()
    return user is not None

def get_subjects():
    """Retourne la liste des sujets"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM subjects")
    sujets = c.fetchall()
    conn.close()
    return sujets
