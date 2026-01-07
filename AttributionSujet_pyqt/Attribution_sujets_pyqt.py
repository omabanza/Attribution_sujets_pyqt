import sys
import os
import socket
import ast
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPalette, QColor, QPixmap
from module_Attribution_sujets_pyqt import get_subjects
from resultats_interface import ResultatsInterface

# ============================
# CONFIGURATION DU SERVEUR
# ============================
SERVER_IP = "127.0.0.1"      # Adresse IP du serveur (localhost)
SERVER_PORT = 55555          # Port de communication TCP

# ============================
# FENÊTRE DE CONNEXION
# ============================
class FenetreConnexion(QWidget):
    """
    Fenêtre de connexion principale de l'application.
    Permet aux utilisateurs de se connecter avec leur login/mot de passe.
    """
    def __init__(self):
        """Initialise la fenêtre de connexion avec tous ses composants."""
        super().__init__()
        # Configuration de la fenêtre
        self.setWindowTitle("Connexion à votre espace stagiaire")
        self.showMaximized()  # Fenêtre en plein écran
        self.setMinimumSize(self.screen().size())
        self.resize(self.screen().size())
        
        # Définition de la couleur de fond
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(70, 130, 180))  # Bleu acier
        self.setPalette(palette)
        
        # Configuration des polices
        fontTitre = QFont("Arial", 28, QFont.Bold)
        fontChamp = QFont("Arial", 16)
        fontLabel = QFont("Arial", 14)
        
        # ======================
        # CRÉATION DES WIDGETS
        # ======================
        
        # Titre principal
        titre = QLabel("Connexion à votre espace stagiaire")
        titre.setFont(fontTitre)
        titre.setStyleSheet("color:white;")
        titre.setAlignment(Qt.AlignCenter)
        
        # Champ login
        lbl_login = QLabel("Login : Entrez votre login")
        lbl_login.setFont(fontLabel)
        lbl_login.setStyleSheet("color:white;")
        self.login = QLineEdit()
        self.login.setPlaceholderText("Login")
        self.login.setFont(fontChamp)
        self.login.setStyleSheet("background:white; padding:10px; border-radius:8px;")
        
        # Exemple de login
        exemple = QLabel("Exemple : lane")
        exemple.setStyleSheet("color:white; font-style:italic;")
        
        # Champ mot de passe
        lbl_mdp = QLabel("Mot de passe : Entrez votre mot de passe")
        lbl_mdp.setFont(fontLabel)
        lbl_mdp.setStyleSheet("color:white;")
        self.mdp = QLineEdit()
        self.mdp.setPlaceholderText("Mot de passe")
        self.mdp.setEchoMode(QLineEdit.Password)  # Masquer les caractères
        self.mdp.setFont(fontChamp)
        self.mdp.setStyleSheet("background:white; padding:10px; border-radius:8px;")
        
        # Checkbox pour afficher/masquer le mot de passe
        self.chk_afficher = QCheckBox("Afficher le mot de passe")
        self.chk_afficher.setStyleSheet("color:white; font-size:14px;")
        self.chk_afficher.stateChanged.connect(self.toggle_mdp)
        
        # Bouton de connexion
        btn_connexion = QPushButton("Se connecter")
        btn_connexion.setFont(fontChamp)
        btn_connexion.setStyleSheet("background:darkblue; color:white; padding:12px; border-radius:10px;")
        btn_connexion.clicked.connect(self.connexion)
        
        # Lien pour créer un compte
        lbl_creer = QLabel(
            "Vous n'avez pas de compte ? <a style='color:white; text-decoration:none;' href='#'>Créez-en un →</a>"
        )
        lbl_creer.setFont(QFont("Arial", 14))
        lbl_creer.setAlignment(Qt.AlignCenter)
        lbl_creer.setOpenExternalLinks(False)
        lbl_creer.linkActivated.connect(self.ouvrir_page_creation)
        
        # ======================
        # ORGANISATION DU LAYOUT
        # ======================
        
        # Layout du formulaire
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
        
        # Frame pour contenir le formulaire
        frame = QFrame()
        frame.setLayout(form_layout)
        frame.setFixedWidth(450)
        frame.setStyleSheet("background-color: rgba(255,255,255,0.1); border-radius:15px; padding:20px;")
        
        # Layout principal
        main_layout = QVBoxLayout()
        main_layout.addStretch()
        main_layout.addWidget(titre)
        main_layout.addSpacing(30)
        main_layout.addWidget(frame, alignment=Qt.AlignCenter)
        main_layout.addStretch()
        self.setLayout(main_layout)
    
    def toggle_mdp(self):
        """
        Affiche ou masque le mot de passe selon l'état de la checkbox.
        """
        self.mdp.setEchoMode(QLineEdit.Normal if self.chk_afficher.isChecked() else QLineEdit.Password)
    
    def connexion(self):
        """
        Gère le processus de connexion au serveur.
        Vérifie les identifiants et redirige vers l'interface appropriée.
        """
        login = self.login.text().strip()
        mdp = self.mdp.text().strip()
        
        print(f"DEBUG: Tentative connexion - Login: '{login}', MDP: '{mdp}'")
        
        # Vérification des champs obligatoires
        if not login or not mdp:
            QMessageBox.warning(self, "Erreur", "Veuillez remplir tous les champs")
            return
        
        try:
            # Établissement de la connexion TCP avec le serveur
            print(f"DEBUG: Création du socket...")
            client = socket.socket()
            client.settimeout(5)  # Timeout de 5 secondes
            
            print(f"DEBUG: Connexion à {SERVER_IP}:{SERVER_PORT}...")
            client.connect((SERVER_IP, SERVER_PORT))
            print("DEBUG: Connecté au serveur")
            
            # Format du message : login:mdp
            message = f"{login}:{mdp}"
            print(f"DEBUG: Envoi du message: '{message}'")
            
            # Envoi des identifiants
            client.send(message.encode())
            
            # Réception de la réponse du serveur
            print("DEBUG: Attente réponse...")
            reponse = client.recv(1024).decode()
            print(f"DEBUG: Réponse reçue: '{reponse}'")
            
            client.close()  # Fermeture de la connexion
            
            # Traitement de la réponse
            if reponse == "ADMIN_OK":  # Connexion administrateur réussie
                print("DEBUG: Connexion admin réussie")
                self.hide()
                self.lancer_interface_admin()
            elif reponse == "OK":  # Connexion utilisateur réussie
                print("DEBUG: Connexion utilisateur réussie")
                self.hide()
                # Ouvrir l'interface de choix des sujets
                self.choix_sujets = FenetreChoixSujets(login, self)
                self.choix_sujets.show()
            elif reponse == "NOK":  # Identifiants incorrects
                print("DEBUG: Identifiants incorrects")
                QMessageBox.warning(self, "Erreur", "Identifiants incorrects ")
            else:  # Réponse inattendue
                print(f"DEBUG: Réponse inattendue: {reponse}")
                QMessageBox.warning(self, "Erreur", f"Réponse serveur inattendue: '{reponse}'")
                
        except socket.timeout:
            print("DEBUG: Timeout - Serveur ne répond pas")
            QMessageBox.critical(self, "Erreur", "Le serveur ne répond pas (timeout de 5s)")
        except ConnectionRefusedError:
            print("DEBUG: Connexion refusée")
            QMessageBox.critical(self, "Erreur", 
                "Impossible de se connecter au serveur \n\n"
                "Assurez-vous que le serveur est démarré:\n"
                "1. Ouvrez un terminal\n"
                "2. Exécutez: python serveur_tcp_sqlite.py\n"
                "3. Attendez le message 'Serveur en écoute'")
        except Exception as e:
            print(f"DEBUG: Exception: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Erreur", f"Erreur de connexion: {str(e)}")
    
    def lancer_interface_admin(self):
        """
        Ouvre l'interface d'administration si l'utilisateur est un admin.
        """
        try:
            # Import dynamique du module admin
            from admin_interface import AdminPanel
            
            # Création et affichage du panneau d'administration
            self.admin_panel = AdminPanel()
            self.admin_panel.parent_fenetre = self  # Référence pour revenir
            self.admin_panel.show()
        except ImportError as e:
            QMessageBox.critical(self, "Erreur", 
                f"Interface admin non disponible:\n{e}\n\n"
                f"Assurez-vous que le fichier admin_interface.py existe dans le même dossier.")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur inattendue: {e}")
    
    def ouvrir_page_creation(self):
        """
        Ouvre la fenêtre de création de compte.
        """
        self.hide()
        self.page_creation = FenetreCreationCompte(self)
        self.page_creation.show()


