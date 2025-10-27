import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPalette, QColor
from module_Attribution_sujets_pyqt import init_db, register_user, login_user


class FenetreConnexion(QWidget):
    """Fenêtre de connexion principale de l'application.

    Permet à l'utilisateur de se connecter ou d'accéder
    à la création d'un nouveau compte.
    """

    def __init__(self):
        """Initialise la fenêtre de connexion."""
        super().__init__()
        self.setWindowTitle("Connexion - Attribution de sujets")
        self.showMaximized()

        # Palette de couleurs sombre
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(20, 20, 40))
        self.setPalette(palette)

        # Polices
        font_titre = QFont("Consolas", 14, QFont.Bold)
        font_input = QFont("Consolas", 12)

        # Titre centré
        titre = QLabel("Connexion")
        titre.setAlignment(Qt.AlignCenter)
        titre.setFont(font_titre)
        titre.setStyleSheet("color: cyan; margin-bottom: 40px;")

        # Champs de saisie
        self.login = QLineEdit()
        self.login.setPlaceholderText("Login")
        self.login.setFont(font_input)
        self.login.setStyleSheet(self.style_input())

        self.password = QLineEdit()
        self.password.setPlaceholderText("Mot de passe")
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setFont(font_input)
        self.password.setStyleSheet(self.style_input())

        # Boutons
        self.btn_connexion = QPushButton("Se connecter")
        self.btn_creer = QPushButton("Créer un compte")

        # Style des boutons
        self.btn_connexion.setFont(font_input)
        self.btn_creer.setFont(font_input)
        bouton_style = """
            QPushButton {
                background-color: cyan;
                color: black;
                padding: 12px;
                border-radius: 10px;
                margin-top: 20px;
            }
            QPushButton:hover {
                background-color: #00bfff;
            }
        """
        self.btn_connexion.setStyleSheet(bouton_style)
        self.btn_creer.setStyleSheet(bouton_style)

        # Layout principal
        layout = QVBoxLayout()
        layout.addWidget(titre)
        layout.addWidget(self.login)
        layout.addWidget(self.password)
        layout.addWidget(self.btn_connexion)
        layout.addWidget(self.btn_creer)
        layout.setAlignment(Qt.AlignTop)
        layout.setContentsMargins(150, 100, 150, 50)
        layout.setSpacing(30)
        self.setLayout(layout)

        # Connexions des boutons
        self.btn_connexion.clicked.connect(self.connexion)
        self.btn_creer.clicked.connect(self.creation)

    def style_input(self):
        """Retourne le style appliqué aux champs de saisie."""
        return """
            QLineEdit {
                background-color: #1c1c3c;
                border: 1px solid white;
                color: white;
                padding: 10px;
                border-radius: 5px;
            }
            QLineEdit:focus {
                border: 1px solid cyan;
            }
        """

    def connexion(self):
        """Gère la tentative de connexion de l'utilisateur."""
        if login_user(self.login.text(), self.password.text()):
            QMessageBox.information(self, "Succès", "Connexion réussie")
            self.hide()
        else:
            QMessageBox.warning(self, "Erreur", "Identifiants incorrects")

    def creation(self):
        """Ouvre la fenêtre de création de compte."""
        self.fen_creation = FenetreCreationCompte()
        self.fen_creation.show()


class FenetreCreationCompte(QWidget):
    """Fenêtre de création de compte utilisateur."""

    def __init__(self):
        """Initialise la fenêtre de création de compte."""
        super().__init__()
        self.setWindowTitle("Création de compte")
        self.showMaximized()

        # Fond sombre
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(20, 20, 40))
        self.setPalette(palette)

        # Polices
        font_titre = QFont("Consolas", 14, QFont.Bold)
        font_input = QFont("Consolas", 12)

        # Titre
        titre = QLabel("Création de compte")
        titre.setAlignment(Qt.AlignCenter)
        titre.setFont(font_titre)
        titre.setStyleSheet("color: cyan; margin-bottom: 40px;")

        # Champs de saisie
        self.nom = QLineEdit()
        self.nom.setPlaceholderText("Nom")
        self.nom.setFont(font_input)
        self.nom.setStyleSheet(self.style_input())

        self.prenom = QLineEdit()
        self.prenom.setPlaceholderText("Prénom")
        self.prenom.setFont(font_input)
        self.prenom.setStyleSheet(self.style_input())

        self.login = QLineEdit()
        self.login.setPlaceholderText("Email / Login")
        self.login.setFont(font_input)
        self.login.setStyleSheet(self.style_input())

        self.password = QLineEdit()
        self.password.setPlaceholderText("Mot de passe")
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setFont(font_input)
        self.password.setStyleSheet(self.style_input())

        # Bouton
        self.btn_valider = QPushButton("Créer le compte")
        self.btn_valider.setFont(QFont("Consolas", 12, QFont.Bold))
        self.btn_valider.setStyleSheet("""
            QPushButton {
                background-color: cyan;
                color: black;
                padding: 12px;
                border-radius: 10px;
                margin-top: 20px;
            }
            QPushButton:hover {
                background-color: #00bfff;
            }
        """)
        self.btn_valider.clicked.connect(self.creer_compte)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(titre)
        layout.addWidget(self.nom)
        layout.addWidget(self.prenom)
        layout.addWidget(self.login)
        layout.addWidget(self.password)
        layout.addWidget(self.btn_valider)
        layout.setAlignment(Qt.AlignTop)
        layout.setContentsMargins(150, 100, 150, 50)
        layout.setSpacing(30)
        self.setLayout(layout)

    def style_input(self):
        """Retourne le style des champs de saisie."""
        return """
            QLineEdit {
                background-color: #1c1c3c;
                border: 1px solid white;
                color: white;
                padding: 10px;
                border-radius: 5px;
            }
            QLineEdit:focus {
                border: 1px solid cyan;
            }
        """

    def creer_compte(self):
        """Valide les champs et enregistre le compte dans la base de données."""
        nom = self.nom.text()
        prenom = self.prenom.text()
        login = self.login.text()
        password = self.password.text()

        if not all([nom, prenom, login, password]):
            QMessageBox.warning(self, "Erreur", "Tous les champs doivent être remplis")
            return

        if register_user(nom, prenom, login, password):
            QMessageBox.information(self, "Succès", "Compte créé")
            self.close()
        else:
            QMessageBox.warning(self, "Erreur", "Ce login existe déjà")


if __name__ == "__main__":
    init_db()
    app = QApplication(sys.argv)
    fen = FenetreConnexion()
    fen.show()
    sys.exit(app.exec_())
