import sys
import socket
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPalette, QColor, QPixmap
from module_Attribution_sujets_pyqt import get_subjects

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
        self.setMinimumSize(self.screen().size())
        self.resize(self.screen().size())

        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(70, 130, 180))
        self.setPalette(palette)

        fontTitre = QFont("Arial", 28, QFont.Bold)
        fontChamp = QFont("Arial", 16)
        fontLabel = QFont("Arial", 14)

        titre = QLabel("Connexion à votre espace candidat")
        titre.setFont(fontTitre)
        titre.setStyleSheet("color:white;")
        titre.setAlignment(Qt.AlignCenter)

        lbl_login = QLabel("Login : Entrez votre login")
        lbl_login.setFont(fontLabel)
        lbl_login.setStyleSheet("color:white;")
        self.login = QLineEdit()
        self.login.setPlaceholderText("Login")
        self.login.setFont(fontChamp)
        self.login.setStyleSheet("background:white; padding:10px; border-radius:8px;")
        exemple = QLabel("Exemple : lane")
        exemple.setStyleSheet("color:white; font-style:italic;")

        lbl_mdp = QLabel("Mot de passe : Entrez votre mot de passe")
        lbl_mdp.setFont(fontLabel)
        lbl_mdp.setStyleSheet("color:white;")
        self.mdp = QLineEdit()
        self.mdp.setPlaceholderText("Mot de passe")
        self.mdp.setEchoMode(QLineEdit.Password)
        self.mdp.setFont(fontChamp)
        self.mdp.setStyleSheet("background:white; padding:10px; border-radius:8px;")

        self.chk_afficher = QCheckBox("Afficher le mot de passe")
        self.chk_afficher.setStyleSheet("color:white; font-size:14px;")
        self.chk_afficher.stateChanged.connect(self.toggle_mdp)

        btn_connexion = QPushButton("Se connecter")
        btn_connexion.setFont(fontChamp)
        btn_connexion.setStyleSheet("background:darkblue; color:white; padding:12px; border-radius:10px;")
        btn_connexion.clicked.connect(self.connexion)

        lbl_creer = QLabel(
            "Vous n’avez pas de compte ? <a style='color:white; text-decoration:none;' href='#'>Créez-en un →</a>"
        )
        lbl_creer.setFont(QFont("Arial", 14))
        lbl_creer.setAlignment(Qt.AlignCenter)
        lbl_creer.setOpenExternalLinks(False)
        lbl_creer.linkActivated.connect(self.ouvrir_page_creation)

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

        frame = QFrame()
        frame.setLayout(form_layout)
        frame.setFixedWidth(450)
        frame.setStyleSheet("background-color: rgba(255,255,255,0.1); border-radius:15px; padding:20px;")

        main_layout = QVBoxLayout()
        main_layout.addStretch()
        main_layout.addWidget(titre)
        main_layout.addSpacing(30)
        main_layout.addWidget(frame, alignment=Qt.AlignCenter)
        main_layout.addStretch()
        self.setLayout(main_layout)

    def toggle_mdp(self):
        self.mdp.setEchoMode(QLineEdit.Normal if self.chk_afficher.isChecked() else QLineEdit.Password)

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
                self.hide()
                self.choix_sujets = FenetreChoixSujets(login, self)
                self.choix_sujets.show()
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

        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(70, 130, 180))
        self.setPalette(palette)

        fontTitre = QFont("Arial", 28, QFont.Bold)
        fontChamp = QFont("Arial", 16)
        fontLabel = QFont("Arial", 14)

        titre = QLabel("Création de compte")
        titre.setFont(fontTitre)
        titre.setStyleSheet("color:white;")
        titre.setAlignment(Qt.AlignCenter)

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

        self.chk_afficher = QCheckBox("Afficher le mot de passe")
        self.chk_afficher.setStyleSheet("color:white; font-size:14px;")
        self.chk_afficher.stateChanged.connect(self.toggle_mdp)

        btn_creer = QPushButton("Créer mon compte")
        btn_creer.setFont(fontChamp)
        btn_creer.setStyleSheet("background:darkblue; color:white; padding:12px; border-radius:10px;")
        btn_creer.clicked.connect(self.creer_compte)

        btn_retour = QPushButton("Retour")
        btn_retour.setFont(fontChamp)
        btn_retour.setStyleSheet("background:darkred; color:white; padding:12px; border-radius:10px;")
        btn_retour.clicked.connect(self.retour)

        form_layout = QVBoxLayout()
        form_layout.setAlignment(Qt.AlignCenter)
        form_layout.setSpacing(10)
        for lbl, champ in [(lbl_nom, self.nom), (lbl_prenom, self.prenom), (lbl_login, self.login), (lbl_mdp, self.mdp)]:
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

        main_layout = QVBoxLayout()
        main_layout.addStretch()
        main_layout.addWidget(titre)
        main_layout.addSpacing(30)
        main_layout.addWidget(frame, alignment=Qt.AlignCenter)
        main_layout.addStretch()
        self.setLayout(main_layout)

    def toggle_mdp(self):
        self.mdp.setEchoMode(QLineEdit.Normal if self.chk_afficher.isChecked() else QLineEdit.Password)

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
                self.page_connexion.login.setText(login)
                self.retour()
            elif reponse == "LOGIN_EXISTE":
                QMessageBox.warning(self, "Erreur", "Login déjà utilisé ❌")
            else:
                QMessageBox.critical(self, "Erreur", f"Réponse serveur inattendue : {reponse}")
        except Exception:
            QMessageBox.critical(self, "Erreur", "Serveur non disponible ❌")


