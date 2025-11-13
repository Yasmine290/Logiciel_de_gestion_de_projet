
# Importation des modules nécessaires
# Flask : framework web pour Python
# jsonify : permet de retourner des réponses JSON
# request : permet de récupérer les données envoyées par le client
# send_from_directory : sert à envoyer des fichiers statiques (HTML, CSS, JS)
# abort : permet d'arrêter une requête avec un code d'erreur
from flask import Flask, jsonify, request, send_from_directory, abort
# Connexion à la base de données MySQL
from db import get_db_connection
# CORS : autorise les requêtes du frontend vers le backend
from flask_cors import CORS
# Sécurité pour les mots de passe (hachage et vérification)
from werkzeug.security import generate_password_hash, check_password_hash
# os : gestion des chemins de fichiers
import os


# Définition des chemins vers les dossiers du frontend
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# FRONTEND_DIR : dossier contenant les fichiers HTML du frontend
FRONTEND_DIR = os.path.abspath(os.path.join(BASE_DIR, '..', 'Frontend'))
# ASSETS_DIR : dossier contenant les fichiers statiques (CSS, JS, images)
ASSETS_DIR = os.path.join(FRONTEND_DIR, 'assets')


# Initialisation de l'application Flask
app = Flask(__name__)
# Activation du mode debug pour afficher les erreurs détaillées
app.config['DEBUG'] = True
# Autorisation des requêtes du frontend (CORS)
CORS(app)


# ROUTES POUR LES PAGES HTML
# Ces routes servent à afficher les pages du frontend

@app.route('/')
def root():
    # Affiche la page d'accueil (index.html)
    return send_from_directory(FRONTEND_DIR, 'index.html')

# Routes "propres" SANS .html (tu les avais déjà)
@app.route('/login')
def page_login():
    # Affiche la page de connexion
    return send_from_directory(FRONTEND_DIR, 'login.html')

@app.route('/projects')
def page_projects():
    # Affiche la page des projets
    return send_from_directory(FRONTEND_DIR, 'projects.html')

@app.route('/time')
def page_time():
    # Affiche la page de suivi du temps
    return send_from_directory(FRONTEND_DIR, 'time.html')

@app.route('/gantt')
def page_gantt():
    # Affiche la page du diagramme de Gantt
    return send_from_directory(FRONTEND_DIR, 'gantt.html')

# Supporte AUSSI les URLs AVEC .html (ex: /login.html)
@app.route('/<page>.html')
def any_html(page):
    # Permet d'accéder à une page HTML via son nom (ex: /login.html)
    filename = f'{page}.html'
    file_path = os.path.join(FRONTEND_DIR, filename)
    if os.path.isfile(file_path):
        return send_from_directory(FRONTEND_DIR, filename)
    # Si le fichier n'existe pas, retourne une erreur 404
    abort(404)

# Favicon (évite un 404 bruyant)
@app.route('/favicon.ico')
def favicon():
    # Route pour le favicon (petite icône du site)
    ico_path = os.path.join(ASSETS_DIR, 'favicon.ico')
    if os.path.isfile(ico_path):
        return send_from_directory(ASSETS_DIR, 'favicon.ico')
    # Si pas de favicon, ne retourne pas d'erreur
    return ('', 204)

# ---------------------------------
# 2) FICHIERS STATIQUES (CSS / JS)
# ---------------------------------
@app.route('/assets/<path:filename>')
def assets(filename):
    # Route pour servir les fichiers statiques (CSS, JS, images)
    return send_from_directory(ASSETS_DIR, filename)


# API DE TEST (pour vérifier la connexion frontend ↔ backend)
@app.route('/api/test', methods=['GET'])
def api_test():
    # Retourne un message de test pour vérifier la connexion
    return jsonify({"message": "Connexion Frontend ↔ Backend OK"})

@app.route('/api/projets', methods=['GET'])
def api_projets():
    # Retourne la liste des projets depuis la base de données
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM projet")
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(data)

# Ajouter un projet
@app.route('/api/projets', methods=['POST'])
def add_projet():
    # Ajoute un nouveau projet dans la base de données
    data = request.json
    print("[API] Données reçues pour ajout projet:", data)
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO projet (nomProjet, dateDebut, dateFin, heuresBudget, coutsProjet, idClient, idEmploye, idTemplateProjet, descriptionProjet, statutProjet)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                data.get('nomProjet'),
                data.get('dateDebut'),
                data.get('dateFin'),
                data.get('heuresBudget', 0),
                data.get('coutsProjet', 0),
                data.get('idClient'),
                data.get('idEmploye'),
                data.get('idTemplateProjet'),
                data.get('descriptionProjet'),
                data.get('statutProjet', 'À faire')
            )
        )
        conn.commit()
        cursor.close()
        conn.close()
        print("[API] Projet ajouté avec succès")
        return jsonify({'message': 'Projet ajouté avec succès'}), 201
    except Exception as e:
        print("[API] Erreur lors de l'ajout du projet:", e)
        return jsonify({'message': "Erreur lors de l'ajout du projet", 'error': str(e)}), 500

