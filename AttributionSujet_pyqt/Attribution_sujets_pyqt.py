import sys, socket
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPalette, QColor

SERVER_IP = "127.0.0.1"
SERVER_PORT = 55555


# ============================
# Fenêtre Création de Compte
# ============================
class FenetreCreationCompte(QWidget):
    def __init__(self, page_connexion):
        super().__init__()
        self.page_connexion = page_connexion
        self.setWindowTitle("Création de compte")
        self.showMaximized()

        # Style
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(25, 25, 112))
        self.setPalette(palette)

        fontTitre = QFont("Arial", 28, QFont.Bold)
        fontChamp = QFont("Arial", 16)

        titre = QLabel("Création de compte")
        titre.setFont(fontTitre)
        titre.setStyleSheet("color: cyan;")
        titre.setAlignment(Qt.AlignCenter)

        # Champs
        self.nom = QLineEdit(); self.nom.setPlaceholderText("Nom")
        self.prenom = QLineEdit(); self.prenom.setPlaceholderText("Prénom")
        self.login = QLineEdit(); self.login.setPlaceholderText("Email / Login")
        self.mdp = QLineEdit(); self.mdp.setPlaceholderText("Mot de passe"); self.mdp.setEchoMode(QLineEdit.Password)

        for champ in [self.nom, self.prenom, self.login, self.mdp]:
            champ.setFont(fontChamp)

        # Boutons
        btn_creer = QPushButton("Créer mon compte")
        btn_creer.setFont(fontChamp)
        btn_creer.setStyleSheet("background:white; padding:10px; border-radius:10px;")
        btn_creer.clicked.connect(self.creer_compte)

        btn_retour = QPushButton("Retour")
        btn_retour.setFont(fontChamp)
        btn_retour.setStyleSheet("background:white; padding:10px; border-radius:10px;")
        btn_retour.clicked.connect(self.retour)

        layout = QVBoxLayout()
        layout.addStretch()
        layout.addWidget(titre)
        layout.addWidget(self.nom)
        layout.addWidget(self.prenom)
        layout.addWidget(self.login)
        layout.addWidget(self.mdp)
        layout.addWidget(btn_creer)
        layout.addWidget(btn_retour)
        layout.addStretch()
        self.setLayout(layout)

    def retour(self):
        self.close()
        self.page_connexion.show()

    # ...existing code...
   # ...existing code...
    def creer_compte(self):
        nom = self.nom.text().strip()
        prenom = self.prenom.text().strip()
        login = self.login.text().strip()
        mdp = self.mdp.text().strip()

        if not (nom and prenom and login and mdp):
            QMessageBox.warning(self, "Erreur", "Tous les champs sont obligatoires.")
            return

        try:
            client = socket.socket()
            client.connect((SERVER_IP, SERVER_PORT))
            client.send(f"REGISTER:{nom}:{prenom}:{login}:{mdp}".encode())
            reponse = client.recv(1024).decode()
            client.close()

            if reponse == "INSCRIPTION_OK":
                QMessageBox.information(self, "OK", "Compte créé ✅")
                # Ne pas revenir automatiquement à la page de connexion :
                # on laisse l'utilisateur sur le formulaire (ou on vide les champs)
                self.nom.clear()
                self.prenom.clear()
                self.login.clear()
                self.mdp.clear()
                # Pré-remplir le login sur la page de connexion si disponible
                try:
                    self.page_connexion.login.setText(login)
                except Exception:
                    pass
            elif reponse == "LOGIN_EXISTE":
                QMessageBox.warning(self, "Erreur", "Login déjà utilisé ❌")
            else:
                QMessageBox.critical(self, "Erreur", f"Réponse serveur inattendue : {reponse}")

        except Exception:
            QMessageBox.critical(self, "Erreur", "Serveur non disponible ❌")
# ...existing code...


# ============================
# Fenêtre Connexion
# ============================
class FenetreConnexion(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Connexion")
        self.showMaximized()

        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(70, 130, 180))
        self.setPalette(palette)

        fontTitre = QFont("Arial", 28, QFont.Bold)
        fontChamp = QFont("Arial", 18)

        titre = QLabel("Connexion")
        titre.setFont(fontTitre)
        titre.setStyleSheet("color:white;")
        titre.setAlignment(Qt.AlignCenter)

        self.login = QLineEdit(); self.login.setPlaceholderText("Login"); self.login.setFont(fontChamp)
        self.mdp = QLineEdit(); self.mdp.setPlaceholderText("Mot de passe"); self.mdp.setEchoMode(QLineEdit.Password); self.mdp.setFont(fontChamp)

        btn_connexion = QPushButton("Se connecter")
        btn_connexion.setFont(fontChamp)
        btn_connexion.setStyleSheet("background:white; padding:10px; border-radius:10px;")
        btn_connexion.clicked.connect(self.connexion)

        btn_creer = QPushButton("Créer un compte")
        btn_creer.setFont(fontChamp)
        btn_creer.setStyleSheet("background:white; padding:10px; border-radius:10px;")
        btn_creer.clicked.connect(self.ouvrir_page_creation)

        layout = QVBoxLayout()
        layout.addStretch()
        layout.addWidget(titre)
        layout.addWidget(self.login)
        layout.addWidget(self.mdp)
        layout.addWidget(btn_connexion)
        layout.addWidget(btn_creer)
        layout.addStretch()
        self.setLayout(layout)

    def connexion(self):
        login = self.login.text().strip()
        mdp = self.mdp.text().strip()

        client = socket.socket()
        client.connect((SERVER_IP, SERVER_PORT))
        client.send(f"{login}:{mdp}".encode())
        reponse = client.recv(1024).decode()
        client.close()

        if reponse == "OK":
            QMessageBox.information(self, "OK", f"Bienvenue {login} ✅")
        else:
            QMessageBox.warning(self, "Erreur", "Identifiants incorrects ❌")

    def ouvrir_page_creation(self):
        self.hide()
        self.page_creation = FenetreCreationCompte(self)
        self.page_creation.show()


# ============================
# Lancement de l'application
# ============================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    f = FenetreConnexion()
    f.show()
    sys.exit(app.exec_())