# ============================
# FENÊTRE DE CRÉATION DE COMPTE
# ============================
class FenetreCreationCompte(QWidget):
    """
    Fenêtre permettant aux utilisateurs de créer un nouveau compte.
    """
    def __init__(self, page_connexion):
        """
        Initialise la fenêtre de création de compte.
        
        Args:
            page_connexion: Référence à la fenêtre de connexion parente
        """
        super().__init__()
        self.page_connexion = page_connexion  # Référence à la fenêtre principale
        
        # Configuration de la fenêtre
        self.setWindowTitle("Création de compte")
        self.showMaximized()
        self.setMinimumSize(self.screen().size())
        self.resize(self.screen().size())
        
        # Couleur de fond
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(70, 130, 180))
        self.setPalette(palette)
        
        # Configuration des polices
        fontTitre = QFont("Arial", 28, QFont.Bold)
        fontChamp = QFont("Arial", 16)
        fontLabel = QFont("Arial", 14)
        
        # Titre principal
        titre = QLabel("Création de compte")
        titre.setFont(fontTitre)
        titre.setStyleSheet("color:white;")
        titre.setAlignment(Qt.AlignCenter)
        
        def champ_avec_label(label_texte, placeholder):
            """
            Fonction utilitaire pour créer un champ avec son label.
            
            Args:
                label_texte: Texte du label
                placeholder: Texte d'aide dans le champ
                
            Returns:
                tuple: (label, champ)
            """
            lbl = QLabel(label_texte)
            lbl.setFont(fontLabel)
            lbl.setStyleSheet("color:white;")
            champ = QLineEdit()
            champ.setPlaceholderText(placeholder)
            champ.setFont(fontChamp)
            champ.setStyleSheet("background:white; padding:10px; border-radius:8px;")
            return lbl, champ
        
        # Création des champs du formulaire
        lbl_nom, self.nom = champ_avec_label("Nom :", "Nom")
        lbl_prenom, self.prenom = champ_avec_label("Prénom :", "Prénom")
        lbl_login, self.login = champ_avec_label("Login :", "Email / Login")
        lbl_mdp, self.mdp = champ_avec_label("Mot de passe :", "Mot de passe")
        self.mdp.setEchoMode(QLineEdit.Password)
        
        # Checkbox pour afficher le mot de passe
        self.chk_afficher = QCheckBox("Afficher le mot de passe")
        self.chk_afficher.setStyleSheet("color:white; font-size:14px;")
        self.chk_afficher.stateChanged.connect(self.toggle_mdp)
        
        # Bouton de création de compte
        btn_creer = QPushButton("Créer mon compte")
        btn_creer.setFont(fontChamp)
        btn_creer.setStyleSheet("background:darkblue; color:white; padding:12px; border-radius:10px;")
        btn_creer.clicked.connect(self.creer_compte)
        
        # Bouton retour
        btn_retour = QPushButton("Retour")
        btn_retour.setFont(fontChamp)
        btn_retour.setStyleSheet("background:darkred; color:white; padding:12px; border-radius:10px;")
        btn_retour.clicked.connect(self.retour)
        
        # ======================
        # ORGANISATION DU LAYOUT
        # ======================
        
        # Layout du formulaire
        form_layout = QVBoxLayout()
        form_layout.setAlignment(Qt.AlignCenter)
        form_layout.setSpacing(10)
        
        # Ajout des champs au layout
        for lbl, champ in [(lbl_nom, self.nom), (lbl_prenom, self.prenom), 
                          (lbl_login, self.login), (lbl_mdp, self.mdp)]:
            form_layout.addWidget(lbl)
            form_layout.addWidget(champ)
            form_layout.addSpacing(10)
        
        form_layout.addWidget(self.chk_afficher)
        form_layout.addSpacing(15)
        form_layout.addWidget(btn_creer)
        form_layout.addWidget(btn_retour)
        
        # Frame contenant le formulaire
        frame = QFrame()
        frame.setLayout(form_layout)
        frame.setFixedWidth(450)
        frame.setStyleSheet("background-color: rgba(255,255,255,0.1); border-radius:15px; padding:20px;")
        
        # Layout principal
        main_layout = QVBoxLayout()
        main_layout.addStretch()
        main_layout.addWidget(titre)
        main_layout.addSpacing(30)
        main_layout.addWidget(frame, alignment=Qt.AlignCenter)
        main_layout.addStretch()
        self.setLayout(main_layout)
    
    def toggle_mdp(self):
        """
        Affiche ou masque le mot de passe.
        """
        self.mdp.setEchoMode(QLineEdit.Normal if self.chk_afficher.isChecked() else QLineEdit.Password)
    
    def retour(self):
        """
        Retourne à la fenêtre de connexion.
        """
        self.close()
        self.page_connexion.show()
    
    def creer_compte(self):
        """
        Envoie les informations de création de compte au serveur.
        """
        # Récupération des données du formulaire
        nom = self.nom.text().strip()
        prenom = self.prenom.text().strip()
        login = self.login.text().strip()
        mdp = self.mdp.text().strip()
        
        # Validation des champs
        if not (nom and prenom and login and mdp):
            QMessageBox.warning(self, "Erreur", "Tous les champs sont obligatoires.")
            return
        
        try:
            # Connexion au serveur pour créer le compte
            client = socket.socket()
            client.connect((SERVER_IP, SERVER_PORT))
            
            # Format du message : REGISTER:nom:prenom:login:mdp
            client.send(f"REGISTER:{nom}:{prenom}:{login}:{mdp}".encode())
            
            # Réception de la réponse
            reponse = client.recv(1024).decode()
            client.close()
            
            # Traitement de la réponse
            if reponse == "INSCRIPTION_OK":
                QMessageBox.information(self, "OK", "Compte créé ")
                # Réinitialisation des champs et retour
                self.nom.clear()
                self.prenom.clear()
                self.login.clear()
                self.mdp.clear()
                self.page_connexion.login.setText(login)  # Pré-remplir le login
                self.retour()
            elif reponse == "LOGIN_EXISTE":
                QMessageBox.warning(self, "Erreur", "Login déjà utilisé ")
            else:
                QMessageBox.critical(self, "Erreur", f"Réponse serveur inattendue : {reponse}")
        except Exception:
            QMessageBox.critical(self, "Erreur", "Serveur non disponible ")


