import socket
import threading
import signal
import sys
import sqlite3
from module_Attribution_sujets_pyqt import init_db, register_user, verifier_identifiants, changer_mot_de_passe, supprimer_compte
from module_Attribution_sujets_pyqt import get_resultats_par_utilisateur, get_statistiques_avancees
# ============================
# Configuration administrateur
# ============================
ADMIN_LOGIN = "admin"
ADMIN_PASSWORD = "admin123"
DB_PATH = "data/base.sqlite"  # Ajout du chemin de la base de données

# ============================
# Gestion des clients
# ============================

def gerer_client(conn, addr):
    print(f"\n=== NOUVELLE CONNEXION de {addr} ===")
    try:
        while True:
            try:
                print("Attente de données du client...")
                data = conn.recv(1024)
                if not data:
                    print(f"Client {addr} a fermé la connexion")
                    break

                message = data.decode("utf-8").strip()
                print(f"Message reçu : '{message}'")
                print(f"Longueur : {len(message)} octets")

                # ============================
                # REQUÊTES ADMINISTRATEUR
                # ============================
                
                # Obtenir tous les sujets
                if message == "GET_ALL_SUBJECTS":
                    print(">>> Requête: GET_ALL_SUBJECTS")
                    try:
                        from module_Attribution_sujets_pyqt import get_tous_sujets
                        sujets = get_tous_sujets()
                        # Convertir en chaîne JSON-like
                        response = "SUJETS:" + str(sujets)
                        conn.sendall(response.encode("utf-8"))
                        print(f"<<< Réponse envoyée: SUJETS ({len(sujets)} sujets)")
                    except Exception as e:
                        conn.sendall(f"ERROR:{str(e)}".encode("utf-8"))
                        print(f"<<< Erreur: {e}")
                    continue
                
                # Obtenir tous les utilisateurs
                elif message == "GET_ALL_USERS":
                    print(">>> Requête: GET_ALL_USERS")
                    try:
                        from module_Attribution_sujets_pyqt import get_tous_utilisateurs, get_nb_choix_utilisateur
                        utilisateurs = get_tous_utilisateurs()
                        # Ajouter le nombre de choix pour chaque utilisateur
                        utilisateurs_avec_choix = []
                        for user in utilisateurs:
                            user_id = user[0]
                            nb_choix = get_nb_choix_utilisateur(user_id)
                            # user contient: [id, nom, prenom, login]
                            # Ajouter nb_choix à la fin
                            utilisateurs_avec_choix.append(user + (nb_choix,))
                        response = "UTILISATEURS:" + str(utilisateurs_avec_choix)
                        conn.sendall(response.encode("utf-8"))
                        print(f"<<< Réponse envoyée: UTILISATEURS ({len(utilisateurs)} utilisateurs)")
                    except Exception as e:
                        conn.sendall(f"ERROR:{str(e)}".encode("utf-8"))
                    continue
                
                # Ajouter un sujet
                elif message.startswith("ADD_SUBJECT:"):
                    print(">>> Requête: ADD_SUBJECT")
                    try:
                        from module_Attribution_sujets_pyqt import ajouter_sujet
                        parts = message.split(":", 4)
                        if len(parts) != 5:
                            conn.sendall("FORMAT_INVALIDE".encode("utf-8"))
                            continue
                        _, titre, description, capacite_max, date_limite = parts
                        if ajouter_sujet(titre, description, int(capacite_max), date_limite):
                            conn.sendall("SUBJECT_ADDED".encode("utf-8"))
                            print("<<< Sujet ajouté avec succès")
                        else:
                            conn.sendall("ADD_FAILED".encode("utf-8"))
                    except Exception as e:
                        conn.sendall(f"ERROR:{str(e)}".encode("utf-8"))
                    continue
                
                # Modifier un sujet
                elif message.startswith("UPDATE_SUBJECT:"):
                    print(">>> Requête: UPDATE_SUBJECT")
                    try:
                        from module_Attribution_sujets_pyqt import modifier_sujet
                        parts = message.split(":", 6)
                        if len(parts) != 7:
                            conn.sendall("FORMAT_INVALIDE".encode("utf-8"))
                            continue
                        _, sujet_id, titre, description, capacite_max, date_limite, actif = parts
                        actif_bool = actif.lower() == 'true'
                        if modifier_sujet(int(sujet_id), titre, description, int(capacite_max), date_limite, actif_bool):
                            conn.sendall("SUBJECT_UPDATED".encode("utf-8"))
                        else:
                            conn.sendall("UPDATE_FAILED".encode("utf-8"))
                    except Exception as e:
                        conn.sendall(f"ERROR:{str(e)}".encode("utf-8"))
                    continue
                
                # Supprimer un sujet
                elif message.startswith("DELETE_SUBJECT:"):
                    print(">>> Requête: DELETE_SUBJECT")
                    try:
                        from module_Attribution_sujets_pyqt import supprimer_sujet
                        parts = message.split(":", 1)
                        if len(parts) != 2:
                            conn.sendall("FORMAT_INVALIDE".encode("utf-8"))
                            continue
                        _, sujet_id = parts
                        if supprimer_sujet(int(sujet_id)):
                            conn.sendall("SUBJECT_DELETED".encode("utf-8"))
                        else:
                            conn.sendall("DELETE_FAILED".encode("utf-8"))
                    except Exception as e:
                        conn.sendall(f"ERROR:{str(e)}".encode("utf-8"))
                    continue
                
                # ============================
                # NOUVELLE REQUÊTE POUR STAGIAIRES
                # ============================
                
                # Obtenir les sujets actifs pour les stagiaires
                elif message == "GET_ACTIVE_SUBJECTS":
                    print(">>> Requête: GET_ACTIVE_SUBJECTS (stagiaire)")
                    try:
                        from module_Attribution_sujets_pyqt import get_subjects
                        sujets = get_subjects()  # Déjà filtrés sur actif=1
                        response = "ACTIVE_SUBJECTS:" + str(sujets)
                        conn.sendall(response.encode("utf-8"))
                        print(f"<<< Réponse envoyée: {len(sujets)} sujets actifs")
                    except Exception as e:
                        conn.sendall(f"ERROR:{str(e)}".encode("utf-8"))
                    continue
                
                # ============================
                # REQUÊTES EXISTANTES
                # ============================
                
                # Format : REGISTER:nom:prenom:login:mdp
                elif message.startswith("REGISTER:"):
                    print(">>> Requête: REGISTER")
                    parts = message.split(":", 4)
                    if len(parts) != 5:
                        conn.sendall("FORMAT_INVALIDE".encode("utf-8"))
                        continue
                    _, nom, prenom, login, mdp = parts
                    print(f"   Inscription: {nom} {prenom} ({login})")
                    if register_user(nom, prenom, login, mdp):
                        conn.sendall("INSCRIPTION_OK".encode("utf-8"))
                        print("<<< Inscription réussie")
                    else:
                        conn.sendall("LOGIN_EXISTE".encode("utf-8"))
                        print("<<< Login déjà existant")

                # Format : CHANGE_PASSWORD:login:nouveau_mdp
                elif message.startswith("CHANGE_PASSWORD:"):
                    print(">>> Requête: CHANGE_PASSWORD")
                    parts = message.split(":", 2)
                    if len(parts) != 3:
                        conn.sendall("FORMAT_INVALIDE".encode("utf-8"))
                        continue
                    _, login, nouveau_mdp = parts
                    
                    if changer_mot_de_passe(login, nouveau_mdp):
                        conn.sendall("PASSWORD_CHANGED".encode("utf-8"))
                    else:
                        conn.sendall("CHANGE_FAILED".encode("utf-8"))

                # Format : DELETE_ACCOUNT:login
                elif message.startswith("DELETE_ACCOUNT:"):
                    print(">>> Requête: DELETE_ACCOUNT")
                    parts = message.split(":", 1)
                    if len(parts) != 2:
                        conn.sendall("FORMAT_INVALIDE".encode("utf-8"))
                        continue
                    _, login = parts
                    
                    if supprimer_compte(login):
                        conn.sendall("ACCOUNT_DELETED".encode("utf-8"))
                    else:
                        conn.sendall("DELETE_FAILED".encode("utf-8"))

                # Format : CHOIX_SUJETS:login:id1,id2,id3
                elif message.startswith("CHOIX_SUJETS:"):
                    print(">>> Requête: CHOIX_SUJETS")
                    try:
                        from module_Attribution_sujets_pyqt import enregistrer_choix_sujets
                        parts = message.split(":", 2)
                        if len(parts) != 3:
                            conn.sendall("FORMAT_INVALIDE".encode("utf-8"))
                            continue
                        _, login, sujets_ids_str = parts
                        sujets_ids = [int(id_str) for id_str in sujets_ids_str.split(",") if id_str.strip()]
                        if enregistrer_choix_sujets(login, sujets_ids):
                            conn.sendall("CHOIX_ENREGISTRE".encode("utf-8"))
                        else:
                            conn.sendall("CHOIX_ECHEC".encode("utf-8"))
                    except Exception as e:
                        conn.sendall(f"ERROR:{str(e)}".encode("utf-8"))
                    continue
                
                # ============================
                # NOUVELLES REQUÊTES POUR L'ALGORITHME D'ATTRIBUTION
                # ============================
                
                # Obtenir les résultats pour un stagiaire (MODIFIÉ)
                elif message.startswith("GET_RESULTS:"):
                    print(">>> Requête: GET_RESULTS")
                    try:
                        parts = message.split(":")
                        if len(parts) < 2:
                            conn.sendall("FORMAT_INVALIDE".encode("utf-8"))
                            continue
                            
                        login = parts[1]
                        print(f"   Recherche des résultats pour: {login}")
                        
                        # Utiliser la fonction du module
                        results = get_resultats_par_utilisateur(login)
                        
                        # Vérifier si des résultats existent
                        if not results['attributions'] and not results['attente']:
                            print("   Aucun résultat disponible")
                            conn.sendall("NO_RESULTS".encode("utf-8"))
                        else:
                            response = "RESULTS:" + str(results)
                            conn.sendall(response.encode("utf-8"))
                            print(f"<<< Résultats envoyés: {len(results['attributions'])} attributions, {len(results['attente'])} en attente")
                            
                    except Exception as e:
                        print(f"   Erreur GET_RESULTS: {e}")
                        conn.sendall(f"ERROR:{str(e)}".encode("utf-8"))
                    continue
                
                # Lancer l'algorithme d'attribution (SECTION CORRIGÉE)
                elif message == "RUN_ATTRIBUTION":
                    print(">>> Requête: RUN_ATTRIBUTION")
                    try:
                        from Algorithme_attribution import lancer_attribution
                        # Récupérer le résultat qui est maintenant toujours un tuple
                        success, sujets_dict, utilisateurs_dict = lancer_attribution()
                        
                        if success:
                            conn.sendall("ATTRIBUTION_DONE".encode("utf-8"))
                            print("<<< Attribution effectuée avec succès")
                        else:
                            # Si sujets_dict est None, c'est que la date limite n'est pas passée
                            if sujets_dict is None and utilisateurs_dict is None:
                                conn.sendall("DATE_LIMITE_NON_ATTEINTE".encode("utf-8"))  # CORRECTION ICI
                                print("<<< Date limite non atteinte")
                            else:
                                conn.sendall("ATTRIBUTION_FAILED".encode("utf-8"))
                                print("<<< Échec de l'attribution")
                    except Exception as e:
                        error_msg = f"ERROR:Erreur lors de l'attribution : {str(e)}"
                        conn.sendall(error_msg.encode("utf-8"))
                        print(f"<<< Erreur: {e}")
                    continue
                
                # Obtenir les statistiques avancées (MODIFIÉ)
                elif message == "GET_ADVANCED_STATS":
                    print(">>> Requête: GET_ADVANCED_STATS")
                    try:
                        stats = get_statistiques_avancees()
                        response = "ADVANCED_STATS:" + str(stats)
                        conn.sendall(response.encode("utf-8"))
                        print("<<< Statistiques avancées envoyées")
                    except Exception as e:
                        print(f"   Erreur GET_ADVANCED_STATS: {e}")
                        conn.sendall(f"ERROR:{str(e)}".encode("utf-8"))
                    continue
                    
                # ============================
                # CONNEXION SIMPLE (login:mdp)
                # ============================
                elif ":" in message and not message.startswith(("REGISTER:", "CHANGE_PASSWORD:", "DELETE_ACCOUNT:", "CHOIX_SUJETS:", 
                                                                "GET_ALL_SUBJECTS", "GET_ALL_USERS", "ADD_SUBJECT:", 
                                                                "UPDATE_SUBJECT:", "DELETE_SUBJECT:", "GET_ACTIVE_SUBJECTS",
                                                                "RUN_ATTRIBUTION", "GET_RESULTS:", "GET_ADVANCED_STATS")):
                    login, mdp = message.split(":", 1)
                    
                    print(f">>> TENTATIVE DE CONNEXION: login='{login}', mdp='{mdp}'")
                    
                    # Vérifier si c'est l'admin
                    if login == ADMIN_LOGIN and mdp == ADMIN_PASSWORD:
                        print("   >>> ADMIN détecté")
                        conn.sendall("ADMIN_OK".encode("utf-8"))
                        print("<<< Réponse: ADMIN_OK")
                    else:
                        print("   >>> Vérification des identifiants...")
                        resultat = verifier_identifiants(login, mdp)
                        print(f"   >>> Résultat: {resultat}")
                        
                        if resultat:
                            conn.sendall("OK".encode("utf-8"))  # IMPORTANT: doit être "OK" exactement
                            print("<<< Réponse: OK")
                        else:
                            conn.sendall("NOK".encode("utf-8"))  # Changé de "ERREUR" à "NOK"
                            print("<<< Réponse: NOK")
                
                # Format invalide
                else:
                    print(f">>> Format invalide: '{message}'")
                    conn.sendall("FORMAT_INVALIDE".encode("utf-8"))

            except ConnectionResetError:
                print(f"Connexion réinitialisée par le client {addr}")
                break
            except Exception as e:
                print(f"Erreur lors du traitement du client {addr}: {e}")
                break
    finally:
        print(f"=== DÉCONNEXION de {addr} ===\n")
        try:
            conn.close()
        except Exception:
            pass

