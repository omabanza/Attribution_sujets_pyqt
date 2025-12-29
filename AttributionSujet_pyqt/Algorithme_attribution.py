import random
from datetime import datetime
import sqlite3
from collections import defaultdict
import os

# Importez votre module existant
import module_Attribution_sujets_pyqt as db_module

DB_PATH = os.path.join("data", "base.sqlite")

class AlgorithmeAttribution:
    def __init__(self):
        # Assurez-vous que la base est initialisée
        db_module.init_db()  # Initialise les tables si elles n'existent pas
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.row_factory = sqlite3.Row
    
    def get_choix_utilisateurs(self):
        """Récupère tous les choix des utilisateurs avec leurs préférences"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 
                u.id as user_id,
                u.nom,
                u.prenom,
                u.login,
                c.sujet_id,
                c.ordre_preference,
                s.titre,
                s.capacite_max,
                s.actif
            FROM choix_utilisateurs c
            JOIN users u ON c.user_id = u.id
            JOIN sujets s ON c.sujet_id = s.id
            WHERE s.actif = 1
            ORDER BY c.ordre_preference
        """)
        return cursor.fetchall()
    
    def get_sujets_disponibles(self):
        """Récupère tous les sujets actifs avec leurs capacités"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, titre, capacite_max, actif
            FROM sujets
            WHERE actif = 1
        """)
        return cursor.fetchall()
    
    def attribution_cascade(self):
        """
        Algorithme d'attribution en cascade (1er choix → 2e choix → etc.)
        avec tirage au sort en cas d'égalité
        """
        # Récupérer les données
        choix = self.get_choix_utilisateurs()
        sujets = self.get_sujets_disponibles()
        
        # Initialiser les structures
        sujets_dict = {sujet['id']: {
            'titre': sujet['titre'],
            'capacite': sujet['capacite_max'],
            'attribues': [],
            'liste_attente': []
        } for sujet in sujets}
        
        utilisateurs_dict = {}
        
        # Organiser les choix par utilisateur
        for row in choix:
            user_id = row['user_id']
            if user_id not in utilisateurs_dict:
                utilisateurs_dict[user_id] = {
                    'nom': row['nom'],
                    'prenom': row['prenom'],
                    'login': row['login'],
                    'choix': []
                }
            
            utilisateurs_dict[user_id]['choix'].append({
                'sujet_id': row['sujet_id'],
                'ordre': row['ordre_preference'],
                'titre': row['titre']
            })
        
        # Trier les utilisateurs par nombre de choix (priorité à ceux qui ont fait plus de choix)
        utilisateurs_tries = sorted(utilisateurs_dict.items(), 
                                  key=lambda x: len(x[1]['choix']), 
                                  reverse=True)
        
        # Phase 1: Attribution des premiers choix
        print("=== PHASE 1: Attribution des premiers choix ===")
        for user_id, user_data in utilisateurs_tries:
            if not user_data['choix']:
                continue
                
            # Trier les choix par ordre de préférence
            choix_tries = sorted(user_data['choix'], key=lambda x: x['ordre'])
            premier_choix = choix_tries[0]
            sujet_id = premier_choix['sujet_id']
            
            if sujet_id in sujets_dict:
                sujet = sujets_dict[sujet_id]
                if len(sujet['attribues']) < sujet['capacite']:
                    # Place disponible
                    sujet['attribues'].append({
                        'user_id': user_id,
                        'nom': user_data['nom'],
                        'prenom': user_data['prenom'],
                        'ordre_preference': premier_choix['ordre']
                    })
                    print(f"✓ {user_data['prenom']} {user_data['nom']} → {premier_choix['titre']} (1er choix)")
                else:
                    # Capacité dépassée, tirage au sort
                    print(f"⚖️ Capacité dépassée pour {premier_choix['titre']}")
                    candidats = sujet['attribues'] + [{
                        'user_id': user_id,
                        'nom': user_data['nom'],
                        'prenom': user_data['prenom'],
                        'ordre_preference': premier_choix['ordre']
                    }]
                    
                    # Tirage au sort
                    random.shuffle(candidats)
                    sujet['attribues'] = candidats[:sujet['capacite']]
                    sujet['liste_attente'] = candidats[sujet['capacite']:]
                    
                    # Vérifier si l'utilisateur est dans la liste d'attente
                    dans_liste_attente = any(u['user_id'] == user_id for u in sujet['liste_attente'])
                    if dans_liste_attente:
                        print(f"⏳ {user_data['prenom']} {user_data['nom']} → Liste d'attente pour {premier_choix['titre']}")
        
        # Phase 2: Cascade pour les choix suivants
        print("\n=== PHASE 2: Cascade vers les choix suivants ===")
        for user_id, user_data in utilisateurs_tries:
            # Vérifier si l'utilisateur n'a pas encore de sujet attribué
            if any(user_id in [u['user_id'] for sujet in sujets_dict.values() for u in sujet['attribues']]):
                continue
            
            # Chercher dans les choix suivants
            choix_tries = sorted(user_data['choix'], key=lambda x: x['ordre'])
            for choix in choix_tries[1:]:  # Ignorer le premier choix déjà traité
                sujet_id = choix['sujet_id']
                
                if sujet_id in sujets_dict:
                    sujet = sujets_dict[sujet_id]
                    if len(sujet['attribues']) < sujet['capacite']:
                        sujet['attribues'].append({
                            'user_id': user_id,
                            'nom': user_data['nom'],
                            'prenom': user_data['prenom'],
                            'ordre_preference': choix['ordre']
                        })
                        print(f"✓ {user_data['prenom']} {user_data['nom']} → {choix['titre']} (choix #{choix['ordre']})")
                        break
        
        # Sauvegarder les résultats dans la base de données
        self.sauvegarder_resultats(sujets_dict)
        
        return sujets_dict, utilisateurs_dict
    
    def sauvegarder_resultats(self, sujets_dict):
        """Sauvegarde les résultats d'attribution dans la base de données"""
        cursor = self.conn.cursor()
        
        # Vider la table des résultats précédents
        cursor.execute("DELETE FROM resultats_attribution")
        
        # Créer la table si elle n'existe pas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS resultats_attribution (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sujet_id INTEGER,
                user_id INTEGER,
                nom TEXT,
                prenom TEXT,
                ordre_preference INTEGER,
                statut TEXT,
                position_liste_attente INTEGER,
                date_attribution TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (sujet_id) REFERENCES sujets(id),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        # Insérer les résultats
        for sujet_id, sujet_data in sujets_dict.items():
            # Attributions principales
            for i, attribution in enumerate(sujet_data['attribues']):
                cursor.execute("""
                    INSERT INTO resultats_attribution 
                    (sujet_id, user_id, nom, prenom, ordre_preference, statut, position_liste_attente)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    sujet_id,
                    attribution['user_id'],
                    attribution['nom'],
                    attribution['prenom'],
                    attribution['ordre_preference'],
                    'attribue',
                    None
                ))
            
            # Liste d'attente
            for i, attente in enumerate(sujet_data['liste_attente']):
                cursor.execute("""
                    INSERT INTO resultats_attribution 
                    (sujet_id, user_id, nom, prenom, ordre_preference, statut, position_liste_attente)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    sujet_id,
                    attente['user_id'],
                    attente['nom'],
                    attente['prenom'],
                    attente['ordre_preference'],
                    'attente',
                    i + 1
                ))
        
        self.conn.commit()
        print("✅ Résultats sauvegardés dans la base de données")
    
    def get_statistiques(self):
        """Calcule les statistiques d'attribution"""
        cursor = self.conn.cursor()
        
        # Statistiques générales
        cursor.execute("SELECT COUNT(*) FROM resultats_attribution WHERE statut = 'attribue'")
        nb_attributions = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM resultats_attribution WHERE statut = 'attente'")
        nb_en_attente = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT user_id) FROM resultats_attribution")
        nb_utilisateurs_traites = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM users")
        nb_total_utilisateurs = cursor.fetchone()[0]
        
        # Sujets les plus/le moins choisis
        cursor.execute("""
            SELECT 
                s.titre,
                COUNT(c.id) as nb_choix,
                s.capacite_max,
                COUNT(CASE WHEN r.statut = 'attribue' THEN 1 END) as nb_attribues,
                COUNT(CASE WHEN r.statut = 'attente' THEN 1 END) as nb_attente
            FROM sujets s
            LEFT JOIN choix_utilisateurs c ON s.id = c.sujet_id
            LEFT JOIN resultats_attribution r ON s.id = r.sujet_id
            WHERE s.actif = 1
            GROUP BY s.id
            ORDER BY nb_choix DESC
        """)
        stats_sujets = cursor.fetchall()
        
        # Nombre moyen de choix par personne
        cursor.execute("""
            SELECT 
                AVG(nb_choix) as moyenne_choix
            FROM (
                SELECT 
                    u.id,
                    COUNT(c.id) as nb_choix
                FROM users u
                LEFT JOIN choix_utilisateurs c ON u.id = c.user_id
                GROUP BY u.id
            )
        """)
        moyenne_choix = cursor.fetchone()[0] or 0
        
        return {
            'nb_attributions': nb_attributions,
            'nb_en_attente': nb_en_attente,
            'nb_utilisateurs_traites': nb_utilisateurs_traites,
            'nb_total_utilisateurs': nb_total_utilisateurs,
            'stats_sujets': stats_sujets,
            'moyenne_choix': round(moyenne_choix, 2)
        }
    
    def close(self):
        self.conn.close()


