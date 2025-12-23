import socket
import threading
import signal
import sys
from module_Attribution_sujets_pyqt import init_db, register_user, verifier_identifiants, changer_mot_de_passe, supprimer_compte

# ============================
# Configuration administrateur
# ============================
ADMIN_LOGIN = "admin"
ADMIN_PASSWORD = "admin123"

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
                # CONNEXION SIMPLE (login:mdp)
                # ============================
                elif ":" in message and not message.startswith(("REGISTER:", "CHANGE_PASSWORD:", "DELETE_ACCOUNT:", "CHOIX_SUJETS:", 
                                                                "GET_ALL_SUBJECTS", "GET_ALL_USERS", "ADD_SUBJECT:", 
                                                                "UPDATE_SUBJECT:", "DELETE_SUBJECT:")):
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
    print(f"📁 Base de données : data/base.sqlite")
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