# ============================
# Fenêtre Changement de Mot de Passe
# ============================
class FenetreChangerMdp(QWidget):
    def __init__(self, login, parent_fenetre):
        super().__init__()
        self.login = login
        self.parent_fenetre = parent_fenetre
        self.setWindowTitle("Changer mon mot de passe")
        self.setFixedSize(400, 350)

        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(70, 130, 180))
        self.setPalette(palette)

        fontTitre = QFont("Arial", 20, QFont.Bold)
        fontChamp = QFont("Arial", 14)

        titre = QLabel("Changer mon mot de passe")
        titre.setFont(fontTitre)
        titre.setStyleSheet("color:white;")
        titre.setAlignment(Qt.AlignCenter)

        # Ancien mot de passe
        lbl_ancien = QLabel("Ancien mot de passe :")
        lbl_ancien.setFont(fontChamp)
        lbl_ancien.setStyleSheet("color:white;")
        self.ancien_mdp = QLineEdit()
        self.ancien_mdp.setEchoMode(QLineEdit.Password)
        self.ancien_mdp.setFont(fontChamp)
        self.ancien_mdp.setStyleSheet("background:white; padding:8px; border-radius:8px;")

        # Nouveau mot de passe
        lbl_nouveau = QLabel("Nouveau mot de passe :")
        lbl_nouveau.setFont(fontChamp)
        lbl_nouveau.setStyleSheet("color:white;")
        self.nouveau_mdp = QLineEdit()
        self.nouveau_mdp.setEchoMode(QLineEdit.Password)
        self.nouveau_mdp.setFont(fontChamp)
        self.nouveau_mdp.setStyleSheet("background:white; padding:8px; border-radius:8px;")

        # Confirmation
        lbl_confirmation = QLabel("Confirmer le nouveau mot de passe :")
        lbl_confirmation.setFont(fontChamp)
        lbl_confirmation.setStyleSheet("color:white;")
        self.confirmation_mdp = QLineEdit()
        self.confirmation_mdp.setEchoMode(QLineEdit.Password)
        self.confirmation_mdp.setFont(fontChamp)
        self.confirmation_mdp.setStyleSheet("background:white; padding:8px; border-radius:8px;")

        # Checkbox pour afficher les mots de passe
        self.chk_afficher = QCheckBox("Afficher les mots de passe")
        self.chk_afficher.setStyleSheet("color:white; font-size:12px;")
        self.chk_afficher.stateChanged.connect(self.toggle_mdp_visibility)

        # Boutons
        btn_changer = QPushButton("Changer le mot de passe")
        btn_changer.setFont(fontChamp)
        btn_changer.setStyleSheet("background:darkblue; color:white; padding:10px; border-radius:10px;")
        btn_changer.clicked.connect(self.changer_mdp)

        btn_annuler = QPushButton("Annuler")
        btn_annuler.setFont(fontChamp)
        btn_annuler.setStyleSheet("background:darkred; color:white; padding:10px; border-radius:10px;")
        btn_annuler.clicked.connect(self.close)

        # Layout
        form_layout = QVBoxLayout()
        form_layout.setSpacing(10)
        
        fields = [
            (lbl_ancien, self.ancien_mdp),
            (lbl_nouveau, self.nouveau_mdp),
            (lbl_confirmation, self.confirmation_mdp)
        ]
        
        for label, field in fields:
            form_layout.addWidget(label)
            form_layout.addWidget(field)
        
        form_layout.addWidget(self.chk_afficher)
        form_layout.addSpacing(20)
        form_layout.addWidget(btn_changer)
        form_layout.addWidget(btn_annuler)

        frame = QFrame()
        frame.setLayout(form_layout)
        frame.setStyleSheet("background-color: rgba(255,255,255,0.1); border-radius:15px; padding:20px;")

        main_layout = QVBoxLayout()
        main_layout.addWidget(titre)
        main_layout.addSpacing(20)
        main_layout.addWidget(frame)
        self.setLayout(main_layout)

    def toggle_mdp_visibility(self):
        mode = QLineEdit.Normal if self.chk_afficher.isChecked() else QLineEdit.Password
        self.ancien_mdp.setEchoMode(mode)
        self.nouveau_mdp.setEchoMode(mode)
        self.confirmation_mdp.setEchoMode(mode)

    def changer_mdp(self):
        ancien = self.ancien_mdp.text().strip()
        nouveau = self.nouveau_mdp.text().strip()
        confirmation = self.confirmation_mdp.text().strip()

        # Vérifications
        if not (ancien and nouveau and confirmation):
            QMessageBox.warning(self, "Erreur", "Tous les champs sont obligatoires.")
            return

        if nouveau != confirmation:
            QMessageBox.warning(self, "Erreur", "Les nouveaux mots de passe ne correspondent pas.")
            return

        if len(nouveau) < 4:
            QMessageBox.warning(self, "Erreur", "Le mot de passe doit contenir au moins 4 caractères.")
            return

        # D'abord vérifier l'ancien mot de passe
        try:
            client = socket.socket()
            client.connect((SERVER_IP, SERVER_PORT))
            client.send(f"{self.login}:{ancien}".encode())
            reponse = client.recv(1024).decode()
            
            if reponse != "OK":
                QMessageBox.warning(self, "Erreur", "Ancien mot de passe incorrect.")
                client.close()
                return
            
            # Envoyer la demande de changement
            client.send(f"CHANGE_PASSWORD:{self.login}:{nouveau}".encode())
            reponse = client.recv(1024).decode()
            client.close()

            if reponse == "PASSWORD_CHANGED":
                QMessageBox.information(self, "Succès", "Mot de passe changé avec succès ✅")
                self.close()
            else:
                QMessageBox.warning(self, "Erreur", "Échec du changement de mot de passe.")
                
        except Exception:
            QMessageBox.critical(self, "Erreur", "Serveur non disponible ❌")