# ============================
# FENÊTRE DE CHANGEMENT DE MOT DE PASSE
# ============================
class FenetrePageChangementMdp(QWidget):
    """
    Fenêtre permettant aux utilisateurs de changer leur mot de passe.
    """
    def __init__(self, login, parent_fenetre):
        """
        Initialise la fenêtre de changement de mot de passe.
        
        Args:
            login: Identifiant de l'utilisateur
            parent_fenetre: Fenêtre parente (choix de sujets)
        """
        super().__init__()
        self.login = login
        self.parent_fenetre = parent_fenetre
        
        # Configuration de la fenêtre
        self.setWindowTitle("Changement de mot de passe")
        self.showMaximized()
        self.setMinimumSize(self.screen().size())
        self.resize(self.screen().size())
        
        # Couleur de fond
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(70, 130, 180))
        self.setPalette(palette)
        
        # Configuration des polices
        fontTitre = QFont("Arial", 28, QFont.Bold)
        fontChamp = QFont("Arial", 16)
        fontLabel = QFont("Arial", 14)
        
        # ======================
        # CRÉATION DES WIDGETS
        # ======================
        
        # Titre principal
        titre = QLabel("Changement de mot de passe")
        titre.setFont(fontTitre)
        titre.setStyleSheet("color:white;")
        titre.setAlignment(Qt.AlignCenter)
        
        # Instructions
        lbl_instructions = QLabel(
            "Pour changer votre mot de passe, veuillez remplir les champs ci-dessous."
        )
        lbl_instructions.setFont(fontLabel)
        lbl_instructions.setStyleSheet("color:white;")
        lbl_instructions.setAlignment(Qt.AlignCenter)
        lbl_instructions.setWordWrap(True)
        
        # Champ ancien mot de passe
        lbl_ancien = QLabel("Ancien mot de passe :")
        lbl_ancien.setFont(fontLabel)
        lbl_ancien.setStyleSheet("color:white;")
        self.ancien_mdp = QLineEdit()
        self.ancien_mdp.setEchoMode(QLineEdit.Password)
        self.ancien_mdp.setFont(fontChamp)
        self.ancien_mdp.setStyleSheet("background:white; padding:10px; border-radius:8px;")
        
        # Champ nouveau mot de passe
        lbl_nouveau = QLabel("Nouveau mot de passe :")
        lbl_nouveau.setFont(fontLabel)
        lbl_nouveau.setStyleSheet("color:white;")
        self.nouveau_mdp = QLineEdit()
        self.nouveau_mdp.setEchoMode(QLineEdit.Password)
        self.nouveau_mdp.setFont(fontChamp)
        self.nouveau_mdp.setStyleSheet("background:white; padding:10px; border-radius:8px;")
        
        # Champ confirmation
        lbl_confirmation = QLabel("Confirmer le nouveau mot de passe :")
        lbl_confirmation.setFont(fontLabel)
        lbl_confirmation.setStyleSheet("color:white;")
        self.confirmation_mdp = QLineEdit()
        self.confirmation_mdp.setEchoMode(QLineEdit.Password)
        self.confirmation_mdp.setFont(fontChamp)
        self.confirmation_mdp.setStyleSheet("background:white; padding:10px; border-radius:8px;")
        
        # Checkbox pour afficher les mots de passe
        self.chk_afficher = QCheckBox("Afficher les mots de passe")
        self.chk_afficher.setStyleSheet("color:white; font-size:14px;")
        self.chk_afficher.stateChanged.connect(self.toggle_mdp_visibility)
        
        # Bouton de changement
        btn_changer = QPushButton("Changer le mot de passe")
        btn_changer.setFont(fontChamp)
        btn_changer.setStyleSheet("background:darkblue; color:white; padding:12px; border-radius:10px;")
        btn_changer.clicked.connect(self.changer_mdp)
        
        # Bouton retour
        btn_annuler = QPushButton("Retour aux sujets")
        btn_annuler.setFont(fontChamp)
        btn_annuler.setStyleSheet("background:darkred; color:white; padding:12px; border-radius:10px;")
        btn_annuler.clicked.connect(self.retour_sujets)
        
        # ======================
        # ORGANISATION DU LAYOUT
        # ======================
        
        # Layout du formulaire
        form_layout = QVBoxLayout()
        form_layout.setAlignment(Qt.AlignCenter)
        form_layout.setSpacing(15)
        
        # Ajout des champs
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
        
        # Frame contenant le formulaire
        frame = QFrame()
        frame.setLayout(form_layout)
        frame.setFixedWidth(450)
        frame.setStyleSheet("background-color: rgba(255,255,255,0.1); border-radius:15px; padding:30px;")
        
        # Layout principal
        main_layout = QVBoxLayout()
        main_layout.addStretch()
        main_layout.addWidget(titre)
        main_layout.addSpacing(20)
        main_layout.addWidget(lbl_instructions)
        main_layout.addSpacing(30)
        main_layout.addWidget(frame, alignment=Qt.AlignCenter)
        main_layout.addStretch()
        self.setLayout(main_layout)
    
    def toggle_mdp_visibility(self):
        """
        Affiche ou masque tous les champs de mot de passe.
        """
        mode = QLineEdit.Normal if self.chk_afficher.isChecked() else QLineEdit.Password
        self.ancien_mdp.setEchoMode(mode)
        self.nouveau_mdp.setEchoMode(mode)
        self.confirmation_mdp.setEchoMode(mode)
    
    def changer_mdp(self):
        """
        Gère le processus de changement de mot de passe.
        """
        # Récupération des valeurs
        ancien = self.ancien_mdp.text().strip()
        nouveau = self.nouveau_mdp.text().strip()
        confirmation = self.confirmation_mdp.text().strip()
        
        # Validation des champs
        if not (ancien and nouveau and confirmation):
            QMessageBox.warning(self, "Erreur", "Tous les champs sont obligatoires.")
            return
        
        # Vérification de la correspondance
        if nouveau != confirmation:
            QMessageBox.warning(self, "Erreur", "Les nouveaux mots de passe ne correspondent pas.")
            return
        
        # Vérification de la longueur
        if len(nouveau) < 4:
            QMessageBox.warning(self, "Erreur", "Le mot de passe doit contenir au moins 4 caractères.")
            return
        
        try:
            # Connexion au serveur
            client = socket.socket()
            client.connect((SERVER_IP, SERVER_PORT))
            
            # Vérification de l'ancien mot de passe
            client.send(f"{self.login}:{ancien}".encode())
            reponse = client.recv(1024).decode()
            
            if reponse != "OK":
                QMessageBox.warning(self, "Erreur", "Ancien mot de passe incorrect.")
                client.close()
                return
            
            # Demande de changement de mot de passe
            client.send(f"CHANGE_PASSWORD:{self.login}:{nouveau}".encode())
            reponse = client.recv(1024).decode()
            client.close()
            
            # Traitement de la réponse
            if reponse == "PASSWORD_CHANGED":
                QMessageBox.information(self, "Succès", "Mot de passe changé avec succès ")
                self.retour_sujets()
            else:
                QMessageBox.warning(self, "Erreur", "Échec du changement de mot de passe.")
                
        except Exception:
            QMessageBox.critical(self, "Erreur", "Serveur non disponible ")
    
    def retour_sujets(self):
        """
        Retourne à la fenêtre de choix des sujets.
        """
        self.close()
        self.parent_fenetre.show()


