import sys
import socket
import ast
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QPalette, QColor, QBrush

SERVER_IP = "127.0.0.1"
SERVER_PORT = 55555

class ResultatsInterface(QWidget):
    def __init__(self, login, parent_fenetre):
        super().__init__()
        self.login = login
        self.parent_fenetre = parent_fenetre
        
        self.setWindowTitle(f"Résultats d'attribution - {login}")
        self.showMaximized()
        
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(70, 130, 180))
        self.setPalette(palette)
        
        self.init_ui()
        self.charger_resultats()
        
        # Auto-rafraîchissement toutes les 30 secondes
        self.timer = QTimer()
        self.timer.timeout.connect(self.charger_resultats)
        self.timer.start(30000)
    
    def init_ui(self):
        """Initialise l'interface utilisateur"""
        # Layout principal
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # En-tête
        header_layout = QHBoxLayout()
        
        # Titre
        lbl_titre = QLabel("🎯 Vos Résultats d'Attribution")
        lbl_titre.setFont(QFont("Arial", 24, QFont.Bold))
        lbl_titre.setStyleSheet("color: white;")
        
        # Boutons
        btn_actualiser = QPushButton("🔄 Actualiser")
        btn_actualiser.setFont(QFont("Arial", 12))
        btn_actualiser.setStyleSheet("""
            QPushButton {
                background: #2196F3;
                color: white;
                padding: 10px 20px;
                border-radius: 8px;
                border: 2px solid white;
            }
            QPushButton:hover {
                background: #42A5F5;
            }
        """)
        btn_actualiser.clicked.connect(self.charger_resultats)
        
        btn_retour = QPushButton("← Retour aux sujets")
        btn_retour.setFont(QFont("Arial", 12))
        btn_retour.setStyleSheet("""
            QPushButton {
                background: #757575;
                color: white;
                padding: 10px 20px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background: #9E9E9E;
            }
        """)
        btn_retour.clicked.connect(self.retour_sujets)
        
        header_layout.addWidget(lbl_titre)
        header_layout.addStretch()
        header_layout.addWidget(btn_actualiser)
        header_layout.addWidget(btn_retour)
        
        main_layout.addLayout(header_layout)
        
        # Zone d'information
        self.lbl_info = QLabel("Chargement des résultats...")
        self.lbl_info.setFont(QFont("Arial", 14))
        self.lbl_info.setStyleSheet("""
            color: #FFD700;
            background: rgba(0, 0, 0, 0.3);
            padding: 15px;
            border-radius: 10px;
            border: 2px solid #FFD700;
        """)
        self.lbl_info.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.lbl_info)
        
        # Widget avec onglets
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 2px solid white;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 10px;
            }
            QTabBar::tab {
                background: #4682B4;
                color: white;
                padding: 12px 20px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background: #FFD700;
                color: #333;
            }
            QTabBar::tab:hover {
                background: #5A9BD3;
            }
        """)
        
        # Onglet 1: Résultats personnels
        self.tab_personnel = QWidget()
        self.init_tab_personnel()
        
        # Onglet 2: Liste d'attente
        self.tab_attente = QWidget()
        self.init_tab_attente()
        
        # Onglet 3: Statistiques globales
        self.tab_stats = QWidget()
        self.init_tab_stats()
        
        # Onglet 4: Statistiques avancées
        self.tab_avance = QWidget()
        self.init_tab_avance()
        
        self.tab_widget.addTab(self.tab_personnel, "📋 Mes Sujets")
        self.tab_widget.addTab(self.tab_attente, "⏳ Liste d'Attente")
        self.tab_widget.addTab(self.tab_stats, "📊 Statistiques")
        self.tab_widget.addTab(self.tab_avance, "📈 Analyse Avancée")
        
        main_layout.addWidget(self.tab_widget)
        self.setLayout(main_layout)
    
    def init_tab_personnel(self):
        """Initialise l'onglet des résultats personnels"""
        layout = QVBoxLayout()
        
        # Tableau des sujets attribués
        self.table_attributions = QTableWidget()
        self.table_attributions.setColumnCount(5)
        self.table_attributions.setHorizontalHeaderLabels([
            "Sujet", "Description", "Choix #", "Statut", "Date"
        ])
        self.table_attributions.horizontalHeader().setStretchLastSection(True)
        self.table_attributions.setStyleSheet("""
            QTableWidget {
                background: white;
                font-size: 12px;
                border: 2px solid #2196F3;
                border-radius: 5px;
            }
            QHeaderView::section {
                background: #2196F3;
                color: white;
                padding: 10px;
                font-weight: bold;
                border: 1px solid #CCC;
            }
        """)
        
        layout.addWidget(self.table_attributions)
        self.tab_personnel.setLayout(layout)
    
    def init_tab_attente(self):
        """Initialise l'onglet des listes d'attente"""
        layout = QVBoxLayout()
        
        # Tableau des listes d'attente
        self.table_attente = QTableWidget()
        self.table_attente.setColumnCount(6)
        self.table_attente.setHorizontalHeaderLabels([
            "Sujet", "Description", "Choix #", "Position", 
            "Places Total", "Estimation"
        ])
        self.table_attente.horizontalHeader().setStretchLastSection(True)
        
        layout.addWidget(self.table_attente)
        
        # Note d'information
        lbl_note = QLabel(
            "ℹ️ Votre position dans la liste d'attente peut évoluer si d'autres "
            "stagiaires renoncent à leur attribution."
        )
        lbl_note.setFont(QFont("Arial", 10))
        lbl_note.setStyleSheet("color: #FFD700; font-style: italic; padding: 10px;")
        lbl_note.setWordWrap(True)
        
        layout.addWidget(lbl_note)
        self.tab_attente.setLayout(layout)
    
    def init_tab_stats(self):
        """Initialise l'onglet des statistiques"""
        layout = QVBoxLayout()
        
        # Widget de texte pour les statistiques
        self.text_stats = QTextEdit()
        self.text_stats.setReadOnly(True)
        self.text_stats.setStyleSheet("""
            QTextEdit {
                background: white;
                font-size: 14px;
                border: 2px solid #4CAF50;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        
        layout.addWidget(self.text_stats)
        self.tab_stats.setLayout(layout)
    
    def init_tab_avance(self):
        """Initialise l'onglet des statistiques avancées"""
        layout = QVBoxLayout()
        
        # Widget de texte pour les statistiques avancées
        self.text_avance = QTextEdit()
        self.text_avance.setReadOnly(True)
        self.text_avance.setStyleSheet("""
            QTextEdit {
                background: white;
                font-size: 14px;
                border: 2px solid #9C27B0;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        
        layout.addWidget(self.text_avance)
        self.tab_avance.setLayout(layout)
    
    def charger_resultats(self):
        """Charge les résultats depuis le serveur"""
        try:
            client = socket.socket()
            client.settimeout(5)
            client.connect((SERVER_IP, SERVER_PORT))
            
            # Envoyer la requête
            message = f"GET_RESULTS:{self.login}"
            client.send(message.encode())
            
            # Recevoir la réponse
            reponse = client.recv(8192).decode()
            client.close()
            
            if reponse.startswith("RESULTS:"):
                self.traiter_resultats(reponse[8:])
            elif reponse == "NO_RESULTS":
                self.lbl_info.setText("⚠️ L'attribution n'a pas encore été effectuée par l'administrateur.")
                self.vider_tables()
            elif reponse == "USER_NOT_FOUND":
                self.lbl_info.setText("❌ Utilisateur non trouvé.")
                self.vider_tables()
            else:
                self.lbl_info.setText(f"❌ Erreur: {reponse[:100]}")
                self.vider_tables()
                
        except Exception as e:
            self.lbl_info.setText(f"❌ Erreur de connexion: {str(e)[:50]}")
            print(f"Erreur: {e}")
    
    def traiter_resultats(self, donnees_str):
        """Traite les données reçues du serveur"""
        try:
            donnees = ast.literal_eval(donnees_str)
            
            # Structure attendue:
            # {
            #     'attributions': [liste des sujets attribués],
            #     'attente': [liste des sujets en attente],
            #     'statistiques': {statistiques}
            # }
            
            attributions = donnees.get('attributions', [])
            attente = donnees.get('attente', [])
            stats = donnees.get('statistiques', {})
            
            # Mettre à jour l'interface
            self.afficher_attributions(attributions)
            self.afficher_attente(attente)
            self.afficher_statistiques(stats)
            self.afficher_statistiques_avancees(stats)
            
            # Mettre à jour le message d'information
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
            self.lbl_info.setText(f"❌ Erreur de traitement: {str(e)[:50]}")
            print(f"Erreur traitement: {e}")
    
    def afficher_attributions(self, attributions):
        """Affiche les sujets attribués"""
        self.table_attributions.setRowCount(len(attributions))
        
        for row, sujet in enumerate(attributions):
            # Sujet: [titre, description, ordre, statut, date]
            for col in range(5):
                valeur = sujet[col] if col < len(sujet) else ""
                item = QTableWidgetItem(str(valeur))
                
                # Colorer selon le statut
                if col == 3:  # Colonne statut
                    if "attribué" in str(valeur).lower():
                        item.setForeground(QColor(0, 150, 0))
                    elif "attente" in str(valeur).lower():
                        item.setForeground(QColor(255, 140, 0))
                
                # Colorer selon l'ordre de préférence
                if col == 2:  # Colonne choix #
                    try:
                        ordre = int(valeur)
                        if ordre == 1:
                            item.setForeground(QColor(0, 100, 0))
                            item.setBackground(QBrush(QColor(200, 255, 200)))
                        elif ordre <= 3:
                            item.setForeground(QColor(0, 0, 150))
                        else:
                            item.setForeground(QColor(100, 100, 100))
                    except:
                        pass
                
                self.table_attributions.setItem(row, col, item)
        
        self.table_attributions.resizeColumnsToContents()
    
    def afficher_attente(self, attente):
        """Affiche les listes d'attente"""
        self.table_attente.setRowCount(len(attente))
        
        for row, sujet in enumerate(attente):
            # Sujet: [titre, description, ordre, position, capacite_total]
            for col in range(5):
                valeur = sujet[col] if col < len(sujet) else ""
                item = QTableWidgetItem(str(valeur))
                
                # Colorer selon la position
                if col == 3:  # Colonne position
                    try:
                        position = int(valeur)
                        capacite = int(sujet[4]) if len(sujet) > 4 else 10
                        
                        if position <= capacite * 0.5:
                            item.setForeground(QColor(0, 150, 0))
                        elif position <= capacite:
                            item.setForeground(QColor(255, 140, 0))
                        else:
                            item.setForeground(QColor(255, 50, 50))
                    except:
                        pass
                
                self.table_attente.setItem(row, col, item)
        
        self.table_attente.resizeColumnsToContents()
    
    def afficher_statistiques(self, stats):
        """Affiche les statistiques"""
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
        
        self.text_stats.setHtml(html)
    
    def afficher_statistiques_avancees(self, stats):
        """Affiche des statistiques plus détaillées"""
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
        
        html += '\n'.join(conseils)
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
        """Vide les tables"""
        self.table_attributions.setRowCount(0)
        self.table_attente.setRowCount(0)
        self.text_stats.clear()
        self.text_avance.clear()
    
    def retour_sujets(self):
        """Retourne à la fenêtre des sujets"""
        self.close()
        self.parent_fenetre.show()


# ============================
# MODIFICATION dans Attribution_sujets_pyqt.py
# ============================
# Ajoutez cette ligne après les autres imports:
# from resultats_interface import ResultatsInterface

# Puis modifiez la méthode afficher_resultats dans FenetreChoixSujets:
"""
def afficher_resultats(self):
    Ouvre la fenêtre des résultats
    print("DEBUG: Ouverture fenêtre résultats")
    self.fenetre_resultats = ResultatsInterface(self.login, self)
    self.fenetre_resultats.show()
"""