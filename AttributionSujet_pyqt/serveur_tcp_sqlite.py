# ...existing code...
import socket
import threading
import signal
import sys
from module_Attribution_sujets_pyqt import init_db, register_user, verifier_identifiants

# ...existing code...
def gerer_client(conn, addr):
    print(f"Client connecté : {addr}")
    try:
        while True:
            try:
                data = conn.recv(1024)
                if not data:
                    break

                message = data.decode("utf-8").strip()
                print(f"Message reçu : {message}")

                # Format : REGISTER:nom:prenom:login:mdp
                if message.startswith("REGISTER:"):
                    parts = message.split(":", 4)
                    if len(parts) != 5:
                        conn.send("FORMAT_INVALIDE".encode("utf-8"))
                        continue
                    _, nom, prenom, login, mdp = parts
                    if register_user(nom, prenom, login, mdp):
                        conn.send("INSCRIPTION_OK".encode("utf-8"))
                    else:
                        conn.send("LOGIN_EXISTE".encode("utf-8"))

                elif ":" in message:
                    login, mdp = message.split(":", 1)
                    if verifier_identifiants(login, mdp):
                        conn.send("OK".encode("utf-8"))
                    else:
                        conn.send("ERREUR".encode("utf-8"))
                else:
                    conn.send("FORMAT_INVALIDE".encode("utf-8"))

            except ConnectionResetError:
                break
            except Exception as e:
                print("Erreur lors du traitement du client :", e)
                break
    finally:
        print(f"Client déconnecté : {addr}")
        try:
            conn.close()
        except Exception:
            pass

# ...existing code...
def main():
    init_db()
    host, port = "127.0.0.1", 55555
    serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serveur.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Handler pour fermer proprement la socket sur SIGINT/SIGTERM
    def _close_and_exit(signum, frame):
        print("\nSignal reçu, fermeture du serveur...")
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
        print(f"Impossible de binder {host}:{port} -> {e}")
        print("Vérifie qu'aucun autre processus n'utilise le port ou change le port dans le client/serveur.")
        serveur.close()
        return

    serveur.listen(5)
    print(f"✅ Serveur en écoute sur {host}:{port}")

    try:
        while True:
            try:
                conn, addr = serveur.accept()
            except OSError:
                # socket fermé, sortir proprement
                break
        threading.Thread(target=gerer_client, args=(conn, addr), daemon=True).start()
    finally:
        try:
            serveur.close()
        except Exception:
            pass

if __name__ == "__main__":
    main()
# ...existing code...        