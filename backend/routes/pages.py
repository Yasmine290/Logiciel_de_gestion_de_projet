"""
Blueprint pour les routes des pages HTML
Gère l'affichage des pages frontend et le service des fichiers statiques
"""
from flask import Blueprint, send_from_directory, abort
import os
import sys
# Ajout du répertoire parent au path pour les imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import FRONTEND_DIR, ASSETS_DIR

# Création du Blueprint pour les pages
pages_bp = Blueprint('pages', __name__)


# ROUTES POUR LES PAGES HTML
# Ces routes servent à afficher les pages du frontend

@pages_bp.route('/')
def root():
    """Affiche la page d'accueil (index.html)"""
    return send_from_directory(FRONTEND_DIR, 'index.html')


# Routes "propres" SANS .html
@pages_bp.route('/login')
def page_login():
    """Affiche la page de connexion"""
    return send_from_directory(FRONTEND_DIR, 'login.html')


@pages_bp.route('/projects')
def page_projects():
    """Affiche la page des projets"""
    return send_from_directory(FRONTEND_DIR, 'projects.html')


@pages_bp.route('/time')
def page_time():
    """Affiche la page de suivi du temps"""
    return send_from_directory(FRONTEND_DIR, 'time.html')


@pages_bp.route('/gantt')
def page_gantt():
    """Affiche la page du diagramme de Gantt"""
    return send_from_directory(FRONTEND_DIR, 'gantt.html')


@pages_bp.route('/users')
def page_users():
    """Affiche la page de gestion des utilisateurs"""
    return send_from_directory(FRONTEND_DIR, 'users.html')


@pages_bp.route('/project_details')
def page_project_details():
    """Affiche la page de détails d'un projet"""
    return send_from_directory(FRONTEND_DIR, 'project_details.html')


# Supporte AUSSI les URLs AVEC .html (ex: /login.html)
@pages_bp.route('/<page>.html')
def any_html(page):
    """Permet d'accéder à une page HTML via son nom (ex: /login.html)"""
    filename = f'{page}.html'
    file_path = os.path.join(FRONTEND_DIR, filename)
    if os.path.isfile(file_path):
        return send_from_directory(FRONTEND_DIR, filename)
    # Si le fichier n'existe pas, retourne une erreur 404
    abort(404)


# Favicon (évite un 404 bruyant)
@pages_bp.route('/favicon.ico')
def favicon():
    """Route pour le favicon (petite icône du site)"""
    ico_path = os.path.join(ASSETS_DIR, 'favicon.ico')
    if os.path.isfile(ico_path):
        return send_from_directory(ASSETS_DIR, 'favicon.ico')
    # Si pas de favicon, ne retourne pas d'erreur
    return ('', 204)


# FICHIERS STATIQUES (CSS / JS)
@pages_bp.route('/assets/<path:filename>')
def assets(filename):
    """Route pour servir les fichiers statiques (CSS, JS, images)"""
    return send_from_directory(ASSETS_DIR, filename)