# ============================
# NOUVELLES FONCTIONS POUR L'ATTRIBUTION
# ============================

def get_results_for_user(login):
    """Récupère les résultats d'un utilisateur"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Récupérer l'ID utilisateur
    cursor.execute("SELECT id FROM users WHERE login = ?", (login,))
    user_row = cursor.fetchone()
    
    if not user_row:
        return {'attributions': [], 'attente': [], 'statistiques': {}}
    
    user_id = user_row[0]
    
    # Sujets attribués
    cursor.execute("""
        SELECT 
            s.titre,
            s.description,
            r.ordre_preference,
            r.statut,
            r.date_attribution
        FROM resultats_attribution r
        JOIN sujets s ON r.sujet_id = s.id
        WHERE r.user_id = ? AND r.statut = 'attribue'
        ORDER BY r.ordre_preference
    """, (user_id,))
    attributions = cursor.fetchall()
    
    # Sujets en attente
    cursor.execute("""
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
    attente = cursor.fetchall()
    
    # Statistiques personnelles
    cursor.execute("""
        SELECT 
            COUNT(*) as nb_total,
            SUM(CASE WHEN statut = 'attribue' THEN 1 ELSE 0 END) as nb_attribues,
            SUM(CASE WHEN statut = 'attente' THEN 1 ELSE 0 END) as nb_en_attente,
            MIN(CASE WHEN statut = 'attribue' THEN ordre_preference END) as meilleur_choix,
            CASE 
                WHEN SUM(CASE WHEN statut = 'attribue' AND ordre_preference = 1 THEN 1 ELSE 0 END) > 0 
                THEN 1 ELSE 0 
            END as premier_choix_obtenu
        FROM resultats_attribution
        WHERE user_id = ?
    """, (user_id,))
    stats_row = cursor.fetchone()
    
    stats = {
        'nb_choix_total': stats_row['nb_total'] if stats_row else 0,
        'nb_attribues': stats_row['nb_attribues'] if stats_row else 0,
        'nb_en_attente': stats_row['nb_en_attente'] if stats_row else 0,
        'taux_reussite': f"{stats_row['nb_attribues'] / stats_row['nb_total'] * 100:.1f}%" if stats_row and stats_row['nb_total'] > 0 else "0%",
        'meilleur_choix': stats_row['meilleur_choix'] if stats_row else "N/A",
        'premier_choix_obtenu': bool(stats_row['premier_choix_obtenu']) if stats_row else False,
        'position_moyenne': "N/A"  # À calculer si besoin
    }
    
    conn.close()
    
    return {
        'attributions': [list(row) for row in attributions],
        'attente': [list(row) for row in attente],
        'statistiques': stats
    }

