import sys, socket
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPalette, QColor

SERVER_IP = "127.0.0.1"
SERVER_PORT = 55555


# ============================
# Fenêtre Connexion
# ============================
class FenetreConnexion(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Connexion à votre espace candidat")
        self.showMaximized()
        self.setMinimumSize(self.screen().size())  # Empêche la fenêtre de rétrécir
        self.resize(self.screen().size())  
        # --- Couleur de fond (bleu clair)
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(70, 130, 180))
        self.setPalette(palette)

        fontTitre = QFont("Arial", 28, QFont.Bold)
        fontChamp = QFont("Arial", 16)
        fontLabel = QFont("Arial", 14)

        # --- Titre principal
        titre = QLabel("Connexion à votre espace candidat")
        titre.setFont(fontTitre)
        titre.setStyleSheet("color:white;")
        titre.setAlignment(Qt.AlignCenter)

        # --- Label et champ Login
        lbl_login = QLabel("Login : Entrez votre login")
        lbl_login.setFont(fontLabel)
        lbl_login.setStyleSheet("color:white;")
        self.login = QLineEdit()
        self.login.setPlaceholderText("Login")
        self.login.setFont(fontChamp)
        self.login.setStyleSheet("background:white; padding:10px; border-radius:8px;")
        exemple = QLabel("Exemple : lane")
        exemple.setStyleSheet("color:white; font-style:italic;")

        # --- Label et champ Mot de passe
        lbl_mdp = QLabel("Mot de passe : Entrez votre mot de passe")
        lbl_mdp.setFont(fontLabel)
        lbl_mdp.setStyleSheet("color:white;")
        self.mdp = QLineEdit()
        self.mdp.setPlaceholderText("Mot de passe")
        self.mdp.setEchoMode(QLineEdit.Password)
        self.mdp.setFont(fontChamp)
        self.mdp.setStyleSheet("background:white; padding:10px; border-radius:8px;")

        # --- Case à cocher : afficher le mot de passe
        self.chk_afficher = QCheckBox("Afficher le mot de passe")
        self.chk_afficher.setStyleSheet("color:white; font-size:14px;")
        self.chk_afficher.stateChanged.connect(self.toggle_mdp)

        # --- Bouton Se connecter
        btn_connexion = QPushButton("Se connecter")
        btn_connexion.setFont(fontChamp)
        btn_connexion.setStyleSheet("background:darkblue; color:white; padding:12px; border-radius:10px;")
        btn_connexion.clicked.connect(self.connexion)

        # --- Lien Créer un compte
        lbl_creer = QLabel("Vous n’avez pas de compte ? <a style='color:white; text-decoration:none;' href='#'>Créez-en un →</a>")
        lbl_creer.setFont(QFont("Arial", 14))
        lbl_creer.setAlignment(Qt.AlignCenter)
        lbl_creer.setOpenExternalLinks(False)
        lbl_creer.linkActivated.connect(self.ouvrir_page_creation)

        # --- Formulaire centré (dans un cadre)
        form_layout = QVBoxLayout()
        form_layout.setAlignment(Qt.AlignCenter)
        form_layout.setSpacing(10)
        form_layout.addWidget(lbl_login)
        form_layout.addWidget(self.login)
        form_layout.addWidget(exemple)
        form_layout.addSpacing(15)
        form_layout.addWidget(lbl_mdp)
        form_layout.addWidget(self.mdp)
        form_layout.addWidget(self.chk_afficher)
        form_layout.addSpacing(15)
        form_layout.addWidget(btn_connexion)
        form_layout.addSpacing(20)
        form_layout.addWidget(lbl_creer)

        # --- Cadre pour centrer le formulaire
        frame = QFrame()
        frame.setLayout(form_layout)
        frame.setFixedWidth(450)
        frame.setStyleSheet("background-color: rgba(255,255,255,0.1); border-radius:15px; padding:20px;")

        # --- Layout principal
        main_layout = QVBoxLayout()
        main_layout.addStretch()
        main_layout.addWidget(titre)
        main_layout.addSpacing(30)
        main_layout.addWidget(frame, alignment=Qt.AlignCenter)
        main_layout.addStretch()
        self.setLayout(main_layout)

    def toggle_mdp(self):
        """Afficher ou masquer le mot de passe"""
        if self.chk_afficher.isChecked():
            self.mdp.setEchoMode(QLineEdit.Normal)
        else:
            self.mdp.setEchoMode(QLineEdit.Password)

    def connexion(self):
        login = self.login.text().strip()
        mdp = self.mdp.text().strip()

        try:
            client = socket.socket()
            client.connect((SERVER_IP, SERVER_PORT))
            client.send(f"{login}:{mdp}".encode())
            reponse = client.recv(1024).decode()
            client.close()

            if reponse == "OK":
                QMessageBox.information(self, "OK", f"Bienvenue {login} ✅")
            else:
                QMessageBox.warning(self, "Erreur", "Identifiants incorrects ❌")

        except Exception:
            QMessageBox.critical(self, "Erreur", "Serveur non disponible ❌")

    def ouvrir_page_creation(self):
        self.hide()
        self.page_creation = FenetreCreationCompte(self)
        self.page_creation.show()


