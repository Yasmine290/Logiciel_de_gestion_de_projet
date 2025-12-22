"""
Initialisation des Blueprints pour la modularisation des routes
"""

def register_blueprints(app):
    """
    Enregistre tous les Blueprints de l'application
    Cette fonction est appelée par app_new.py lors de l'initialisation
    """
    # Import des Blueprints
    from .pages import pages_bp
    from .auth import auth_bp
    from .projets import projets_bp
    from .taches import taches_bp
    from .temps import temps_bp
    from .employes import employes_bp
    
    # Enregistrement des Blueprints
    app.register_blueprint(pages_bp)           # Routes des pages HTML (/, /login, etc.)
    app.register_blueprint(auth_bp)            # Routes d'authentification (/api/register, /api/login)
    app.register_blueprint(projets_bp)         # Routes des projets (/api/projets/...)
    app.register_blueprint(taches_bp)          # Routes des tâches (/api/taches/...)
    app.register_blueprint(temps_bp)           # Routes du temps (/api/temps/...)
    app.register_blueprint(employes_bp)        # Routes des employés (/api/employes/...)