def get_advanced_stats():
    """Récupère les statistiques avancées"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Sujets les plus populaires
    cursor.execute("""
        SELECT 
            s.titre,
            COUNT(c.id) as nb_choix
        FROM sujets s
        LEFT JOIN choix_utilisateurs c ON s.id = c.sujet_id
        WHERE s.actif = 1
        GROUP BY s.id
        ORDER BY nb_choix DESC
        LIMIT 3
    """)
    sujets_populaires = cursor.fetchall()
    
    # Sujets les moins demandés
    cursor.execute("""
        SELECT 
            s.titre,
            COUNT(c.id) as nb_choix
        FROM sujets s
        LEFT JOIN choix_utilisateurs c ON s.id = c.sujet_id
        WHERE s.actif = 1
        GROUP BY s.id
        ORDER BY nb_choix ASC
        LIMIT 3
    """)
    sujets_moins_demandes = cursor.fetchall()
    
    # Moyenne de choix
    cursor.execute("""
        SELECT AVG(nb_choix) 
        FROM (
            SELECT COUNT(*) as nb_choix
            FROM choix_utilisateurs
            GROUP BY user_id
        )
    """)
    moyenne_choix_result = cursor.fetchone()
    moyenne_choix = moyenne_choix_result[0] if moyenne_choix_result and moyenne_choix_result[0] else 0
    
    # Taux de satisfaction (1er choix)
    cursor.execute("""
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN ordre_preference = 1 AND statut = 'attribue' THEN 1 ELSE 0 END) as premier_choix
        FROM resultats_attribution
    """)
    taux_row = cursor.fetchone()
    if taux_row and taux_row['total'] > 0:
        taux_satisfaction = f"{taux_row['premier_choix'] / taux_row['total'] * 100:.1f}%"
    else:
        taux_satisfaction = "0%"
    
    conn.close()
    
    return {
        'sujets_populaires': ', '.join([s[0] for s in sujets_populaires]),
        'sujets_moins_demandes': ', '.join([s[0] for s in sujets_moins_demandes]),
        'moyenne_choix': round(moyenne_choix, 2),
        'taux_satisfaction': taux_satisfaction
    }

# ============================
# Fonction principale
# ============================
def main():
    init_db()
    host, port = "127.0.0.1", 55555
    serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serveur.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Handler pour fermer proprement la socket sur SIGINT/SIGTERM
    def _close_and_exit(signum, frame):
        print("\n⚠️ Signal reçu, fermeture du serveur...")
        try:
            serveur.close()
        except Exception:
            pass
        sys.exit(0)

    signal.signal(signal.SIGINT, _close_and_exit)
    signal.signal(signal.SIGTERM, _close_and_exit)

    try:
        serveur.bind((host, port))
    except OSError as e:
        print(f"❌ Impossible de binder {host}:{port} -> {e}")
        print("Vérifie qu'aucun autre processus n'utilise le port.")
        serveur.close()
        return

    serveur.listen(5)
    print(f"✅ Serveur en écoute sur {host}:{port}")
    print(f"🔑 Identifiants administrateur : {ADMIN_LOGIN} / {ADMIN_PASSWORD}")
    print(f"📁 Base de données : {DB_PATH}")
    print("=" * 50)

    try:
        while True:
            try:
                conn, addr = serveur.accept()
                # Démarrer un thread pour chaque client
                threading.Thread(target=gerer_client, args=(conn, addr), daemon=True).start()
            except OSError:
                # socket fermé, sortir proprement
                break
    except KeyboardInterrupt:
        print("\n🛑 Arrêt demandé par l'utilisateur")
    finally:
        try:
            serveur.close()
            print("✅ Serveur fermé proprement")
        except Exception:
            pass

if __name__ == "__main__":
    main()