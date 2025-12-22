import sys
import socket
import ast
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QDateTime
from PyQt5.QtGui import QFont, QPalette, QColor
from datetime import datetime

SERVER_IP = "127.0.0.1"
SERVER_PORT = 55555

# ============================
# Panneau d'administration principal
# ============================
class AdminPanel(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Panneau d'Administration - Attribution des Sujets")
        self.showMaximized()
        
        # Configuration de la fenêtre
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(40, 40, 60))
        self.setPalette(palette)
        
        # Barre de statut
        self.statusBar().showMessage("Mode Administrateur - Connecté")
        self.statusBar().setStyleSheet("""
            QStatusBar {
                background: #2A2A3A;
                color: #FFD700;
                font-weight: bold;
                border-top: 2px solid #FFD700;
            }
        """)
        
        # Menu principal
        self.create_menu()
        
        # Zone centrale avec onglets
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 2px solid #FFD700;
                background: #2A2A3A;
                border-radius: 10px;
            }
            QTabBar::tab {
                background: #4A4A6A;
                color: white;
                padding: 12px 24px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-size: 13px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background: #FFD700;
                color: #333;
            }
            QTabBar::tab:hover {
                background: #5A5A7A;
            }
        """)
        
        # Création des onglets
        self.tab_gestion_sujets = QWidget()
        self.tab_gestion_utilisateurs = QWidget()
        self.tab_configuration = QWidget()
        self.tab_statistiques = QWidget()
        
        self.tab_widget.addTab(self.tab_gestion_sujets, "📝 Sujets")
        self.tab_widget.addTab(self.tab_gestion_utilisateurs, "👥 Utilisateurs")
        self.tab_widget.addTab(self.tab_configuration, "⚙️ Configuration")
        self.tab_widget.addTab(self.tab_statistiques, "📊 Statistiques")
        
        self.setCentralWidget(self.tab_widget)
        
        # Initialiser les onglets
        self.init_tab_gestion_sujets()
        self.init_tab_gestion_utilisateurs()
        self.init_tab_configuration()
        self.init_tab_statistiques()
        
        # Charger les données
        self.load_sujets()
        self.load_utilisateurs()
        self.load_config()
        self.actualiser_statistiques()
    
    def create_menu(self):
        menubar = self.menuBar()
        menubar.setStyleSheet("""
            QMenuBar {
                background: #2A2A3A;
                color: white;
                border-bottom: 2px solid #FFD700;
            }
            QMenuBar::item:selected {
                background: #FFD700;
                color: #333;
            }
        """)
        
        # Menu Fichier
        menu_fichier = menubar.addMenu("📁 Fichier")
        
        action_actualiser = menu_fichier.addAction("🔄 Actualiser")
        action_actualiser.setShortcut("F5")
        action_actualiser.triggered.connect(self.actualiser_donnees)
        
        menu_fichier.addSeparator()
        
        action_deconnexion = menu_fichier.addAction("👤 Déconnexion")
        action_deconnexion.setShortcut("Ctrl+Q")
        action_deconnexion.triggered.connect(self.deconnexion)
        
        # Menu Aide
        menu_aide = menubar.addMenu("❓ Aide")
        
        action_apropos = menu_aide.addAction("ℹ️ À propos")
        action_apropos.triggered.connect(self.afficher_a_propos)
    
    def init_tab_gestion_sujets(self):
        layout = QVBoxLayout()
        
        # En-tête avec boutons
        header = QHBoxLayout()
        
        lbl_titre = QLabel("📝 Gestion des Sujets")
        lbl_titre.setStyleSheet("color: #FFD700; font-size: 20px; font-weight: bold;")
        header.addWidget(lbl_titre)
        header.addStretch()
        
        # Boutons d'action
        btn_ajouter = QPushButton("➕ Ajouter")
        btn_ajouter.setStyleSheet("""
            QPushButton {
                background: #4CAF50;
                color: white;
                padding: 8px 16px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #66BB6A;
            }
        """)
        btn_ajouter.clicked.connect(self.ajouter_sujet)
        
        btn_modifier = QPushButton("✏️ Modifier")
        btn_modifier.setStyleSheet("""
            QPushButton {
                background: #2196F3;
                color: white;
                padding: 8px 16px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background: #42A5F5;
            }
        """)
        btn_modifier.clicked.connect(self.modifier_sujet)
        
        btn_supprimer = QPushButton("🗑️ Supprimer")
        btn_supprimer.setStyleSheet("""
            QPushButton {
                background: #F44336;
                color: white;
                padding: 8px 16px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background: #EF5350;
            }
        """)
        btn_supprimer.clicked.connect(self.supprimer_sujet)
        
        header.addWidget(btn_ajouter)
        header.addWidget(btn_modifier)
        header.addWidget(btn_supprimer)
        
        layout.addLayout(header)
        
        # Table des sujets
        self.table_sujets = QTableWidget()
        self.table_sujets.setColumnCount(6)
        self.table_sujets.setHorizontalHeaderLabels([
            "ID", "Titre", "Description", "Places Max", 
            "Date Limite", "Actif"
        ])
        self.table_sujets.horizontalHeader().setStretchLastSection(True)
        self.table_sujets.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_sujets.setStyleSheet("""
            QTableWidget {
                background: white;
                gridline-color: #CCC;
                font-size: 12px;
                border: 2px solid #FFD700;
                border-radius: 5px;
            }
            QHeaderView::section {
                background: #FFD700;
                color: #333;
                padding: 10px;
                font-weight: bold;
                border: 1px solid #CCC;
            }
            QTableWidget::item:selected {
                background-color: #FFD700;
                color: #333;
            }
        """)
        
        layout.addWidget(self.table_sujets)
        
        self.tab_gestion_sujets.setLayout(layout)
    
    def init_tab_gestion_utilisateurs(self):
        layout = QVBoxLayout()
        
        # En-tête
        header = QHBoxLayout()
        lbl_titre = QLabel("👥 Gestion des Utilisateurs")
        lbl_titre.setStyleSheet("color: #FFD700; font-size: 20px; font-weight: bold;")
        header.addWidget(lbl_titre)
        header.addStretch()
        
        layout.addLayout(header)
        
        # Table des utilisateurs
        self.table_utilisateurs = QTableWidget()
        self.table_utilisateurs.setColumnCount(6)
        self.table_utilisateurs.setHorizontalHeaderLabels([
            "ID", "Nom", "Prénom", "Login", 
            "Date Inscription", "Nb Choix"
        ])
        self.table_utilisateurs.horizontalHeader().setStretchLastSection(True)
        self.table_utilisateurs.setStyleSheet("""
            QTableWidget {
                background: white;
                gridline-color: #CCC;
                font-size: 12px;
                border: 2px solid #4CAF50;
                border-radius: 5px;
            }
            QHeaderView::section {
                background: #4CAF50;
                color: white;
                padding: 10px;
                font-weight: bold;
                border: 1px solid #CCC;
            }
        """)
        
        layout.addWidget(self.table_utilisateurs)
        
        self.tab_gestion_utilisateurs.setLayout(layout)
    
    def init_tab_configuration(self):
        layout = QVBoxLayout()
        layout.setSpacing(25)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Titre
        lbl_titre = QLabel("⚙️ Configuration du Système")
        lbl_titre.setStyleSheet("color: #FFD700; font-size: 24px; font-weight: bold;")
        lbl_titre.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(lbl_titre)
        layout.addSpacing(30)
        
        # Paramètres
        frame_params = QFrame()
        frame_params.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 15px;
                border: 2px solid #FFD700;
                padding: 25px;
            }
        """)
        
        layout_params = QVBoxLayout()
        
        # Nombre de choix
        hbox_choix = QHBoxLayout()
        lbl_nb_choix = QLabel("Nombre maximum de choix par personne:")
        lbl_nb_choix.setStyleSheet("color: white; font-size: 14px; min-width: 300px;")
        
        self.spin_nb_choix = QSpinBox()
        self.spin_nb_choix.setRange(1, 10)
        self.spin_nb_choix.setValue(3)
        self.spin_nb_choix.setStyleSheet("""
            QSpinBox {
                background: white;
                padding: 10px;
                border-radius: 8px;
                font-size: 14px;
                min-width: 100px;
                border: 2px solid #4CAF50;
            }
        """)
        
        hbox_choix.addWidget(lbl_nb_choix)
        hbox_choix.addWidget(self.spin_nb_choix)
        hbox_choix.addStretch()
        
        # Activation système
        hbox_actif = QHBoxLayout()
        self.check_actif = QCheckBox("Système actif (les stagiaires peuvent faire leurs choix)")
        self.check_actif.setChecked(True)
        self.check_actif.setStyleSheet("color: white; font-size: 14px;")
        
        hbox_actif.addWidget(self.check_actif)
        hbox_actif.addStretch()
        
        layout_params.addLayout(hbox_choix)
        layout_params.addLayout(hbox_actif)
        layout_params.addSpacing(20)
        
        # Bouton sauvegarde
        btn_sauvegarder = QPushButton("💾 Sauvegarder la configuration")
        btn_sauvegarder.setStyleSheet("""
            QPushButton {
                background: #4CAF50;
                color: white;
                padding: 15px 25px;
                border-radius: 10px;
                font-size: 14px;
                font-weight: bold;
                border: 2px solid white;
            }
            QPushButton:hover {
                background: #66BB6A;
            }
        """)
        btn_sauvegarder.clicked.connect(self.sauvegarder_config)
        
        layout_params.addWidget(btn_sauvegarder, 0, Qt.AlignCenter)
        
        frame_params.setLayout(layout_params)
        layout.addWidget(frame_params)
        layout.addStretch()
        
        self.tab_configuration.setLayout(layout)
    
    def init_tab_statistiques(self):
        layout = QVBoxLayout()
        
        # En-tête
        header = QHBoxLayout()
        lbl_titre = QLabel("📊 Statistiques")
        lbl_titre.setStyleSheet("color: #FFD700; font-size: 20px; font-weight: bold;")
        
        btn_actualiser = QPushButton("🔄 Actualiser")
        btn_actualiser.setStyleSheet("""
            QPushButton {
                background: #2196F3;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background: #42A5F5;
            }
        """)
        btn_actualiser.clicked.connect(self.actualiser_statistiques)
        
        header.addWidget(lbl_titre)
        header.addStretch()
        header.addWidget(btn_actualiser)
        
        layout.addLayout(header)
        
        # Widget de statistiques
        self.text_stats = QTextEdit()
        self.text_stats.setReadOnly(True)
        self.text_stats.setStyleSheet("""
            QTextEdit {
                background: white;
                font-size: 14px;
                border: 2px solid #2196F3;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        
        layout.addWidget(self.text_stats)
        
        self.tab_statistiques.setLayout(layout)
    
    # ============================
    # Fonctions de communication avec le serveur
    # ============================
    
    def envoyer_requete(self, message):
        """Envoie une requête au serveur et retourne la réponse"""
        try:
            client = socket.socket()
            client.connect((SERVER_IP, SERVER_PORT))
            client.send(message.encode())
            reponse = client.recv(4096).decode()
            client.close()
            return reponse
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible de communiquer avec le serveur: {e}")
            return None
    
    def load_sujets(self):
        """Charge la liste des sujets depuis le serveur"""
        try:
            reponse = self.envoyer_requete("GET_ALL_SUBJECTS")
            if not reponse:
                return
            
            if reponse.startswith("SUJETS:"):
                # Convertir la chaîne en liste
                sujets_str = reponse[7:]  # Enlever "SUJETS:"
                try:
                    sujets = ast.literal_eval(sujets_str)
                    
                    self.table_sujets.setRowCount(len(sujets))
                    for row, sujet in enumerate(sujets):
                        for col in range(6):  # 6 colonnes
                            valeur = sujet[col] if col < len(sujet) else ""
                            item = QTableWidgetItem(str(valeur))
                            
                            # Colorer la colonne "Actif"
                            if col == 5:  # Colonne Actif
                                if valeur == 1 or str(valeur).lower() in ['true', '1', 'oui', 'yes']:
                                    item.setText("✓ Actif")
                                    item.setForeground(QColor(0, 150, 0))
                                else:
                                    item.setText("✗ Inactif")
                                    item.setForeground(QColor(200, 0, 0))
                            
                            self.table_sujets.setItem(row, col, item)
                    
                    self.table_sujets.resizeColumnsToContents()
                    
                except Exception as e:
                    QMessageBox.critical(self, "Erreur", f"Erreur lors du traitement des données: {e}")
            else:
                QMessageBox.warning(self, "Erreur", f"Réponse inattendue du serveur: {reponse}")
                
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible de charger les sujets: {e}")
    
    def load_utilisateurs(self):
        """Charge la liste des utilisateurs depuis le serveur"""
        try:
            reponse = self.envoyer_requete("GET_ALL_USERS")
            if not reponse:
                return
            
            if reponse.startswith("UTILISATEURS:"):
                # Convertir la chaîne en liste
                users_str = reponse[13:]  # Enlever "UTILISATEURS:"
                try:
                    utilisateurs = ast.literal_eval(users_str)
                    
                    self.table_utilisateurs.setRowCount(len(utilisateurs))
                    for row, user in enumerate(utilisateurs):
                        for col in range(6):  # 6 colonnes
                            valeur = user[col] if col < len(user) else ""
                            item = QTableWidgetItem(str(valeur))
                            
                            # Colorer la colonne "Nb Choix"
                            if col == 5:  # Colonne Nb Choix
                                try:
                                    nb = int(valeur)
                                    if nb == 0:
                                        item.setForeground(QColor(255, 0, 0))
                                    elif nb >= 3:
                                        item.setForeground(QColor(0, 150, 0))
                                except:
                                    pass
                            
                            self.table_utilisateurs.setItem(row, col, item)
                    
                    self.table_utilisateurs.resizeColumnsToContents()
                    
                except Exception as e:
                    QMessageBox.critical(self, "Erreur", f"Erreur lors du traitement des données: {e}")
            else:
                QMessageBox.warning(self, "Erreur", f"Réponse inattendue du serveur: {reponse}")
                
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible de charger les utilisateurs: {e}")
    
    def ajouter_sujet(self):
        """Ouvre une fenêtre pour ajouter un sujet"""
        dialog = QDialog(self)
        dialog.setWindowTitle("➕ Ajouter un nouveau sujet")
        dialog.setFixedSize(500, 450)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)
        
        # Titre
        lbl_titre = QLabel("Nouveau Sujet")
        lbl_titre.setStyleSheet("font-size: 18px; font-weight: bold; color: #FFD700;")
        lbl_titre.setAlignment(Qt.AlignCenter)
        
        # Formulaire
        lbl_nom = QLabel("Titre du sujet:")
        self.edit_nom = QLineEdit()
        self.edit_nom.setPlaceholderText("Ex: Projet Réseau")
        
        lbl_desc = QLabel("Description:")
        self.edit_desc = QTextEdit()
        self.edit_desc.setMaximumHeight(100)
        self.edit_desc.setPlaceholderText("Décrivez le sujet...")
        
        lbl_capacite = QLabel("Capacité maximale (nombre de personnes):")
        self.spin_capacite = QSpinBox()
        self.spin_capacite.setRange(1, 50)
        self.spin_capacite.setValue(3)
        
        lbl_date = QLabel("Date limite:")
        self.edit_date = QDateEdit()
        self.edit_date.setCalendarPopup(True)
        self.edit_date.setDate(QDateTime.currentDateTime().date().addDays(60))
        
        # Boutons
        hbox_boutons = QHBoxLayout()
        btn_annuler = QPushButton("Annuler")
        btn_annuler.clicked.connect(dialog.reject)
        
        btn_valider = QPushButton("Ajouter")
        btn_valider.setStyleSheet("background: #4CAF50; color: white; font-weight: bold;")
        
        hbox_boutons.addWidget(btn_annuler)
        hbox_boutons.addWidget(btn_valider)
        
        # Assemblage
        layout.addWidget(lbl_titre)
        layout.addWidget(lbl_nom)
        layout.addWidget(self.edit_nom)
        layout.addWidget(lbl_desc)
        layout.addWidget(self.edit_desc)
        layout.addWidget(lbl_capacite)
        layout.addWidget(self.spin_capacite)
        layout.addWidget(lbl_date)
        layout.addWidget(self.edit_date)
        layout.addSpacing(20)
        layout.addLayout(hbox_boutons)
        
        def valider_ajout():
            titre = self.edit_nom.text().strip()
            description = self.edit_desc.toPlainText().strip()
            capacite = self.spin_capacite.value()
            date_limite = self.edit_date.date().toString("yyyy-MM-dd")
            
            if not titre:
                QMessageBox.warning(dialog, "Erreur", "Le titre du sujet est obligatoire.")
                return
            
            # Envoyer la requête au serveur
            message = f"ADD_SUBJECT:{titre}:{description}:{capacite}:{date_limite}"
            reponse = self.envoyer_requete(message)
            
            if reponse == "SUBJECT_ADDED":
                QMessageBox.information(self, "Succès", "Sujet ajouté avec succès!")
                self.load_sujets()
                dialog.accept()
            else:
                QMessageBox.warning(self, "Erreur", f"Échec de l'ajout: {reponse}")
        
        btn_valider.clicked.connect(valider_ajout)
        dialog.setLayout(layout)
        dialog.exec_()
    
    def modifier_sujet(self):
        """Modifie le sujet sélectionné"""
        selected_row = self.table_sujets.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner un sujet à modifier.")
            return
        
        # Récupérer les données du sujet sélectionné
        sujet_id = self.table_sujets.item(selected_row, 0).text()
        titre = self.table_sujets.item(selected_row, 1).text()
        description = self.table_sujets.item(selected_row, 2).text()
        capacite = self.table_sujets.item(selected_row, 3).text()
        date_limite = self.table_sujets.item(selected_row, 4).text()
        actif_item = self.table_sujets.item(selected_row, 5)
        actif = "Actif" in actif_item.text() if actif_item else True
        
        # Créer la boîte de dialogue de modification
        dialog = QDialog(self)
        dialog.setWindowTitle("✏️ Modifier le sujet")
        dialog.setFixedSize(500, 500)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)
        
        # Titre
        lbl_titre = QLabel(f"Modifier le sujet: {titre}")
        lbl_titre.setStyleSheet("font-size: 18px; font-weight: bold; color: #FFD700;")
        lbl_titre.setAlignment(Qt.AlignCenter)
        
        # Formulaire
        lbl_nom = QLabel("Titre du sujet:")
        self.edit_nom_modif = QLineEdit()
        self.edit_nom_modif.setText(titre)
        
        lbl_desc = QLabel("Description:")
        self.edit_desc_modif = QTextEdit()
        self.edit_desc_modif.setText(description)
        self.edit_desc_modif.setMaximumHeight(100)
        
        lbl_capacite = QLabel("Capacité maximale (nombre de personnes):")
        self.spin_capacite_modif = QSpinBox()
        self.spin_capacite_modif.setRange(1, 50)
        self.spin_capacite_modif.setValue(int(capacite))
        
        lbl_date = QLabel("Date limite:")
        self.edit_date_modif = QDateEdit()
        self.edit_date_modif.setCalendarPopup(True)
        try:
            date_obj = QDateTime.fromString(date_limite, "yyyy-MM-dd")
            self.edit_date_modif.setDate(date_obj.date())
        except:
            self.edit_date_modif.setDate(QDateTime.currentDateTime().date().addDays(60))
        
        lbl_actif = QLabel("Statut:")
        self.check_actif_modif = QCheckBox("Sujet actif")
        self.check_actif_modif.setChecked(actif)
        
        # Boutons
        hbox_boutons = QHBoxLayout()
        btn_annuler = QPushButton("Annuler")
        btn_annuler.clicked.connect(dialog.reject)
        
        btn_valider = QPushButton("Enregistrer")
        btn_valider.setStyleSheet("background: #2196F3; color: white; font-weight: bold;")
        
        hbox_boutons.addWidget(btn_annuler)
        hbox_boutons.addWidget(btn_valider)
        
        # Assemblage
        layout.addWidget(lbl_titre)
        layout.addWidget(lbl_nom)
        layout.addWidget(self.edit_nom_modif)
        layout.addWidget(lbl_desc)
        layout.addWidget(self.edit_desc_modif)
        layout.addWidget(lbl_capacite)
        layout.addWidget(self.spin_capacite_modif)
        layout.addWidget(lbl_date)
        layout.addWidget(self.edit_date_modif)
        layout.addWidget(lbl_actif)
        layout.addWidget(self.check_actif_modif)
        layout.addSpacing(20)
        layout.addLayout(hbox_boutons)
        
        def valider_modification():
            nouveau_titre = self.edit_nom_modif.text().strip()
            nouvelle_description = self.edit_desc_modif.toPlainText().strip()
            nouvelle_capacite = self.spin_capacite_modif.value()
            nouvelle_date = self.edit_date_modif.date().toString("yyyy-MM-dd")
            nouvel_actif = self.check_actif_modif.isChecked()
            
            if not nouveau_titre:
                QMessageBox.warning(dialog, "Erreur", "Le titre du sujet est obligatoire.")
                return
            
            # Envoyer la requête au serveur
            message = f"UPDATE_SUBJECT:{sujet_id}:{nouveau_titre}:{nouvelle_description}:{nouvelle_capacite}:{nouvelle_date}:{nouvel_actif}"
            reponse = self.envoyer_requete(message)
            
            if reponse == "SUBJECT_UPDATED":
                QMessageBox.information(self, "Succès", "Sujet modifié avec succès!")
                self.load_sujets()
                dialog.accept()
            else:
                QMessageBox.warning(self, "Erreur", f"Échec de la modification: {reponse}")
        
        btn_valider.clicked.connect(valider_modification)
        dialog.setLayout(layout)
        dialog.exec_()
    
    def supprimer_sujet(self):
        """Supprime le sujet sélectionné"""
        selected_row = self.table_sujets.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner un sujet à supprimer.")
            return
        
        sujet_id = self.table_sujets.item(selected_row, 0).text()
        sujet_titre = self.table_sujets.item(selected_row, 1).text()
        
        # Demander confirmation
        reponse = QMessageBox.question(
            self,
            "Confirmation",
            f"Êtes-vous sûr de vouloir supprimer le sujet :\n\n<b>{sujet_titre}</b> ?\n\nCette action est irréversible.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reponse == QMessageBox.Yes:
            # Envoyer la requête de suppression
            message = f"DELETE_SUBJECT:{sujet_id}"
            reponse_serveur = self.envoyer_requete(message)
            
            if reponse_serveur == "SUBJECT_DELETED":
                QMessageBox.information(self, "Succès", "Sujet supprimé avec succès!")
                self.load_sujets()
            else:
                QMessageBox.warning(self, "Erreur", f"Échec de la suppression: {reponse_serveur}")
    
    def load_config(self):
        """Charge la configuration actuelle"""
        # Pour l'instant, valeurs par défaut
        self.spin_nb_choix.setValue(3)
        self.check_actif.setChecked(True)
    
    def sauvegarder_config(self):
        """Sauvegarde la configuration"""
        nb_choix = self.spin_nb_choix.value()
        actif = self.check_actif.isChecked()
        
        # À implémenter: sauvegarde dans la base de données
        QMessageBox.information(self, "Succès", 
            f"Configuration sauvegardée!\n\n"
            f"• Choix max par personne: {nb_choix}\n"
            f"• Système actif: {'Oui' if actif else 'Non'}")
    
    def actualiser_statistiques(self):
        """Actualise les statistiques"""
        try:
            # Récupérer les données
            sujets = self.table_sujets.rowCount()
            utilisateurs = self.table_utilisateurs.rowCount()
            
            # Calculer le nombre total de choix
            total_choix = 0
            for row in range(utilisateurs):
                item = self.table_utilisateurs.item(row, 5)
                if item:
                    try:
                        total_choix += int(item.text())
                    except:
                        pass
            
            # Calculer la moyenne
            moyenne = total_choix / utilisateurs if utilisateurs > 0 else 0
            
            # Générer le HTML des statistiques
            stats_html = f"""
            <div style='font-family: Arial;'>
                <h2 style='color: #FFD700;'>📊 Statistiques en temps réel</h2>
                <hr>
                
                <h3>📈 Vue d'ensemble</h3>
                <table style='width: 100%;'>
                    <tr>
                        <td><b>Nombre total d'utilisateurs:</b></td>
                        <td style='text-align: right; color: #4CAF50;'>{utilisateurs}</td>
                    </tr>
                    <tr>
                        <td><b>Nombre total de sujets:</b></td>
                        <td style='text-align: right; color: #2196F3;'>{sujets}</td>
                    </tr>
                    <tr>
                        <td><b>Total des choix effectués:</b></td>
                        <td style='text-align: right; color: #9C27B0;'>{total_choix}</td>
                    </tr>
                    <tr>
                        <td><b>Choix moyens par utilisateur:</b></td>
                        <td style='text-align: right; color: #FF9800;'>{moyenne:.1f}</td>
                    </tr>
                </table>
                
                <h3>📅 Dernière mise à jour</h3>
                <p><i>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i></p>
                
                <h3>💡 Recommandations</h3>
                <ul>
                    <li>Vérifiez régulièrement les sujets inactifs</li>
                    <li>Encouragez les utilisateurs sans choix</li>
                    <li>Mettez à jour les dates limites</li>
                </ul>
            </div>
            """
            
            self.text_stats.setHtml(stats_html)
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de l'actualisation des statistiques: {e}")
    
    def actualiser_donnees(self):
        """Actualise manuellement toutes les données"""
        self.load_sujets()
        self.load_utilisateurs()
        self.load_config()
        self.actualiser_statistiques()
        QMessageBox.information(self, "Actualisation", "✅ Données actualisées avec succès!")
    
    def deconnexion(self):
        """Déconnexion de l'admin"""
        reponse = QMessageBox.question(
            self,
            "Déconnexion",
            "Voulez-vous vraiment vous déconnecter ?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reponse == QMessageBox.Yes:
            self.close()
            # Retour à la fenêtre de connexion principale
            if hasattr(self, 'parent_fenetre'):
                self.parent_fenetre.show()
    
    def afficher_a_propos(self):
        """Affiche la boîte À propos"""
        QMessageBox.about(self, "À propos",
            "<h2>AttributionSujet - Administration</h2>"
            "<p><b>Version:</b> 1.1.0</p>"
            "<p><b>Fonctionnalités:</b></p>"
            "<ul>"
            "<li>Gestion complète des sujets</li>"
            "<li>Visualisation des utilisateurs</li>"
            "<li>Configuration du système</li>"
            "<li>Statistiques en temps réel</li>"
            "</ul>"
            "<p>© 2024 - Tous droits réservés</p>")

# ============================
# Lancement direct (pour test)
# ============================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Palette de couleurs sombre
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(30, 30, 46))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(20, 20, 32))
    palette.setColor(QPalette.AlternateBase, QColor(40, 40, 56))
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(50, 50, 70))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.Highlight, QColor(255, 215, 0))
    palette.setColor(QPalette.HighlightedText, QColor(40, 40, 56))
    
    app.setPalette(palette)
    
    admin_panel = AdminPanel()
    admin_panel.show()
    sys.exit(app.exec_())