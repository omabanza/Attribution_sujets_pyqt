import sys  # Module système pour interagir avec l'interpréteur Python
import socket  # Module pour les communications réseau via sockets
import ast  # Module pour évaluer des chaînes en structures Python (sécurité)
from PyQt5.QtWidgets import *  # Tous les widgets de l'interface graphique PyQt5
from PyQt5.QtCore import Qt, QTimer  # Classes de base Qt: constantes et timer
from PyQt5.QtGui import QFont, QPalette, QColor, QBrush  # Classes graphiques Qt

# Configuration du serveur - adresse IP et port pour la communication réseau
SERVER_IP = "127.0.0.1"  # Adresse localhost (serveur local)
SERVER_PORT = 55555  # Port de communication

class ResultatsInterface(QWidget):
    """
    Interface graphique pour afficher les résultats d'attribution des sujets.
    Cette classe hérite de QWidget et gère l'affichage des résultats pour un utilisateur.
    """
    
    def __init__(self, login, parent_fenetre):
        """
        Constructeur de la classe ResultatsInterface.
        
        Args:
            login (str): Identifiant de l'utilisateur connecté
            parent_fenetre: Référence à la fenêtre parente pour permettre le retour
        """
        super().__init__()  # Appel du constructeur de la classe parent QWidget
        self.login = login  # Stockage du login utilisateur
        self.parent_fenetre = parent_fenetre  # Référence à la fenêtre précédente
        
        # Configuration de la fenêtre
        self.setWindowTitle(f"Résultats d'attribution - {login}")  # Titre avec login
        self.showMaximized()  # Affichage en plein écran
        
        # Configuration du fond d'écran (bleu acier)
        palette = QPalette()  # Création d'une palette de couleurs
        palette.setColor(QPalette.Window, QColor(70, 130, 180))  # Couleur bleu acier
        self.setPalette(palette)  # Application de la palette
        
        self.init_ui()  # Initialisation de l'interface utilisateur
        self.charger_resultats()  # Chargement initial des résultats
        
        # Configuration d'un timer pour le rafraîchissement automatique
        self.timer = QTimer()  # Création d'un timer
        self.timer.timeout.connect(self.charger_resultats)  # Connexion au slot de rafraîchissement
        self.timer.start(30000)  # Démarrage du timer (30 secondes)
    
    def init_ui(self):
        """Initialise l'interface utilisateur avec tous ses composants."""
        # Layout principal - organisation verticale des éléments
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)  # Espacement entre les widgets
        main_layout.setContentsMargins(30, 30, 30, 30)  # Marges (gauche, haut, droite, bas)
        
        # ==================== EN-TÊTE ====================
        header_layout = QHBoxLayout()  # Layout horizontal pour l'en-tête
        
        # Titre principal
        lbl_titre = QLabel("🎯 Vos Résultats d'Attribution")
        lbl_titre.setFont(QFont("Arial", 24, QFont.Bold))  # Police en gras, taille 24
        lbl_titre.setStyleSheet("color: white;")  # Texte en blanc
        
        # Bouton d'actualisation manuelle
        btn_actualiser = QPushButton("🔄 Actualiser")
        btn_actualiser.setFont(QFont("Arial", 12))
        # Feuille de style CSS pour le bouton
        btn_actualiser.setStyleSheet("""
            QPushButton {
                background: #2196F3;  /* Bleu */
                color: white;
                padding: 10px 20px;  /* Espacement intérieur */
                border-radius: 8px;  /* Coins arrondis */
                border: 2px solid white;  /* Bordure blanche */
            }
            QPushButton:hover {
                background: #42A5F5;  /* Bleu plus clair au survol */
            }
        """)
        btn_actualiser.clicked.connect(self.charger_resultats)  # Connexion à la méthode
        
        # Bouton de retour à la fenêtre des sujets
        btn_retour = QPushButton("← Retour aux sujets")
        btn_retour.setFont(QFont("Arial", 12))
        btn_retour.setStyleSheet("""
            QPushButton {
                background: #757575;  /* Gris */
                color: white;
                padding: 10px 20px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background: #9E9E9E;  /* Gris plus clair au survol */
            }
        """)
        btn_retour.clicked.connect(self.retour_sujets)  # Connexion à la méthode de retour
        
        # Assemblage de l'en-tête
        header_layout.addWidget(lbl_titre)  # Ajout du titre
        header_layout.addStretch()  # Espace élastique pour pousser les boutons à droite
        header_layout.addWidget(btn_actualiser)  # Ajout du bouton d'actualisation
        header_layout.addWidget(btn_retour)  # Ajout du bouton de retour
        
        main_layout.addLayout(header_layout)  # Ajout de l'en-tête au layout principal
        
        # ==================== ZONE D'INFORMATION ====================
        self.lbl_info = QLabel("Chargement des résultats...")
        self.lbl_info.setFont(QFont("Arial", 14))
        self.lbl_info.setStyleSheet("""
            color: #FFD700;  /* Or */
            background: rgba(0, 0, 0, 0.3);  /* Fond noir semi-transparent */
            padding: 15px;
            border-radius: 10px;
            border: 2px solid #FFD700;  /* Bordure or */
        """)
        self.lbl_info.setAlignment(Qt.AlignCenter)  # Centrage du texte
        main_layout.addWidget(self.lbl_info)
        
        # ==================== ONGLETS ====================
        self.tab_widget = QTabWidget()  # Widget avec onglets
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 2px solid white;
                background: rgba(255, 255, 255, 0.1);  /* Fond blanc très transparent */
                border-radius: 10px;
            }
            QTabBar::tab {
                background: #4682B4;  /* Bleu acier */
                color: white;
                padding: 12px 20px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background: #FFD700;  /* Or pour l'onglet sélectionné */
                color: #333;  /* Texte foncé */
            }
            QTabBar::tab:hover {
                background: #5A9BD3;  /* Bleu plus clair au survol */
            }
        """)
        
        # Création des différents onglets
        self.tab_personnel = QWidget()  # Onglet des résultats personnels
        self.init_tab_personnel()  # Initialisation
        
        self.tab_attente = QWidget()  # Onglet des listes d'attente
        self.init_tab_attente()  # Initialisation
        
        self.tab_stats = QWidget()  # Onglet des statistiques
        self.init_tab_stats()  # Initialisation
        
        self.tab_avance = QWidget()  # Onglet des statistiques avancées
        self.init_tab_avance()  # Initialisation
        
        # Ajout des onglets au widget avec leurs icônes et noms
        self.tab_widget.addTab(self.tab_personnel, "📋 Mes Sujets")
        self.tab_widget.addTab(self.tab_attente, "⏳ Liste d'Attente")
        self.tab_widget.addTab(self.tab_stats, "📊 Statistiques")
        self.tab_widget.addTab(self.tab_avance, "📈 Analyse Avancée")
        
        main_layout.addWidget(self.tab_widget)  # Ajout des onglets au layout principal
        self.setLayout(main_layout)  # Application du layout à la fenêtre
    
    def init_tab_personnel(self):
        """Initialise l'onglet des résultats personnels avec un tableau."""
        layout = QVBoxLayout()  # Layout vertical pour cet onglet
        
        # Tableau pour afficher les sujets attribués
        self.table_attributions = QTableWidget()
        self.table_attributions.setColumnCount(5)  # 5 colonnes
        # En-têtes des colonnes
        self.table_attributions.setHorizontalHeaderLabels([
            "Sujet", "Description", "Choix #", "Statut", "Date"
        ])
        self.table_attributions.horizontalHeader().setStretchLastSection(True)  # Dernière colonne extensible
        self.table_attributions.setStyleSheet("""
            QTableWidget {
                background: white;
                font-size: 12px;
                border: 2px solid #2196F3;  /* Bordure bleue */
                border-radius: 5px;
            }
            QHeaderView::section {
                background: #2196F3;  /* Fond bleu pour les en-têtes */
                color: white;
                padding: 10px;
                font-weight: bold;
                border: 1px solid #CCC;
            }
        """)
        
        layout.addWidget(self.table_attributions)  # Ajout du tableau au layout
        self.tab_personnel.setLayout(layout)  # Application du layout à l'onglet
    
    def init_tab_attente(self):
        """Initialise l'onglet des listes d'attente."""
        layout = QVBoxLayout()
        
        # Tableau pour les listes d'attente
        self.table_attente = QTableWidget()
        self.table_attente.setColumnCount(6)  # 6 colonnes
        self.table_attente.setHorizontalHeaderLabels([
            "Sujet", "Description", "Choix #", "Position", 
            "Places Total", "Estimation"
        ])
        self.table_attente.horizontalHeader().setStretchLastSection(True)
        
        layout.addWidget(self.table_attente)
        
        # Note d'information sur le fonctionnement des listes d'attente
        lbl_note = QLabel(
            "ℹ️ Votre position dans la liste d'attente peut évoluer si d'autres "
            "stagiaires renoncent à leur attribution."
        )
        lbl_note.setFont(QFont("Arial", 10))
        lbl_note.setStyleSheet("color: #FFD700; font-style: italic; padding: 10px;")
        lbl_note.setWordWrap(True)  # Retour à la ligne automatique
        
        layout.addWidget(lbl_note)
        self.tab_attente.setLayout(layout)
    
    def init_tab_stats(self):
        """Initialise l'onglet des statistiques avec une zone de texte enrichie."""
        layout = QVBoxLayout()
        
        # Zone de texte pour afficher les statistiques formatées en HTML
        self.text_stats = QTextEdit()
        self.text_stats.setReadOnly(True)  # Lecture seule
        self.text_stats.setStyleSheet("""
            QTextEdit {
                background: white;
                font-size: 14px;
                border: 2px solid #4CAF50;  /* Bordure verte */
                border-radius: 10px;
                padding: 20px;
            }
        """)
        
        layout.addWidget(self.text_stats)
        self.tab_stats.setLayout(layout)
    
    def init_tab_avance(self):
        """Initialise l'onglet des statistiques avancées."""
        layout = QVBoxLayout()
        
        # Zone de texte pour les statistiques avancées
        self.text_avance = QTextEdit()
        self.text_avance.setReadOnly(True)
        self.text_avance.setStyleSheet("""
            QTextEdit {
                background: white;
                font-size: 14px;
                border: 2px solid #9C27B0;  /* Bordure violette */
                border-radius: 10px;
                padding: 20px;
            }
        """)
        
        layout.addWidget(self.text_avance)
        self.tab_avance.setLayout(layout)
    
    def charger_resultats(self):
        """
        Charge les résultats depuis le serveur via une connexion socket.
        Envoie une requête au serveur et traite la réponse.
        """
        try:
            # Création et configuration du socket client
            client = socket.socket()
            client.settimeout(5)  # Timeout de 5 secondes
            client.connect((SERVER_IP, SERVER_PORT))  # Connexion au serveur
            
            # Envoi de la requête au format "GET_RESULTS:login"
            message = f"GET_RESULTS:{self.login}"
            client.send(message.encode())  # Encodage en bytes
            
            # Réception de la réponse (max 8KB)
            reponse = client.recv(8192).decode()
            client.close()  # Fermeture de la connexion
            
            # Traitement des différentes réponses possibles du serveur
            if reponse.startswith("RESULTS:"):
                # Réponse contenant des données
                self.traiter_resultats(reponse[8:])  # Extraction des données après "RESULTS:"
            elif reponse == "NO_RESULTS":
                # Aucun résultat disponible (attribution non effectuée)
                self.lbl_info.setText("⚠️ L'attribution n'a pas encore été effectuée par l'administrateur.")
                self.vider_tables()
            elif reponse == "USER_NOT_FOUND":
                # Utilisateur non trouvé sur le serveur
                self.lbl_info.setText("❌ Utilisateur non trouvé.")
                self.vider_tables()
            else:
                # Autre erreur
                self.lbl_info.setText(f"❌ Erreur: {reponse[:100]}")
                self.vider_tables()
                
        except Exception as e:
            # Gestion des erreurs de connexion
            self.lbl_info.setText(f"❌ Erreur de connexion: {str(e)[:50]}")
            print(f"Erreur: {e}")  # Log en console (à des fins de débogage)
    
    def traiter_resultats(self, donnees_str):
        """
        Traite les données brutes reçues du serveur.
        
        Args:
            donnees_str (str): Chaîne de données à évaluer en structure Python
        """
        try:
            # Conversion de la chaîne en dictionnaire Python
            # Utilisation de ast.literal_eval pour sécurité (pas d'exécution de code)
            donnees = ast.literal_eval(donnees_str)
            
            # Extraction des différentes parties des données
            # Structure attendue du dictionnaire:
            # {
            #     'attributions': [liste des sujets attribués],
            #     'attente': [liste des sujets en attente],
            #     'statistiques': {dictionnaire de statistiques}
            # }
            attributions = donnees.get('attributions', [])  # Liste, défaut: liste vide
            attente = donnees.get('attente', [])
            stats = donnees.get('statistiques', {})
            
            # Mise à jour des différents composants de l'interface
            self.afficher_attributions(attributions)
            self.afficher_attente(attente)
            self.afficher_statistiques(stats)
            self.afficher_statistiques_avancees(stats)
            
            # Mise à jour du message d'information principal
            total = len(attributions) + len(attente)
            if attributions:
                if attente:
                    self.lbl_info.setText(f"✅ Vous avez {len(attributions)} sujet(s) attribué(s) et êtes en liste d'attente pour {len(attente)} sujet(s)")
                else:
                    self.lbl_info.setText(f"🎉 Félicitations ! Tous vos choix ont été attribués ({len(attributions)} sujet(s))")
            elif attente:
                self.lbl_info.setText(f"⏳ Vous êtes en liste d'attente pour {len(attente)} sujet(s)")
            else:
                self.lbl_info.setText("📝 Aucun résultat disponible pour le moment")
                
        except Exception as e:
            # Gestion des erreurs de traitement des données
            self.lbl_info.setText(f"❌ Erreur de traitement: {str(e)[:50]}")
            print(f"Erreur traitement: {e}")  # Log en console
    
    def afficher_attributions(self, attributions):
        """
        Affiche les sujets attribués dans le tableau.
        
        Args:
            attributions (list): Liste des sujets attribués
                Format attendu: [titre, description, ordre, statut, date]
        """
        # Configuration du nombre de lignes du tableau
        self.table_attributions.setRowCount(len(attributions))
        
        # Remplissage du tableau ligne par ligne
        for row, sujet in enumerate(attributions):
            # Parcours des colonnes (0 à 4)
            for col in range(5):
                # Récupération de la valeur (chaîne vide si non disponible)
                valeur = sujet[col] if col < len(sujet) else ""
                item = QTableWidgetItem(str(valeur))  # Conversion en chaîne
                
                # Mise en forme conditionnelle basée sur le contenu
                if col == 3:  # Colonne "Statut"
                    if "attribué" in str(valeur).lower():
                        item.setForeground(QColor(0, 150, 0))  # Vert pour "attribué"
                    elif "attente" in str(valeur).lower():
                        item.setForeground(QColor(255, 140, 0))  # Orange pour "attente"
                
                # Coloration selon l'ordre de préférence
                if col == 2:  # Colonne "Choix #"
                    try:
                        ordre = int(valeur)  # Conversion en entier
                        if ordre == 1:
                            # Premier choix: vert foncé avec fond vert clair
                            item.setForeground(QColor(0, 100, 0))
                            item.setBackground(QBrush(QColor(200, 255, 200)))
                        elif ordre <= 3:
                            # Choix 2-3: bleu foncé
                            item.setForeground(QColor(0, 0, 150))
                        else:
                            # Autres choix: gris
                            item.setForeground(QColor(100, 100, 100))
                    except ValueError:
                        # Si conversion échoue, pas de coloration
                        pass
                
                # Placement de l'item dans le tableau
                self.table_attributions.setItem(row, col, item)
        
        # Ajustement automatique de la largeur des colonnes
        self.table_attributions.resizeColumnsToContents()
    
    def afficher_attente(self, attente):
        """
        Affiche les sujets en liste d'attente.
        
        Args:
            attente (list): Liste des sujets en attente
                Format attendu: [titre, description, ordre, position, capacite_total]
        """
        self.table_attente.setRowCount(len(attente))
        
        for row, sujet in enumerate(attente):
            for col in range(5):  # Note: le tableau a 6 colonnes mais on traite 5 valeurs
                valeur = sujet[col] if col < len(sujet) else ""
                item = QTableWidgetItem(str(valeur))
                
                # Coloration selon la position dans la liste d'attente
                if col == 3:  # Colonne "Position"
                    try:
                        position = int(valeur)  # Position actuelle
                        # Capacité totale (valeur à l'index 4)
                        capacite = int(sujet[4]) if len(sujet) > 4 else 10
                        
                        # Coloration conditionnelle:
                        if position <= capacite * 0.5:  # Dans la première moitié
                            item.setForeground(QColor(0, 150, 0))  # Vert
                        elif position <= capacite:  # Dans la capacité mais après la moitié
                            item.setForeground(QColor(255, 140, 0))  # Orange
                        else:  # Au-delà de la capacité
                            item.setForeground(QColor(255, 50, 50))  # Rouge
                    except (ValueError, IndexError):
                        pass  # Pas de coloration si erreur
                
                self.table_attente.setItem(row, col, item)
        
        self.table_attente.resizeColumnsToContents()
    
    def afficher_statistiques(self, stats):
        """
        Affiche les statistiques formatées en HTML.
        
        Args:
            stats (dict): Dictionnaire de statistiques
        """
        # Génération de HTML avec les données statistiques
        html = f"""
        <div style='font-family: Arial; font-size: 14px;'>
            <h2 style='color: #2196F3;'>📈 Vos Statistiques Personnelles</h2>
            <hr style='border: 1px solid #CCC;'>
            
            <h3>🎯 Performance de vos choix</h3>
            <table style='width: 100%; border-collapse: collapse;'>
                <tr>
                    <td style='padding: 8px; border-bottom: 1px solid #EEE;'>
                        <b>Nombre total de choix effectués :</b>
                    </td>
                    <td style='padding: 8px; border-bottom: 1px solid #EEE; text-align: right;'>
                        {stats.get('nb_choix_total', 0)}
                    </td>
                </tr>
                <tr>
                    <td style='padding: 8px; border-bottom: 1px solid #EEE;'>
                        <b>Sujets attribués :</b>
                    </td>
                    <td style='padding: 8px; border-bottom: 1px solid #EEE; text-align: right; color: #4CAF50;'>
                        {stats.get('nb_attribues', 0)}
                    </td>
                </tr>
                <tr>
                    <td style='padding: 8px; border-bottom: 1px solid #EEE;'>
                        <b>Sujets en liste d'attente :</b>
                    </td>
                    <td style='padding: 8px; border-bottom: 1px solid #EEE; text-align: right; color: #FF9800;'>
                        {stats.get('nb_en_attente', 0)}
                    </td>
                </tr>
                <tr>
                    <td style='padding: 8px; border-bottom: 1px solid #EEE;'>
                        <b>Taux de réussite :</b>
                    </td>
                    <td style='padding: 8px; border-bottom: 1px solid #EEE; text-align: right; color: #2196F3; font-weight: bold;'>
                        {stats.get('taux_reussite', '0%')}
                    </td>
                </tr>
            </table>
            
            <h3>📊 Distribution de vos choix</h3>
            <table style='width: 100%; border-collapse: collapse;'>
                <tr>
                    <td style='padding: 8px;'>1er choix obtenu :</td>
                    <td style='padding: 8px; text-align: right;'>
                        <span style='color: {'#4CAF50' if stats.get('premier_choix_obtenu', False) else '#F44336'};'>
                            {'✅ Oui' if stats.get('premier_choix_obtenu', False) else '❌ Non'}
                        </span>
                    </td>
                </tr>
                <tr>
                    <td style='padding: 8px;'>Moyenne de vos positions :</td>
                    <td style='padding: 8px; text-align: right;'>
                        {stats.get('position_moyenne', 'N/A')}
                    </td>
                </tr>
                <tr>
                    <td style='padding: 8px;'>Meilleur choix obtenu :</td>
                    <td style='padding: 8px; text-align: right; color: #4CAF50;'>
                        Choix #{stats.get('meilleur_choix', 'N/A')}
                    </td>
                </tr>
            </table>
            
            <h3>💡 Conseils</h3>
            <ul style='color: #666;'>
                <li>Plus vous faites de choix, plus vos chances d'obtenir un sujet sont grandes</li>
                <li>Les choix peu populaires ont plus de chances d'être attribués</li>
                <li>Vérifiez régulièrement votre position dans les listes d'attente</li>
            </ul>
        </div>
        """
        
        self.text_stats.setHtml(html)  # Affichage du HTML
    
    def afficher_statistiques_avancees(self, stats):
        """
        Affiche des statistiques plus détaillées et des conseils personnalisés.
        
        Args:
            stats (dict): Dictionnaire de statistiques
        """
        # Structure HTML pour l'analyse avancée
        html = f"""
        <div style='font-family: Arial; font-size: 14px;'>
            <h2 style='color: #2196F3;'>📈 Analyse Détaillée</h2>
            <hr style='border: 1px solid #CCC;'>
            
            <h3>🎯 Performance de vos choix</h3>
            <div style='display: flex; justify-content: space-around; margin: 20px 0;'>
                <div style='text-align: center;'>
                    <div style='font-size: 36px; color: #4CAF50; font-weight: bold;'>
                        {stats.get('taux_reussite', '0%')}
                    </div>
                    <div style='color: #666;'>Taux de réussite</div>
                </div>
                <div style='text-align: center;'>
                    <div style='font-size: 36px; color: {'#4CAF50' if stats.get('premier_choix_obtenu', False) else '#F44336'}; font-weight: bold;'>
                        {'✅' if stats.get('premier_choix_obtenu', False) else '❌'}
                    </div>
                    <div style='color: #666;'>1er choix obtenu</div>
                </div>
                <div style='text-align: center;'>
                    <div style='font-size: 36px; color: #FF9800; font-weight: bold;'>
                        {stats.get('meilleur_choix', 'N/A')}
                    </div>
                    <div style='color: #666;'>Meilleur choix</div>
                </div>
            </div>
            
            <h3>📊 Comparaison avec la moyenne</h3>
            <table style='width: 100%; border-collapse: collapse; margin: 15px 0;'>
                <tr style='background: #F5F5F5;'>
                    <th style='padding: 10px; text-align: left;'>Métrique</th>
                    <th style='padding: 10px; text-align: center;'>Vous</th>
                    <th style='padding: 10px; text-align: center;'>Moyenne</th>
                </tr>
                <tr>
                    <td style='padding: 10px; border-bottom: 1px solid #EEE;'>Choix effectués</td>
                    <td style='padding: 10px; border-bottom: 1px solid #EEE; text-align: center;'>
                        {stats.get('nb_choix_total', 0)}
                    </td>
                    <td style='padding: 10px; border-bottom: 1px solid #EEE; text-align: center; color: #666;'>
                        {stats.get('moyenne_generale', 3)}
                    </td>
                </tr>
                <tr>
                    <td style='padding: 10px; border-bottom: 1px solid #EEE;'>Sujets obtenus</td>
                    <td style='padding: 10px; border-bottom: 1px solid #EEE; text-align: center; color: #4CAF50;'>
                        {stats.get('nb_attribues', 0)}
                    </td>
                    <td style='padding: 10px; border-bottom: 1px solid #EEE; text-align: center; color: #666;'>
                        {stats.get('moyenne_attribues', 1.5)}
                    </td>
                </tr>
            </table>
            
            <h3>📈 Conseils personnalisés</h3>
            <ul style='background: #FFF3E0; padding: 15px; border-radius: 8px; border-left: 4px solid #FF9800;'>
        """
        
        # Génération de conseils personnalisés basés sur les statistiques
        conseils = []
        nb_choix = stats.get('nb_choix_total', 0)
        
        if nb_choix < 3:
            conseils.append("<li><b>Diversifiez vos choix :</b> Faites au moins 3 choix pour augmenter vos chances</li>")
        
        if not stats.get('premier_choix_obtenu', False):
            conseils.append("<li><b>Choix alternatifs :</b> Votre 1er choix était très demandé. Pensez à des sujets similaires moins populaires</li>")
        
        if stats.get('nb_en_attente', 0) > 0:
            conseils.append("<li><b>Liste d'attente :</b> Restez optimiste ! Les positions peuvent évoluer</li>")
        
        if len(conseils) == 0:
            conseils.append("<li><b>Excellent travail !</b> Votre stratégie de choix est optimale</li>")
        
        html += '\n'.join(conseils)  # Ajout des conseils au HTML
        
        # Section finale du HTML
        html += """
            </ul>
            
            <div style='margin-top: 20px; padding: 15px; background: #E8F5E8; border-radius: 8px; border-left: 4px solid #4CAF50;'>
                <b>Prochaine étape :</b> Consultez régulièrement cette page. Les listes d'attente 
                sont mises à jour en temps réel.
            </div>
        </div>
        """
        
        self.text_avance.setHtml(html)
    
    def vider_tables(self):
        """Vide tous les tableaux et zones de texte."""
        self.table_attributions.setRowCount(0)  # 0 ligne = tableau vide
        self.table_attente.setRowCount(0)
        self.text_stats.clear()  # Efface le contenu HTML
        self.text_avance.clear()
    
    def retour_sujets(self):
        """Ferme cette fenêtre et retourne à la fenêtre parente (choix des sujets)."""
        self.close()  # Ferme la fenêtre actuelle
        self.parent_fenetre.show()  # Affiche la fenêtre parente


# ============================
# MODIFICATION dans Attribution_sujets_pyqt.py
# ============================
"""
Instructions pour intégrer cette classe dans le fichier principal:

1. Ajoutez cette ligne après les autres imports:
   from resultats_interface import ResultatsInterface

2. Modifiez la méthode afficher_resultats dans FenetreChoixSujets:
   
   def afficher_resultats(self):
       # Ouvre la fenêtre des résultats
       print("DEBUG: Ouverture fenêtre résultats")
       self.fenetre_resultats = ResultatsInterface(self.login, self)
       self.fenetre_resultats.show()
       
Note: Ces commentaires sont des instructions pour l'intégration, 
pas du code exécuté dans ce fichier.
"""