# ============================
# Fenêtre Création de Compte
# ============================
class FenetreCreationCompte(QWidget):
    def __init__(self, page_connexion):
        super().__init__()
        self.page_connexion = page_connexion
        self.setWindowTitle("Création de compte")
        self.showMaximized()
        self.setMinimumSize(self.screen().size())
        self.resize(self.screen().size())

        # --- Couleur de fond (bleu clair, comme la page de connexion)
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(70, 130, 180))
        self.setPalette(palette)

        fontTitre = QFont("Arial", 28, QFont.Bold)
        fontChamp = QFont("Arial", 16)
        fontLabel = QFont("Arial", 14)

        # --- Titre principal
        titre = QLabel("Création de compte")
        titre.setFont(fontTitre)
        titre.setStyleSheet("color:white;")
        titre.setAlignment(Qt.AlignCenter)

        # --- Champs + labels
        def champ_avec_label(label_texte, placeholder):
            lbl = QLabel(label_texte)
            lbl.setFont(fontLabel)
            lbl.setStyleSheet("color:white;")
            champ = QLineEdit()
            champ.setPlaceholderText(placeholder)
            champ.setFont(fontChamp)
            champ.setStyleSheet("background:white; padding:10px; border-radius:8px;")
            return lbl, champ

        lbl_nom, self.nom = champ_avec_label("Nom :", "Nom")
        lbl_prenom, self.prenom = champ_avec_label("Prénom :", "Prénom")
        lbl_login, self.login = champ_avec_label("Login :", "Email / Login")
        lbl_mdp, self.mdp = champ_avec_label("Mot de passe :", "Mot de passe")
        self.mdp.setEchoMode(QLineEdit.Password)

        # --- Case à cocher : afficher le mot de passe
        self.chk_afficher = QCheckBox("Afficher le mot de passe")
        self.chk_afficher.setStyleSheet("color:white; font-size:14px;")
        self.chk_afficher.stateChanged.connect(self.toggle_mdp)

        # --- Boutons
        btn_creer = QPushButton("Créer mon compte")
        btn_creer.setFont(fontChamp)
        btn_creer.setStyleSheet("background:darkblue; color:white; padding:12px; border-radius:10px;")
        btn_creer.clicked.connect(self.creer_compte)

        btn_retour = QPushButton("Retour")
        btn_retour.setFont(fontChamp)
        btn_retour.setStyleSheet("background:darkblue; color:white; padding:12px; border-radius:10px;")
        btn_retour.clicked.connect(self.retour)

        # --- Formulaire dans un cadre centré
        form_layout = QVBoxLayout()
        form_layout.setAlignment(Qt.AlignCenter)
        form_layout.setSpacing(10)
        for lbl, champ in [
            (lbl_nom, self.nom),
            (lbl_prenom, self.prenom),
            (lbl_login, self.login),
            (lbl_mdp, self.mdp),
        ]:
            form_layout.addWidget(lbl)
            form_layout.addWidget(champ)
            form_layout.addSpacing(10)

        form_layout.addWidget(self.chk_afficher)
        form_layout.addSpacing(15)
        form_layout.addWidget(btn_creer)
        form_layout.addWidget(btn_retour)

        frame = QFrame()
        frame.setLayout(form_layout)
        frame.setFixedWidth(450)
        frame.setStyleSheet("background-color: rgba(255,255,255,0.1); border-radius:15px; padding:20px;")

        # --- Layout principal
        main_layout = QVBoxLayout()
        main_layout.addStretch()
        main_layout.addWidget(titre)
        main_layout.addSpacing(30)
        main_layout.addWidget(frame, alignment=Qt.AlignCenter)
        main_layout.addStretch()
        self.setLayout(main_layout)

    def toggle_mdp(self):
        if self.chk_afficher.isChecked():
            self.mdp.setEchoMode(QLineEdit.Normal)
        else:
            self.mdp.setEchoMode(QLineEdit.Password)

    def retour(self):
        self.close()
        self.page_connexion.show()

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
                self.nom.clear()
                self.prenom.clear()
                self.login.clear()
                self.mdp.clear()
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

# ============================
# Lancement de l'application
# ============================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    f = FenetreConnexion()
    f.show()
    sys.exit(app.exec_())
