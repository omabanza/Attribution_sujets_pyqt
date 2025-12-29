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
    """Récupère tous les utilisateurs avec leur nombre de choix"""
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
# ============================
# FONCTIONS POUR LES RÉSULTATS D'ATTRIBUTION
# ============================

def creer_table_resultats():
    """Crée la table des résultats d'attribution si elle n'existe pas"""
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
        print("✅ Table resultats_attribution créée/vérifiée")

def get_resultats_par_utilisateur(login):
    """Récupère tous les résultats d'un utilisateur"""
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
                "✅ Attribué",  # statut formaté
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
            # Calculer l'estimation
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
    """Sauvegarde les résultats d'attribution dans la base"""
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
                        None
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
                        i + 1
                    ))
            
            conn.commit()
            print(f"✅ {c.rowcount} résultats sauvegardés")
            return True
    except Exception as e:
        print(f"❌ Erreur lors de la sauvegarde des résultats: {e}")
        return False

def get_statistiques_avancees():
    """Récupère les statistiques avancées"""
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        
        # Statistiques générales
        c.execute("SELECT COUNT(DISTINCT user_id) FROM resultats_attribution WHERE statut = 'attribue'")
        nb_attribues = c.fetchone()[0]
        
        c.execute("SELECT COUNT(DISTINCT user_id) FROM resultats_attribution WHERE statut = 'attente'")
        nb_en_attente = c.fetchone()[0]
        
        # Sujets les plus populaires
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
        
        # Sujets les moins demandés
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
        
        # Taux de satisfaction (1er choix)
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
creer_table_resultats()