def lancer_attribution():
    """Fonction principale pour lancer l'attribution"""
    print("🚀 Lancement de l'algorithme d'attribution...")
    print("=" * 60)
    
    algo = AlgorithmeAttribution()
    
    # Vérifier si AU MOINS UN sujet a sa date limite passée
    cursor = algo.conn.cursor()
    
    # DÉBUG : Afficher toutes les dates pour comprendre
    cursor.execute("""
        SELECT titre, date_limite, actif,
               date('now') as aujourdhui,
               julianday(date('now')) - julianday(date_limite) as jours_ecart
        FROM sujets 
        WHERE actif = 1
    """)
    
    dates_info = cursor.fetchall()
    print("\n=== DÉBUG : VÉRIFICATION DES DATES ===")
    for row in dates_info:
        print(f"  • {row['titre']}: date_limite={row['date_limite']}, aujourd'hui={row['aujourdhui']}, écart={row['jours_ecart']} jours")
    
    # Requête corrigée pour vérifier les dates limites
    cursor.execute("""
        SELECT COUNT(*) as nb_sujets_eligibles 
        FROM sujets 
        WHERE actif = 1 
        AND (date_limite IS NULL OR date(date_limite) <= date('now'))
    """)
    
    nb_sujets_eligibles = cursor.fetchone()['nb_sujets_eligibles']
    
    if nb_sujets_eligibles == 0:
        print("\n⚠️  Aucun sujet n'a sa date limite passée !")
        print("   L'attribution ne peut être lancée que pour les sujets dont la date limite est atteinte.")
        
        # OPTION : Informer sur les dates limites
        cursor.execute("""
            SELECT titre, date_limite, actif
            FROM sujets 
            WHERE actif = 1 
            ORDER BY date_limite
        """)
        sujets_info = cursor.fetchall()
        
        print("\n   Dates limites des sujets actifs :")
        for sujet in sujets_info:
            try:
                date_limite = datetime.strptime(sujet['date_limite'], '%Y-%m-%d')
                aujourdhui = datetime.now()
                statut = "✓ PASSÉE" if date_limite.date() <= aujourdhui.date() else "✗ FUTURE"
                print(f"   • {sujet['titre']} : {sujet['date_limite']} ({statut})")
            except:
                print(f"   • {sujet['titre']} : {sujet['date_limite']} (Format invalide)")
        
        # OPTION 2 : Forcer l'attribution quand même (pour tests)
        reponse = input("\nVoulez-vous forcer l'attribution quand même ? (oui/non): ")
        if reponse.lower() == 'oui':
            print("Forçage de l'attribution...")
            # On continue même si les dates ne sont pas passées
            nb_sujets_eligibles = 1
        else:
            algo.close()
            return False, None, None
    
    print(f"\n✅ {nb_sujets_eligibles} sujet(s) avec date limite passée ou forcée")
    
    # VÉRIFIER D'ABORD SI DES CHOIX EXISTENT
    cursor.execute("SELECT COUNT(*) as nb_choix FROM choix_utilisateurs")
    nb_choix_total = cursor.fetchone()['nb_choix']
    
    if nb_choix_total == 0:
        print("❌ Aucun choix enregistré par les utilisateurs !")
        print("   Les utilisateurs doivent d'abord sélectionner des sujets.")
        algo.close()
        return False, None, None
    
    print(f"✅ {nb_choix_total} choix(s) enregistrés par les utilisateurs\n")
    
    try:
        # OPTION : Inclure tous les sujets actifs, indépendamment de la date limite
        cursor.execute("""
            SELECT id, titre, capacite_max, actif, date_limite
            FROM sujets
            WHERE actif = 1
        """)
        sujets_eligibles = cursor.fetchall()
        sujets_eligibles_ids = [s['id'] for s in sujets_eligibles]
        
        print(f"✅ {len(sujets_eligibles)} sujet(s) actif(s) inclus dans l'attribution")
        
        # DEBUG: Afficher les sujets inclus
        for sujet in sujets_eligibles:
            print(f"   • {sujet['titre']} (ID: {sujet['id']}, Date limite: {sujet['date_limite']})")
        
        # DEBUG: Vérifier les choix pour ces sujets
        cursor.execute(f"""
            SELECT COUNT(*) as nb_choix_eligibles
            FROM choix_utilisateurs
            WHERE sujet_id IN ({','.join(['?']*len(sujets_eligibles_ids))})
        """, sujets_eligibles_ids)
        nb_choix_eligibles = cursor.fetchone()['nb_choix_eligibles']
        
        print(f"✅ {nb_choix_eligibles} choix pour les sujets éligibles")
        
        if nb_choix_eligibles == 0:
            print("❌ Aucun choix enregistré pour les sujets actifs")
            print("   Les utilisateurs n'ont pas sélectionné de sujets actifs.")
            algo.close()
            return False, None, None
        
        print(f"\n✅ Lancement de l'attribution...\n")
        
        # Exécuter l'algorithme d'attribution personnalisé
        sujets_dict = {sujet['id']: {
            'titre': sujet['titre'],
            'capacite': sujet['capacite_max'],
            'attribues': [],
            'liste_attente': []
        } for sujet in sujets_eligibles}
        
        utilisateurs_dict = {}
        
        # Récupérer les choix seulement pour les sujets éligibles
        cursor.execute(f"""
            SELECT 
                u.id as user_id,
                u.nom,
                u.prenom,
                u.login,
                c.sujet_id,
                c.ordre_preference,
                s.titre,
                s.capacite_max,
                s.actif
            FROM choix_utilisateurs c
            JOIN users u ON c.user_id = u.id
            JOIN sujets s ON c.sujet_id = s.id
            WHERE s.actif = 1 
            AND s.id IN ({','.join(['?']*len(sujets_eligibles_ids))})
            ORDER BY c.ordre_preference
        """, sujets_eligibles_ids)
        choix = cursor.fetchall()
        
        # Organiser les choix par utilisateur
        for row in choix:
            user_id = row['user_id']
            if user_id not in utilisateurs_dict:
                utilisateurs_dict[user_id] = {
                    'nom': row['nom'],
                    'prenom': row['prenom'],
                    'login': row['login'],
                    'choix': []
                }
            
            utilisateurs_dict[user_id]['choix'].append({
                'sujet_id': row['sujet_id'],
                'ordre': row['ordre_preference'],
                'titre': row['titre']
            })
        
        # Trier les utilisateurs par nombre de choix (priorité à ceux qui ont fait plus de choix)
        utilisateurs_tries = sorted(utilisateurs_dict.items(), 
                                  key=lambda x: len(x[1]['choix']), 
                                  reverse=True)
        
        # Phase 1: Attribution des premiers choix
        print("=== PHASE 1: Attribution des premiers choix ===")
        for user_id, user_data in utilisateurs_tries:
            if not user_data['choix']:
                continue
                
            # Trier les choix par ordre de préférence
            choix_tries = sorted(user_data['choix'], key=lambda x: x['ordre'])
            premier_choix = choix_tries[0]
            sujet_id = premier_choix['sujet_id']
            
            if sujet_id in sujets_dict:
                sujet = sujets_dict[sujet_id]
                if len(sujet['attribues']) < sujet['capacite']:
                    # Place disponible
                    sujet['attribues'].append({
                        'user_id': user_id,
                        'nom': user_data['nom'],
                        'prenom': user_data['prenom'],
                        'ordre_preference': premier_choix['ordre']
                    })
                    print(f"✓ {user_data['prenom']} {user_data['nom']} → {premier_choix['titre']} (1er choix)")
                else:
                    # Capacité dépassée, tirage au sort
                    print(f"⚖️ Capacité dépassée pour {premier_choix['titre']}")
                    candidats = sujet['attribues'] + [{
                        'user_id': user_id,
                        'nom': user_data['nom'],
                        'prenom': user_data['prenom'],
                        'ordre_preference': premier_choix['ordre']
                    }]
                    
                    # Tirage au sort
                    random.shuffle(candidats)
                    sujet['attribues'] = candidats[:sujet['capacite']]
                    sujet['liste_attente'] = candidats[sujet['capacite']:]
                    
                    # Vérifier si l'utilisateur est dans la liste d'attente
                    dans_liste_attente = any(u['user_id'] == user_id for u in sujet['liste_attente'])
                    if dans_liste_attente:
                        print(f"⏳ {user_data['prenom']} {user_data['nom']} → Liste d'attente pour {premier_choix['titre']}")
        
        # Phase 2: Cascade pour les choix suivants
        print("\n=== PHASE 2: Cascade vers les choix suivants ===")
        for user_id, user_data in utilisateurs_tries:
            # Vérifier si l'utilisateur n'a pas encore de sujet attribué
            # Ligne 500 - Remplacez par :
            if any(user_id == u['user_id'] for sujet in sujets_dict.values() for u in sujet['attribues']):
                continue
            
            # Chercher dans les choix suivants
            choix_tries = sorted(user_data['choix'], key=lambda x: x['ordre'])
            for choix in choix_tries[1:]:  # Ignorer le premier choix déjà traité
                sujet_id = choix['sujet_id']
                
                if sujet_id in sujets_dict:
                    sujet = sujets_dict[sujet_id]
                    if len(sujet['attribues']) < sujet['capacite']:
                        sujet['attribues'].append({
                            'user_id': user_id,
                            'nom': user_data['nom'],
                            'prenom': user_data['prenom'],
                            'ordre_preference': choix['ordre']
                        })
                        print(f"✓ {user_data['prenom']} {user_data['nom']} → {choix['titre']} (choix #{choix['ordre']})")
                        break
        
        # Sauvegarder les résultats dans la base de données
        algo.sauvegarder_resultats(sujets_dict)
        
        # Afficher les résultats
        print("\n" + "=" * 60)
        print("📊 RÉSULTATS DE L'ATTRIBUTION")
        print("=" * 60)
        
        for sujet_id, sujet_data in sujets_dict.items():
            print(f"\n📌 {sujet_data['titre']} (Capacité: {sujet_data['capacite']})")
            print("   Attribués :")
            for attrib in sujet_data['attribues']:
                print(f"     • {attrib['prenom']} {attrib['nom']} (Choix #{attrib['ordre_preference']})")
            
            if sujet_data['liste_attente']:
                print("   Liste d'attente :")
                for i, attente in enumerate(sujet_data['liste_attente'], 1):
                    print(f"     {i}. {attente['prenom']} {attente['nom']}")
        
        # Calculer les statistiques
        stats = algo.get_statistiques()
        print("\n" + "=" * 60)
        print("📈 STATISTIQUES")
        print("=" * 60)
        print(f"• Utilisateurs avec attribution : {stats['nb_attributions']}/{stats['nb_total_utilisateurs']}")
        print(f"• Utilisateurs en liste d'attente : {stats['nb_en_attente']}")
        print(f"• Nombre moyen de choix par personne : {stats['moyenne_choix']}")
        
        algo.close()
        return True, sujets_dict, utilisateurs_dict
        
    except Exception as e:
        print(f"❌ Erreur lors de l'attribution : {e}")
        import traceback
        traceback.print_exc()
        algo.close()
        return False, None, None

if __name__ == "__main__":
    lancer_attribution()