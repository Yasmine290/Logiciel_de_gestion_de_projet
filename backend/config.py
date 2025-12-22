"""
Configuration centralisée pour l'application Flask
"""
import os

# Définition des chemins vers les dossiers du frontend
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# FRONTEND_DIR : dossier contenant les fichiers HTML du frontend
FRONTEND_DIR = os.path.abspath(os.path.join(BASE_DIR, '..', 'Frontend'))
# ASSETS_DIR : dossier contenant les fichiers statiques (CSS, JS, images)
ASSETS_DIR = os.path.join(FRONTEND_DIR, 'assets')

class Config:
    """Configuration de l'application Flask"""
    # Mode debug pour afficher les erreurs détaillées
    DEBUG = True
    # Configuration CORS (Cross-Origin Resource Sharing)
    # Permet les requêtes du frontend vers le backend
    CORS_ORIGINS = "*"
