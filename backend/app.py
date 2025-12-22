"""
Point d'entrée principal de l'application Flask
Version modulaire avec Blueprints
"""
# Importation des modules nécessaires
from flask import Flask
from flask_cors import CORS

# Import de la configuration
from config import Config, FRONTEND_DIR

# Import de la fonction d'enregistrement des Blueprints
from routes import register_blueprints


def create_app():
    """
    Factory function pour créer et configurer l'application Flask
    
    Retourne:
        app: Instance de l'application Flask configurée
    """
    # Initialisation de l'application Flask
    app = Flask(__name__)
    
    # Chargement de la configuration
    app.config.from_object(Config)
    
    # Activation de CORS (Cross-Origin Resource Sharing)
    # Permet les requêtes du frontend vers le backend
    CORS(app)
    
    # Enregistrement de tous les Blueprints
    # Cela importe et configure toutes les routes de l'application
    register_blueprints(app)
    
    return app


# Point d'entrée de l'application
if __name__ == '__main__':
    # Création de l'application
    app = create_app()
    
    # Affichage du chemin du dossier frontend au démarrage
    print("Frontend dir:", FRONTEND_DIR)
    
    # Lancement de l'application Flask en mode debug
    # host='0.0.0.0' permet les connexions externes (nécessaire pour ngrok)
    app.run(host='0.0.0.0', port=5000, debug=True)
