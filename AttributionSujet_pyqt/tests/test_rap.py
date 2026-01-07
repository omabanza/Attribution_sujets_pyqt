
"""
Test rapide des fonctions principales.
"""

import sys
import os

# Configuration des chemins
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, parent_dir)

print(f"Repertoire: {parent_dir}")
print("Import des modules...")

try:
    from module_Attribution_sujets_pyqt import init_db, get_subjects, get_tous_utilisateurs
    print("Modules importes")
    
    # Creer base temporaire
    import tempfile
    import module_Attribution_sujets_pyqt as mod
    
    temp_db = tempfile.NamedTemporaryFile(suffix='.sqlite', delete=False)
    temp_db.close()
    
    # Sauvegarder et modifier le chemin
    original_path = mod.DB_PATH
    mod.DB_PATH = temp_db.name
    
    print(f"Base temporaire: {temp_db.name}")
    
    # Tests rapides
    print("\nTests rapides:")
    
    # 1. Initialisation
    init_db()
    print("1. Base initialisee")
    
    # 2. Recuperer sujets
    sujets = get_subjects()
    print(f"2. {len(sujets)} sujets trouves")
    
    # 3. Recuperer utilisateurs
    users = get_tous_utilisateurs()
    print(f"3. {len(users)} utilisateurs trouves")
    
    # Restaurer
    mod.DB_PATH = original_path
    
    # Nettoyer
    os.unlink(temp_db.name)
    print("4. Nettoyage termine")
    
    print("\nTest rapide reussi !")
    
except Exception as e:
    print(f"Erreur: {e}")
    import traceback
    traceback.print_exc()