# Inscription utilisateur
@app.route('/api/register', methods=['POST'])
def register():
    # Inscription d'un nouvel utilisateur (employé)
    data = request.json
    hashed_password = generate_password_hash(data['motDePasse'])
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO employe (idDepartement, idRole, nomEmploye, prenomEmploye, motDePasse, telephoneEmploye, courrielEmploye)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        (
            data.get('idDepartement'),
            data.get('idRole'),
            data.get('nomEmploye'),
            data.get('prenomEmploye'),
            hashed_password,
            data.get('telephoneEmploye'),
            data.get('courrielEmploye')
        )
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'message': 'Utilisateur inscrit avec succès'}), 201

# Connexion utilisateur
@app.route('/api/login', methods=['POST'])
def login():
    # Connexion utilisateur : vérifie l'email et le mot de passe
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM employe WHERE courrielEmploye = %s", (data['courrielEmploye'],))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    if user and check_password_hash(user['motDePasse'], data['motDePasse']):
        return jsonify({'message': 'Connexion réussie', 'user': user})
    else:
        return jsonify({'message': 'Identifiants invalides'}), 401

@app.route('/api/temps', methods=['GET'])
def api_temps_get():
    # Exemple de données de temps (à remplacer par la base de données si besoin)
    data = [
        {"id": 1, "projet": "Projet Alpha", "date": "2025-11-12", "heures": 3.5, "commentaire": "Réunion"},
    ]
    return jsonify(data)

@app.route('/api/temps', methods=['POST'])
def api_temps_post():
    # Ajout d'une saisie de temps dans la base de données
    data = request.get_json(silent=True) or {}
    print("POST /api/temps →", data)
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO saisie_temps (idEmploye, idTache, dateTravail, heures, commentaires)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                data.get('idEmploye'),
                data.get('idTache'),
                data.get('date'),
                data.get('heures'),
                data.get('commentaire')
            )
        )
        conn.commit()
        cursor.close()
        conn.close()
        print("[API] Temps ajouté avec succès")
        return jsonify({"message": "Entrée de temps enregistrée"})
    except Exception as e:
        print("[API] Erreur ajout temps:", e)
        return jsonify({"message": "Erreur lors de l'ajout du temps", "error": str(e)}), 500


@app.route('/api/projets/<int:id>', methods=['GET'])
def get_projet_by_id(id):
    # Retourne les détails d'un projet selon son identifiant
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM projet WHERE idProjet = %s", (id,))
    projet = cursor.fetchone()
    cursor.close()
    conn.close()
    if projet:
        return jsonify(projet)
    else:
        return jsonify({'message': 'Projet introuvable'}), 404

# Page de détails d’un projet
@app.route('/project_details')
def page_project_details():
    # Affiche la page de détails d'un projet
    return send_from_directory(FRONTEND_DIR, 'project_details.html')



@app.route('/api/taches', methods=['POST'])
def ajouter_tache():
    # Ajoute une nouvelle tâche dans la base de données
    data = request.get_json(silent=True) or {}
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO tache
            (idProjet, idTacheParent, titreTache, nomTache, descriptionTache, statutTache,
             prioriteTache, dateDebutTache, dateFinTache, heuresEstimees, idEtat)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            (
                data.get('idProjet'),
                data.get('idTacheParent'),
                data.get('titreTache'),
                data.get('titreTache'),  # nomTache = titreTache
                data.get('descriptionTache'),
                data.get('statutTache'),
                data.get('prioriteTache'),
                data.get('dateDebutTache'),
                data.get('dateFinTache'),
                data.get('heuresEstimees', 0),
                1  # idEtat par défaut
            )
        )
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'message': 'Tâche ajoutée avec succès'}), 201
    except Exception as e:
        import traceback
        print("[API] Erreur ajout tâche:", e)
        traceback.print_exc()
        return jsonify({'message': 'Erreur ajout tâche', 'error': str(e)}), 500

@app.route('/api/taches/<int:idProjet>', methods=['GET'])
def get_taches_by_projet(idProjet):
    # Retourne la liste des tâches d'un projet donné
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tache WHERE idProjet = %s", (idProjet,))
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(data)

# --------------------
# 4) Lancement Flask
# --------------------

# Point d'entrée de l'application Flask
# Affiche le chemin du dossier frontend au démarrage
if __name__ == '__main__':
    print("Frontend dir:", FRONTEND_DIR)
    app.run(debug=True)