# ============================
# FENÊTRE DE SUPPRESSION DE COMPTE
# ============================
class FenetreSuppressionCompte(QWidget):
    """
    Fenêtre permettant aux utilisateurs de supprimer leur compte.
    Avec plusieurs confirmations pour éviter les suppressions accidentelles.
    """
    def __init__(self, login, parent_fenetre, page_connexion):
        """
        Initialise la fenêtre de suppression de compte.
        
        Args:
            login: Identifiant de l'utilisateur
            parent_fenetre: Fenêtre parente (choix de sujets)
            page_connexion: Fenêtre de connexion principale
        """
        super().__init__()
        self.login = login
        self.parent_fenetre = parent_fenetre
        self.page_connexion = page_connexion
        
        # Configuration de la fenêtre
        self.setWindowTitle("Suppression de compte")
        self.setFixedSize(550, 450)  # Fenêtre de taille fixe
        
        # Centrage de la fenêtre
        screen_geometry = QApplication.desktop().screenGeometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)
        
        # Couleur de fond (rouge pour avertissement)
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(220, 80, 80))
        self.setPalette(palette)
        
        # Configuration des polices
        fontTitre = QFont("Arial", 22, QFont.Bold)
        fontLabel = QFont("Arial", 11)
        fontChamp = QFont("Arial", 12)
        
        # ======================
        # CRÉATION DES WIDGETS
        # ======================
        
        # Icône d'avertissement
        lbl_icone = QLabel("⚠️")
        lbl_icone.setFont(QFont("Arial", 48))
        lbl_icone.setAlignment(Qt.AlignCenter)
        lbl_icone.setStyleSheet("color:yellow;")
        
        # Titre
        titre = QLabel("SUPPRESSION DE COMPTE")
        titre.setFont(fontTitre)
        titre.setStyleSheet("color:white;")
        titre.setAlignment(Qt.AlignCenter)
        
        # Message d'avertissement détaillé
        lbl_message = QLabel(
            "<center><b style='color:#FFD700;'>ATTENTION : Action irréversible !</b></center><br>"
            "<p style='color:white; line-height:1.4;'>"
            "Vous êtes sur le point de supprimer définitivement votre compte.<br><br>"
            "<b>Conséquences :</b><br>"
            "• Toutes vos données seront effacées<br>"
            "• Vous perdrez l'accès à votre espace<br>"
            "• Vos choix de sujets seront perdus<br>"
            "• Cette action ne peut être annulée"
            "</p>"
        )
        lbl_message.setFont(fontLabel)
        lbl_message.setAlignment(Qt.AlignCenter)
        lbl_message.setWordWrap(True)
        
        # Champ mot de passe
        lbl_mdp = QLabel("Mot de passe actuel :")
        lbl_mdp.setFont(fontLabel)
        lbl_mdp.setStyleSheet("color:white;")
        
        self.champ_mdp = QLineEdit()
        self.champ_mdp.setEchoMode(QLineEdit.Password)
        self.champ_mdp.setFont(fontChamp)
        self.champ_mdp.setStyleSheet("""
            QLineEdit {
                background: white;
                padding: 10px;
                border-radius: 8px;
                border: 2px solid #ccc;
            }
        """)
        
        # Checkbox de confirmation
        self.check_confirmation = QCheckBox("Je comprends et accepte les conséquences")
        self.check_confirmation.setFont(fontLabel)
        self.check_confirmation.setStyleSheet("color:white;")
        
        # Bouton de suppression
        btn_supprimer = QPushButton("🗑️ Supprimer mon compte")
        btn_supprimer.setFont(QFont("Arial", 13, QFont.Bold))
        btn_supprimer.setStyleSheet("""
            QPushButton {
                background: darkred;
                color: white;
                padding: 12px;
                border-radius: 8px;
                border: 2px solid #FFD700;
            }
            QPushButton:hover {
                background: #FF4444;
                border: 2px solid white;
            }
            QPushButton:disabled {
                background: gray;
                border: 2px solid #999;
            }
        """)
        btn_supprimer.clicked.connect(self.supprimer_compte)
        
        # Bouton d'annulation
        btn_annuler = QPushButton("Annuler")
        btn_annuler.setFont(fontChamp)
        btn_annuler.setStyleSheet("""
            QPushButton {
                background: #4682B4;
                color: white;
                padding: 10px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background: #5A9BD3;
            }
        """)
        btn_annuler.clicked.connect(self.close)
        
        # ======================
        # ORGANISATION DU LAYOUT
        # ======================
        
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        layout.addWidget(lbl_icone)
        layout.addWidget(titre)
        layout.addWidget(lbl_message)
        layout.addWidget(lbl_mdp)
        layout.addWidget(self.champ_mdp)
        layout.addWidget(self.check_confirmation, 0, Qt.AlignCenter)
        layout.addSpacing(10)
        layout.addWidget(btn_supprimer)
        layout.addWidget(btn_annuler)
        
        # Activation/désactivation du bouton selon les conditions
        self.check_confirmation.stateChanged.connect(self.verifier_bouton)
        self.champ_mdp.textChanged.connect(self.verifier_bouton)
        self.verifier_bouton()
        
        self.setLayout(layout)
    
    def verifier_bouton(self):
        """
        Active le bouton de suppression seulement si toutes les conditions sont remplies :
        - Mot de passe saisi
        - Confirmation cochée
        """
        bouton = self.findChild(QPushButton, None)
        if bouton and bouton.text().startswith("🗑️"):
            mdp_ok = bool(self.champ_mdp.text().strip())
            confirme_ok = self.check_confirmation.isChecked()
            bouton.setEnabled(mdp_ok and confirme_ok)
    
    def supprimer_compte(self):
        """
        Gère le processus de suppression de compte avec confirmation.
        """
        mdp = self.champ_mdp.text().strip()
        
        # Dernière confirmation (popup)
        reponse = QMessageBox.question(
            self,
            "Dernière confirmation",
            "<b>Êtes-vous ABSOLUMENT SÛR ?</b><br><br>"
            "Cette action supprimera définitivement votre compte.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reponse != QMessageBox.Yes:
            return  # Annulation
        
        # Vérification du mot de passe
        try:
            client = socket.socket()
            client.connect((SERVER_IP, SERVER_PORT))
            
            # Vérification des identifiants
            client.send(f"{self.login}:{mdp}".encode())
            reponse = client.recv(1024).decode()
            
            if reponse != "OK":
                QMessageBox.warning(self, "Erreur", "Mot de passe incorrect.")
                client.close()
                return
            
            # Demande de suppression
            client.send(f"DELETE_ACCOUNT:{self.login}".encode())
            reponse = client.recv(1024).decode()
            client.close()
            
            if reponse == "ACCOUNT_DELETED":
                QMessageBox.information(self, "Succès", "Compte supprimé avec succès ")
                # Fermeture des fenêtres et retour à la connexion
                self.close()
                self.parent_fenetre.close()
                self.page_connexion.show()
            else:
                QMessageBox.warning(self, "Erreur", "Échec de la suppression.")
                
        except Exception:
            QMessageBox.critical(self, "Erreur", "Serveur non disponible ")


# ============================
# FENÊTRE DE CHOIX DE SUJETS
# ============================
class FenetreChoixSujets(QWidget):
    """
    Fenêtre principale où les utilisateurs classent les sujets par ordre de préférence.
    Interface riche avec gestion des préférences et communication serveur.
    """
    def __init__(self, login, page_connexion):
        """
        Initialise la fenêtre de choix des sujets.
        
        Args:
            login: Identifiant de l'utilisateur
            page_connexion: Fenêtre de connexion parente
        """
        super().__init__()
        self.login = login
        self.page_connexion = page_connexion
        self.fenetre_changement_mdp = None
        self.fenetre_suppression = None
        
        # Structures de données pour la gestion des sujets
        self.sujets = []  # Liste des sujets disponibles
        self.combobox_dict = {}  # Dictionnaire des combobox par ID sujet
        self.spinbox_dict = {}   # Dictionnaire des spinbox par ID sujet
        self.preferences = {}    # Dictionnaire des préférences choisies
        
        # Configuration de la fenêtre
        self.setWindowTitle(f"Choix de sujets - {login}")
        self.showMaximized()
        self.setMinimumSize(self.screen().size())
        self.resize(self.screen().size())
        
        # Couleur de fond
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(70, 130, 180))
        self.setPalette(palette)
        
        # ======================
        # 1. CRÉATION DES WIDGETS
        # ======================
        
        # Zone haute : thème + menu utilisateur
        lbl_theme = QLabel("AttributionSujet")
        lbl_theme.setFont(QFont("Arial", 18, QFont.Bold))
        lbl_theme.setStyleSheet("color:white;")
        
        # Bouton menu utilisateur
        self.btn_menu_login = QPushButton(f"👤 {login}")
        self.btn_menu_login.setFixedWidth(200)
        self.btn_menu_login.setFont(QFont("Arial", 12, QFont.Bold))
        self.btn_menu_login.setStyleSheet("""
            QPushButton {
                color: white;
                background-color: rgba(255, 255, 255, 0.1);
                border: 2px solid white;
                border-radius: 12px;
                padding: 10px 15px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.2);
            }
            QPushButton::menu-indicator {
                image: none;
                width: 0px;
            }
        """)
        
        # Menu contextuel du bouton utilisateur
        self.menu_login = QMenu(self.btn_menu_login)
        self.menu_login.setStyleSheet("""
            QMenu {
                background-color: #4682B4;
                border: 2px solid white;
                border-radius: 8px;
                padding: 5px;
            }
            QMenu::item {
                color: white;
                padding: 8px 20px;
                border-radius: 5px;
                margin: 2px;
            }
            QMenu::item:selected {
                background-color: #5A9BD3;
            }
            QMenu::item:disabled {
                color: #AAAAAA;
            }
        """)
        
        # Actions du menu
        self.action_changer_mdp = self.menu_login.addAction("🔄 Changer le mot de passe")
        self.action_supprimer_compte = self.menu_login.addAction("🗑️ Supprimer mon compte")
        self.menu_login.addSeparator()
        self.action_rafraichir = self.menu_login.addAction("🔄 Rafraîchir la liste")
        self.menu_login.addSeparator()
        self.action_deconnexion = self.menu_login.addAction("🚪 Déconnexion")
        
        # Assignation du menu
        self.btn_menu_login.setMenu(self.menu_login)
        
        # Bouton rafraîchissement visible
        self.btn_rafraichir = QPushButton("🔄")
        self.btn_rafraichir.setFixedSize(40, 40)
        self.btn_rafraichir.setFont(QFont("Arial", 16))
        self.btn_rafraichir.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.15);
                color: white;
                border: 2px solid white;
                border-radius: 20px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.3);
                border: 2px solid #FFD700;
            }
            QPushButton:pressed {
                background-color: rgba(255, 215, 0, 0.5);
            }
        """)
        self.btn_rafraichir.setToolTip("Rafraîchir la liste des sujets")
        
        # Icône utilisateur
        lbl_icone = QLabel()
        try:
            lbl_icone.setPixmap(QPixmap("pv.png").scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        except:
            lbl_icone.setText("👤")
            lbl_icone.setFont(QFont("Arial", 20))
        
        # Layout pour la zone utilisateur
        box_user = QHBoxLayout()
        box_user.addWidget(lbl_icone)
        box_user.addWidget(self.btn_menu_login)
        box_user.addWidget(self.btn_rafraichir)
        box_user.setSpacing(10)
        
        # Bouton retour
        btn_retour = QPushButton("Retour à la connexion")
        btn_retour.setFont(QFont("Arial", 16))
        btn_retour.setStyleSheet("background:darkred; color:white; padding:10px; border-radius:10px;")
        btn_retour.clicked.connect(self.retour_connexion)
        
        # Layout de la zone haute
        layout_haut = QHBoxLayout()
        layout_haut.addWidget(lbl_theme)
        layout_haut.addStretch()
        layout_haut.addLayout(box_user)
        layout_haut.addSpacing(20)
        layout_haut.addWidget(btn_retour)
        
        # Titre principal
        titre = QLabel("📋 Classement des sujets par ordre de préférence")
        titre.setFont(QFont("Arial", 28, QFont.Bold))
        titre.setStyleSheet("color:white;")
        titre.setAlignment(Qt.AlignCenter)
        
        # Instructions détaillées
        instructions = QLabel(
            "<center>"
            "<b style='color:#FFD700;'>Instructions importantes :</b><br>"
            "1. <b>Attribuez un ordre de préférence à chaque sujet</b> (1 = préféré)<br>"
            "2. Chaque <b>numéro doit être unique</b> (pas de doublons)<br>"
            "3. Vous pouvez <b>ne pas classer tous les sujets</b><br>"
            "4. Les sujets non classés ne seront pas pris en compte"
            "</center>"
        )
        instructions.setFont(QFont("Arial", 12))
        instructions.setStyleSheet("""
            color: white; 
            background: rgba(0, 0, 0, 0.3); 
            padding: 15px; 
            border-radius: 10px;
            border: 2px solid #FFD700;
        """)
        instructions.setAlignment(Qt.AlignCenter)
        instructions.setWordWrap(True)
        
        # Zone défilante pour les sujets
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background: rgba(255, 255, 255, 0.1);
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: rgba(255, 255, 255, 0.5);
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(255, 255, 255, 0.8);
            }
        """)
        
        # Widget conteneur pour les sujets
        self.sujets_widget = QWidget()
        self.sujets_layout = QVBoxLayout(self.sujets_widget)
        self.sujets_layout.setSpacing(15)
        self.sujets_layout.setContentsMargins(20, 20, 20, 20)
        self.scroll_area.setWidget(self.sujets_widget)
        
        # Informations en bas
        info_label = QLabel("ℹ️ Sélectionnez les sujets qui vous intéressent en leur attribuant un ordre de préférence")
        info_label.setFont(QFont("Arial", 12))
        info_label.setStyleSheet("color: #81C784; background: rgba(0, 0, 0, 0.3); padding: 10px; border-radius: 8px;")
        info_label.setAlignment(Qt.AlignCenter)
        
        # Boutons d'action
        btn_valider = QPushButton(" Valider mes choix")
        btn_valider.setFont(QFont("Arial", 16))
        btn_valider.setStyleSheet("""
            QPushButton {
                background: #2E7D32;
                color: white;
                padding: 15px 30px;
                border-radius: 12px;
                font-weight: bold;
                border: 2px solid #4CAF50;
            }
            QPushButton:hover {
                background: #388E3C;
            }
            QPushButton:pressed {
                background: #1B5E20;
            }
        """)
        btn_valider.clicked.connect(self.valider_choix)
        
        btn_resultat = QPushButton("📊 Résultats")
        btn_resultat.setFont(QFont("Arial", 16))
        btn_resultat.setStyleSheet("""
            QPushButton {
                background: #1565C0;
                color: white;
                padding: 15px 30px;
                border-radius: 12px;
                font-weight: bold;
                border: 2px solid #2196F3;
            }
            QPushButton:hover {
                background: #1976D2;
            }
        """)
        btn_resultat.clicked.connect(self.afficher_resultats)
        
        # Bouton réinitialisation
        btn_reset = QPushButton("🔄 Réinitialiser")
        btn_reset.setFont(QFont("Arial", 14))
        btn_reset.setStyleSheet("""
            QPushButton {
                background: #FF8C00;
                color: white;
                padding: 10px 20px;
                border-radius: 8px;
                border: 2px solid #FFA500;
            }
            QPushButton:hover {
                background: #FF9900;
            }
        """)
        btn_reset.clicked.connect(self.reinitialiser_preferences)
        
        # Layout pour les boutons
        layout_boutons = QHBoxLayout()
        layout_boutons.setAlignment(Qt.AlignCenter)
        layout_boutons.setSpacing(20)
        layout_boutons.addWidget(btn_reset)
        layout_boutons.addWidget(btn_valider)
        layout_boutons.addWidget(btn_resultat)
        
        # Label de statut
        self.status_label = QLabel("Prêt - Connecté au serveur")
        self.status_label.setFont(QFont("Arial", 10))
        self.status_label.setStyleSheet("color: #FFD700; background: rgba(0, 0, 0, 0.3); padding: 8px; border-radius: 5px;")
        self.status_label.setAlignment(Qt.AlignCenter)
        
        # ======================
        # 3. LAYOUT PRINCIPAL
        # ======================
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.addLayout(layout_haut)
        layout.addWidget(titre)
        layout.addWidget(instructions)
        layout.addWidget(info_label)
        layout.addWidget(self.scroll_area, 1)  # 1 = étirement
        layout.addLayout(layout_boutons)
        layout.addWidget(self.status_label)
        layout.addSpacing(10)
        
        self.setLayout(layout)
        
        # ======================
        # 4. CHARGEMENT INITIAL
        # ======================
        self.charger_sujets()
        
        # ======================
        # 5. CONNEXION DES SIGNALS
        # ======================
        self.connecter_signals()
    
    def get_sujets_from_server(self):
        """
        Récupère la liste des sujets actifs depuis le serveur TCP.
        
        Returns:
            list: Liste des sujets disponibles
        """
        try:
            print("DEBUG: Récupération des sujets depuis le serveur...")
            client = socket.socket()
            client.settimeout(5)  # Timeout de 5 secondes
            client.connect((SERVER_IP, SERVER_PORT))
            
            # Demande des sujets actifs
            client.send("GET_ACTIVE_SUBJECTS".encode())
            reponse = client.recv(4096).decode()
            client.close()
            
            print(f"DEBUG: Réponse serveur: {reponse[:100]}...")
            
            if reponse.startswith("ACTIVE_SUBJECTS:"):
                # Extraction et conversion des données
                sujets_str = reponse[16:]  # Enlever "ACTIVE_SUBJECTS:"
                sujets = ast.literal_eval(sujets_str)
                return sujets
            else:
                print(f"DEBUG: Réponse inattendue: {reponse}")
                # Fallback vers la base locale
                return get_subjects()
                
        except socket.timeout:
            print("DEBUG: Timeout - Serveur ne répond pas")
            self.status_label.setText(" Serveur ne répond pas - Utilisation de la liste locale")
            return get_subjects()
        except ConnectionRefusedError:
            print("DEBUG: Connexion refusée")
            self.status_label.setText(" Serveur non disponible - Utilisation de la liste locale")
            return get_subjects()
        except Exception as e:
            print(f"DEBUG: Exception: {e}")
            self.status_label.setText(f" Erreur: {str(e)[:50]}...")
            return get_subjects()
    
    def connecter_signals(self):
        """Connecte les actions du menu aux méthodes correspondantes."""
        self.action_changer_mdp.triggered.connect(self.ouvrir_changement_mdp)
        self.action_supprimer_compte.triggered.connect(self.ouvrir_suppression_compte)
        self.action_rafraichir.triggered.connect(self.charger_sujets)
        self.action_deconnexion.triggered.connect(self.retour_connexion)
        self.btn_rafraichir.clicked.connect(self.charger_sujets)
    
    def charger_sujets(self):
        """
        Charge et affiche tous les sujets disponibles depuis le serveur.
        Organise l'affichage avec des spinbox pour le classement.
        """
        try:
            # Nettoyage du layout existant
            while self.sujets_layout.count():
                child = self.sujets_layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
            
            # Réinitialisation des structures de données
            self.combobox_dict = {}
            self.spinbox_dict = {}
            self.preferences = {}
            
            # Récupération des sujets
            self.status_label.setText("🔄 Récupération des sujets en cours...")
            QApplication.processEvents()  # Mise à jour immédiate de l'interface
            
            self.sujets = self.get_sujets_from_server()
            
            # Gestion du cas sans sujets
            if not self.sujets:
                lbl_aucun = QLabel("Aucun sujet disponible pour le moment.\nL'administrateur ajoutera des sujets bientôt.")
                lbl_aucun.setFont(QFont("Arial", 16))
                lbl_aucun.setStyleSheet("color: white; padding: 40px; text-align: center;")
                lbl_aucun.setAlignment(Qt.AlignCenter)
                self.sujets_layout.addWidget(lbl_aucun)
                self.status_label.setText(" Aucun sujet disponible")
                return
            
            # ======================
            # EN-TÊTE DES COLONNES
            # ======================
            header_widget = QWidget()
            header_layout = QHBoxLayout()
            header_layout.setContentsMargins(15, 5, 15, 5)
            
            lbl_header_sujet = QLabel("📝 SUJET")
            lbl_header_sujet.setFont(QFont("Arial", 14, QFont.Bold))
            lbl_header_sujet.setStyleSheet("color: #4DD0E1;")
            lbl_header_sujet.setFixedWidth(400)
            
            lbl_header_ordre = QLabel("🎯 ORDRE DE PRÉFÉRENCE")
            lbl_header_ordre.setFont(QFont("Arial", 14, QFont.Bold))
            lbl_header_ordre.setStyleSheet("color: #FFD700;")
            lbl_header_ordre.setFixedWidth(200)
            
            header_layout.addWidget(lbl_header_sujet)
            header_layout.addStretch()
            header_layout.addWidget(lbl_header_ordre)
            
            header_widget.setLayout(header_layout)
            self.sujets_layout.addWidget(header_widget)
            
            # ======================
            # AFFICHAGE DES SUJETS
            # ======================
            for sujet in self.sujets:
                _id = sujet[0]
                titre_sujet = sujet[1]
                description = sujet[2] if len(sujet) > 2 else ""
                
                # Création d'un frame pour chaque sujet
                sujet_frame = QFrame()
                sujet_frame.setStyleSheet("""
                    QFrame {
                        background-color: rgba(255, 255, 255, 0.1);
                        border-radius: 10px;
                        border: 1px solid rgba(255, 255, 255, 0.2);
                    }
                    QFrame:hover {
                        background-color: rgba(255, 255, 255, 0.15);
                        border: 1px solid rgba(255, 255, 255, 0.3);
                    }
                """)
                
                frame_layout = QHBoxLayout()
                frame_layout.setSpacing(15)
                frame_layout.setContentsMargins(15, 15, 15, 15)
                
                # Partie gauche : informations du sujet
                info_widget = QWidget()
                info_layout = QVBoxLayout()
                info_layout.setSpacing(5)
                
                # Titre du sujet
                lbl_titre = QLabel(titre_sujet)
                lbl_titre.setFont(QFont("Arial", 14, QFont.Bold))
                lbl_titre.setStyleSheet("color: #81C784;")
                lbl_titre.setWordWrap(True)
                
                # Description
                if description:
                    lbl_desc = QLabel(description)
                    lbl_desc.setFont(QFont("Arial", 12))
                    lbl_desc.setStyleSheet("color: #B0BEC5;")
                    lbl_desc.setWordWrap(True)
                else:
                    lbl_desc = QLabel("Aucune description fournie")
                    lbl_desc.setStyleSheet("color: #AAAAAA; font-style: italic;")
                    lbl_desc.setFont(QFont("Arial", 11))
                    lbl_desc.setWordWrap(True)
                
                # Détails (ID)
                lbl_details = QLabel(f"ID: {_id}")
                lbl_details.setFont(QFont("Arial", 11))
                lbl_details.setStyleSheet("color: #4DD0E1;")
                
                info_layout.addWidget(lbl_titre)
                info_layout.addWidget(lbl_desc)
                info_layout.addWidget(lbl_details)
                info_widget.setLayout(info_layout)
                
                # Partie droite : classement
                pref_widget = QWidget()
                pref_layout = QVBoxLayout()
                pref_layout.setAlignment(Qt.AlignCenter)
                
                # SpinBox pour choisir l'ordre (0 = non classé)
                spinbox = QSpinBox()
                spinbox.setRange(0, len(self.sujets))  # 0 = non classé
                spinbox.setValue(0)  # Par défaut à 0
                spinbox.setFont(QFont("Arial", 12))
                spinbox.setStyleSheet("""
                    QSpinBox {
                        background: white;
                        color: #2C3E50;
                        padding: 8px;
                        border-radius: 6px;
                        border: 2px solid #3498DB;
                        min-width: 80px;
                    }
                    QSpinBox::up-button, QSpinBox::down-button {
                        width: 25px;
                    }
                """)
                spinbox.setToolTip(f"Entrez l'ordre de préférence pour: {titre_sujet}\n0 = non classé")
                
                # Label explicatif
                lbl_instruction = QLabel("(0 = non classé)")
                lbl_instruction.setFont(QFont("Arial", 10))
                lbl_instruction.setStyleSheet("color: #FFD700;")
                lbl_instruction.setAlignment(Qt.AlignCenter)
                
                pref_layout.addWidget(spinbox)
                pref_layout.addWidget(lbl_instruction)
                pref_widget.setLayout(pref_layout)
                
                # Assemblage du frame
                frame_layout.addWidget(info_widget, 1)  # 1 = étirement
                frame_layout.addWidget(pref_widget)
                
                sujet_frame.setLayout(frame_layout)
                self.sujets_layout.addWidget(sujet_frame)
                
                # Stockage des références
                self.spinbox_dict[_id] = spinbox
                
                # Connexion du signal pour vérifier les doublons
                spinbox.valueChanged.connect(self.verifier_doublons)
            
            # Ajout d'un stretch à la fin
            self.sujets_layout.addStretch()
            
            # Mise à jour du statut
            self.status_label.setText(f"{len(self.sujets)} sujet(s) disponible(s) - Attribuez un ordre de préférence")
            
        except Exception as e:
            print(f"Erreur lors du chargement des sujets: {e}")
            self.status_label.setText(f" Erreur lors du chargement: {str(e)[:50]}")
            QMessageBox.critical(self, "Erreur", f"Impossible de charger les sujets: {e}")
    
    def verifier_doublons(self):
        """
        Vérifie s'il y a des doublons dans les ordres de préférence.
        Met en évidence visuellement les doublons détectés.
        """
        valeurs = {}
        doublons = []
        
        # Collecte des valeurs non nulles
        for sujet_id, spinbox in self.spinbox_dict.items():
            valeur = spinbox.value()
            if valeur > 0:  # Seulement les valeurs positives
                if valeur in valeurs:
                    valeurs[valeur].append(sujet_id)
                    doublons.append(valeur)
                else:
                    valeurs[valeur] = [sujet_id]
        
        # Mise en évidence visuelle des doublons
        for sujet_id, spinbox in self.spinbox_dict.items():
            valeur = spinbox.value()
            if valeur > 0 and valeur in doublons:
                # Doublon détecté : mise en rouge
                spinbox.setStyleSheet("""
                    QSpinBox {
                        background: #FFE0E0;
                        color: #D32F2F;
                        padding: 8px;
                        border-radius: 6px;
                        border: 2px solid #F44336;
                        min-width: 80px;
                    }
                """)
                spinbox.setToolTip(f"ATTENTION : L'ordre {valeur} est utilisé plusieurs fois !")
            elif valeur > 0:
                # Valeur unique : mise en vert
                spinbox.setStyleSheet("""
                    QSpinBox {
                        background: white;
                        color: #2C3E50;
                        padding: 8px;
                        border-radius: 6px;
                        border: 2px solid #4CAF50;
                        min-width: 80px;
                    }
                """)
                spinbox.setToolTip("OK - Ordre unique")
            else:
                # Valeur 0 (non classé) : mise en gris
                spinbox.setStyleSheet("""
                    QSpinBox {
                        background: #F5F5F5;
                        color: #757575;
                        padding: 8px;
                        border-radius: 6px;
                        border: 2px solid #BDBDBD;
                        min-width: 80px;
                    }
                """)
                spinbox.setToolTip("Non classé")
        
        # Mise à jour du message de statut
        if doublons:
            self.status_label.setText(f"⚠️ Attention : doublons détectés (ordres: {', '.join(map(str, doublons))})")
        else:
            self.status_label.setText("Aucun doublon détecté - Prêt à valider")
    
    def reinitialiser_preferences(self):
        """
        Réinitialise toutes les préférences à 0 (non classé).
        """
        for spinbox in self.spinbox_dict.values():
            spinbox.setValue(0)
        self.status_label.setText(" Toutes les préférences ont été réinitialisées")
    
    def valider_choix(self):
        """
        Valide les choix de sujets et envoie les préférences au serveur.
        Effectue plusieurs vérifications avant l'envoi.
        """
        # Vérification des doublons
        valeurs = {}
        doublons = []
        
        for sujet_id, spinbox in self.spinbox_dict.items():
            valeur = spinbox.value()
            if valeur > 0:
                if valeur in valeurs:
                    doublons.append(valeur)
                else:
                    valeurs[valeur] = sujet_id
        
        if doublons:
            QMessageBox.warning(self, "Erreur de classement", 
                f"<b>Des doublons ont été détectés !</b><br><br>"
                f"Les ordres suivants sont utilisés plusieurs fois :<br>"
                f"<b>{', '.join(map(str, doublons))}</b><br><br>"
                f"Chaque ordre de préférence doit être unique.")
            return
        
        # Collecte des préférences non nulles
        preferences = {}
        for sujet_id, spinbox in self.spinbox_dict.items():
            valeur = spinbox.value()
            if valeur > 0:
                preferences[sujet_id] = valeur
        
        # Vérification qu'au moins un sujet est classé
        if not preferences:
            QMessageBox.warning(self, "Erreur", "Veuillez attribuer un ordre de préférence à au moins un sujet.")
            return
        
        # Tri des préférences par ordre croissant
        sujets_tries = sorted(preferences.items(), key=lambda x: x[1])
        
        # ======================
        # CONFIRMATION VISUELLE
        # ======================
        msg = QMessageBox(self)
        msg.setWindowTitle("Confirmation des préférences")
        msg.setText(f"<h3>Vous avez classé {len(preferences)} sujet(s)</h3>")
        
        # Détails des préférences
        details = "<b>Vos préférences :</b><br><br>"
        for sujet_id, ordre in sujets_tries:
            # Recherche du titre du sujet
            titre = ""
            for s in self.sujets:
                if s[0] == sujet_id:
                    titre = s[1]
                    break
            details += f"<b>#{ordre}</b> → {titre}<br>"
        
        msg.setInformativeText(details)
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.Yes)
        
        if msg.exec_() == QMessageBox.Yes:
            try:
                self.status_label.setText("🔄 Envoi des préférences au serveur...")
                QApplication.processEvents()  # Mise à jour immédiate
                
                # Connexion au serveur
                client = socket.socket()
                client.settimeout(5)
                client.connect((SERVER_IP, SERVER_PORT))
                
                # Construction du message au format: PREFERENCES:login:id1=ordre1,id2=ordre2,...
                preferences_str = ",".join([f"{sujet_id}={ordre}" for sujet_id, ordre in preferences.items()])
                message = f"PREFERENCES:{self.login}:{preferences_str}"
                print(f"DEBUG: Message envoyé: {message}")
                
                # Envoi des préférences
                client.send(message.encode())
                
                # Réception de la réponse
                reponse = client.recv(1024).decode()
                client.close()
                
                print(f"DEBUG: Réponse serveur: '{reponse}'")
                
                # Traitement de la réponse
                if reponse == "PREFERENCES_ENREGISTREES":
                    self.status_label.setText("Préférences enregistrées avec succès")
                    QMessageBox.information(self, "Succès", 
                        "Vos préférences ont été enregistrées avec succès ! \n\n"
                        f"{len(preferences)} sujet(s) classé(s).")
                elif reponse == "PREFERENCES_VIDES":
                    QMessageBox.warning(self, "Erreur", "Aucune préférence n'a été spécifiée.")
                elif reponse == "PREFERENCES_INVALIDES":
                    QMessageBox.warning(self, "Erreur", "Format de préférences invalide.")
                else:
                    QMessageBox.warning(self, "Erreur", 
                        f"Erreur lors de l'enregistrement.\n"
                        f"Réponse serveur: {reponse}")
                            
            except socket.timeout:
                self.status_label.setText(" Timeout - Serveur ne répond pas")
                QMessageBox.critical(self, "Erreur", 
                    "Le serveur ne répond pas (timeout).")
            except ConnectionRefusedError:
                self.status_label.setText(" Serveur non disponible")
                QMessageBox.critical(self, "Erreur", 
                    "Impossible de se connecter au serveur.\n"
                    "Assurez-vous que le serveur est démarré.")
            except Exception as e:
                self.status_label.setText(f" Erreur: {str(e)[:30]}")
                QMessageBox.critical(self, "Erreur", 
                    f"Erreur de connexion au serveur:\n{str(e)}")
    
    def afficher_resultats(self):
        """
        Ouvre la fenêtre des résultats d'attribution des sujets.
        """
        print("DEBUG: Ouverture fenêtre résultats")
        try:
            # Masquage temporaire de la fenêtre actuelle
            self.hide()
            
            # Création et affichage de la fenêtre des résultats
            self.fenetre_resultats = ResultatsInterface(self.login, self)
            self.fenetre_resultats.show()
            
        except ImportError as e:
            QMessageBox.critical(self, "Erreur", 
                f"Module résultats non disponible:\n{e}\n\n"
                f"Assurez-vous que le fichier resultats_interface.py existe dans le même dossier.")
            self.show()  # Ré-affichage de la fenêtre actuelle
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible d'afficher les résultats: {e}")
            import traceback
            traceback.print_exc()
            self.show()  # Ré-affichage de la fenêtre actuelle
    
    def ouvrir_changement_mdp(self):
        """
        Ouvre la fenêtre de changement de mot de passe.
        """
        print("DEBUG: Ouverture fenêtre changement mdp")
        self.fenetre_changement_mdp = FenetrePageChangementMdp(self.login, self)
        self.fenetre_changement_mdp.show()
    
    def ouvrir_suppression_compte(self):
        """
        Ouvre la fenêtre de suppression de compte.
        """
        print("DEBUG: Ouverture fenêtre suppression compte")
        self.fenetre_suppression = FenetreSuppressionCompte(self.login, self, self.page_connexion)
        self.fenetre_suppression.show()
    
    def retour_connexion(self):
        """
        Retourne à la fenêtre de connexion principale.
        """
        self.close()
        self.page_connexion.show()


# ============================
# POINT D'ENTRÉE DE L'APPLICATION
# ============================
if __name__ == "__main__":
    """
    Point d'entrée principal de l'application.
    Initialise l'application PyQt et affiche la fenêtre de connexion.
    """
    app = QApplication(sys.argv)  # Création de l'application
    f = FenetreConnexion()        # Création de la fenêtre principale
    f.show()                      # Affichage de la fenêtre
    sys.exit(app.exec_())         # Lancement de la boucle d'événements