# ============================
# Fenêtre Choix de Sujets (Checkbox)
# ============================
class FenetreChoixSujets(QWidget):
    def __init__(self, login, page_connexion):
        super().__init__()
        self.login = login
        self.page_connexion = page_connexion
        self.fenetre_changer_mdp = None
        self.setWindowTitle(f"Choix de sujets - {login}")
        self.showMaximized()
        self.setMinimumSize(self.screen().size())
        self.resize(self.screen().size())

        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(70, 130, 180))
        self.setPalette(palette)

        fontTitre = QFont("Arial", 28, QFont.Bold)
        fontSujet = QFont("Arial", 16)

        # ------------------------------
        # Haut : thème à gauche + login/icône/retour à droite
        # ------------------------------
        lbl_theme = QLabel("AttributionSujet")
        lbl_theme.setFont(QFont("Arial", 18, QFont.Bold))
        lbl_theme.setStyleSheet("color:white;")

        lbl_icone = QLabel()
        lbl_icone.setPixmap(QPixmap("pv.png").scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation))

        lbl_user = QLabel(self.login)
        lbl_user.setFont(QFont("Arial", 14))
        lbl_user.setStyleSheet("""
            color:white;
            padding:5px 12px;
            border:2px solid white;
            border-radius:12px;
        """)

        box_user = QHBoxLayout()
        box_user.addWidget(lbl_icone)
        box_user.addWidget(lbl_user)
        box_user.setSpacing(10)

        # Bouton pour changer le mot de passe
        btn_changer_mdp = QPushButton("Changer mon mot de passe")
        btn_changer_mdp.setFont(QFont("Arial", 12))
        btn_changer_mdp.setStyleSheet("background:orange; color:white; padding:8px; border-radius:8px;")
        btn_changer_mdp.clicked.connect(self.ouvrir_changer_mdp)

        btn_retour = QPushButton("Retour à la connexion")
        btn_retour.setFont(QFont("Arial", 16))
        btn_retour.setStyleSheet("background:darkred; color:white; padding:10px; border-radius:10px;")
        btn_retour.clicked.connect(self.retour_connexion)

        layout_haut = QHBoxLayout()
        layout_haut.addWidget(lbl_theme)
        layout_haut.addStretch()
        layout_haut.addWidget(btn_changer_mdp)
        layout_haut.addSpacing(10)
        layout_haut.addLayout(box_user)
        layout_haut.addSpacing(20)
        layout_haut.addWidget(btn_retour)

        # ------------------------------
        # Titre centré
        # ------------------------------
        titre = QLabel("Choisissez vos sujets")
        titre.setFont(fontTitre)
        titre.setStyleSheet("color:white;")
        titre.setAlignment(Qt.AlignCenter)

        # ------------------------------
        # Sujets simples (checkbox) au centre
        # ------------------------------
        self.sujets = get_subjects()
        self.checkbox_dict = {}
        sujets_layout = QVBoxLayout()
        sujets_layout.setAlignment(Qt.AlignCenter)

        for _id, titre_sujet, description in self.sujets:
            cb = QCheckBox(f"{titre_sujet} - {description}")
            cb.setFont(fontSujet)
            cb.setStyleSheet("color:white;")
            sujets_layout.addWidget(cb)
            self.checkbox_dict[_id] = cb

        # ------------------------------
        # Boutons Valider / Résultats
        # ------------------------------
        btn_valider = QPushButton("Valider mes choix")
        btn_valider.setFont(fontSujet)
        btn_valider.setStyleSheet("background:darkblue; color:white; padding:12px; border-radius:10px;")
        btn_valider.clicked.connect(self.valider_choix)

        btn_resultat = QPushButton("Résultats")
        btn_resultat.setFont(fontSujet)
        btn_resultat.setStyleSheet("background:darkgreen; color:white; padding:12px; border-radius:10px;")

        layout_boutons = QHBoxLayout()
        layout_boutons.setAlignment(Qt.AlignCenter)
        layout_boutons.addWidget(btn_valider)
        layout_boutons.addWidget(btn_resultat)

        # ------------------------------
        # Layout principal avec sujets centrés verticalement
        # ------------------------------
        layout = QVBoxLayout()
        layout.addLayout(layout_haut)
        layout.addStretch()
        layout.addWidget(titre)
        layout.addSpacing(20)
        layout.addLayout(sujets_layout)
        layout.addSpacing(20)
        layout.addLayout(layout_boutons)
        layout.addStretch()

        self.setLayout(layout)

    # ------------------------------
    # Fonctions
    # ------------------------------
    def ouvrir_changer_mdp(self):
        """Ouvre la fenêtre de changement de mot de passe"""
        self.fenetre_changer_mdp = FenetreChangerMdp(self.login, self)
        self.fenetre_changer_mdp.show()

    def valider_choix(self):
        sujets_choisis = [cb.text() for _id, cb in self.checkbox_dict.items() if cb.isChecked()]
        if not sujets_choisis:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner au moins un sujet.")
            return

        QMessageBox.information(
            self,
            "Sujets choisis",
            "Vous avez choisi :\n" + "\n".join(sujets_choisis) + " ✅"
        )

        try:
            client = socket.socket()
            client.connect((SERVER_IP, SERVER_PORT))
            ids = [str(_id) for _id, cb in self.checkbox_dict.items() if cb.isChecked()]
            client.send(f"CHOIX_SUJETS:{self.login}:{','.join(ids)}".encode())
            client.close()
        except Exception:
            QMessageBox.critical(self, "Erreur", "Impossible d'envoyer les choix au serveur.")

    def retour_connexion(self):
        self.close()
        self.page_connexion.show()


# ============================
# Lancement de l'application
# ============================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    f = FenetreConnexion()
    f.show()
    sys.exit(app.exec_())