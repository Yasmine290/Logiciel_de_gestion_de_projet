
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

@app.route('/users')
def page_users():
    # Affiche la page de gestion des utilisateurs
    return send_from_directory(FRONTEND_DIR, 'users.html')

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

@app.route('/api/employes', methods=['GET'])
def api_employes():
    # Retourne la liste des employés depuis la base de données
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT e.idEmploye, e.nomEmploye, e.prenomEmploye, e.courrielEmploye, 
                   e.idRole, r.nomRole 
            FROM employe e 
            LEFT JOIN role r ON e.idRole = r.idRole
            ORDER BY e.nomEmploye
        """)
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(data)
    except Exception as e:
        print(f"Erreur lors de la récupération des employés: {e}")
        return jsonify({'message': 'Erreur lors de la récupération des employés'}), 500

@app.route('/api/employes/<int:idEmploye>', methods=['DELETE'])
def supprimer_employe(idEmploye):
    # Supprime un employé de la base de données
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Vérifier si l'employé existe
        cursor.execute("SELECT nomEmploye, prenomEmploye FROM employe WHERE idEmploye = %s", (idEmploye,))
        employe = cursor.fetchone()
        
        if not employe:
            cursor.close()
            conn.close()
            return jsonify({'message': 'Utilisateur introuvable'}), 404
        
        # Supprimer l'employé (les contraintes ON DELETE CASCADE s'occupent des relations)
        cursor.execute("DELETE FROM employe WHERE idEmploye = %s", (idEmploye,))
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"[API] Employé {idEmploye} supprimé avec succès")
        return jsonify({'message': f'Utilisateur {employe[1]} {employe[0]} supprimé avec succès'})
    except Exception as e:
        print(f"[API] Erreur lors de la suppression de l'employé: {e}")
        return jsonify({'message': f'Erreur lors de la suppression: {str(e)}'}), 500

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
        idProjet = cursor.lastrowid  # Récupérer l'ID du projet créé
        conn.commit()
        cursor.close()
        conn.close()
        print("[API] Projet ajouté avec succès, ID:", idProjet)
        return jsonify({'message': 'Projet ajouté avec succès', 'idProjet': idProjet}), 201
    except Exception as e:
        print("[API] Erreur lors de l'ajout du projet:", e)
        return jsonify({'message': "Erreur lors de l'ajout du projet", 'error': str(e)}), 500

# Inscription utilisateur
@app.route('/api/register', methods=['POST'])
def register():
    # Inscription d'un nouvel utilisateur (employé)
    # Récupération des données du formulaire
    data = request.json
    hashed_password = generate_password_hash(data['motDePasse'])
    # Détermination de l'idRole selon le type choisi
    role_map = {'Admin': 1, 'Gestionnaire': 2, 'Employe': 3}
    idRole = role_map.get(data.get('role'), 3)
    # Ajout de l'utilisateur en base
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO employe (idDepartement, idRole, nomEmploye, prenomEmploye, motDePasse, telephoneEmploye, courrielEmploye)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        (
            1,  # idDepartement par défaut
            idRole,
            data.get('nomEmploye'),
            '',  # prenomEmploye vide si non fourni
            hashed_password,
            '',  # telephoneEmploye vide si non fourni
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

@app.route('/api/projets/<int:id>', methods=['PUT'])
def update_projet(id):
    # Modifie un projet dans la base de données
    data = request.get_json(silent=True) or {}
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE projet 
            SET nomProjet = %s, descriptionProjet = %s, dateDebut = %s, dateFin = %s, statutProjet = %s
            WHERE idProjet = %s
            """,
            (
                data.get('nomProjet'),
                data.get('descriptionProjet'),
                data.get('dateDebut'),
                data.get('dateFin'),
                data.get('statutProjet'),
                id
            )
        )
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'message': 'Projet modifié avec succès'}), 200
    except Exception as e:
        print(f"Erreur lors de la modification du projet: {e}")
        return jsonify({'message': 'Erreur lors de la modification du projet'}), 500

@app.route('/api/projets/<int:id>', methods=['DELETE'])
def delete_projet(id):
    # Supprime un projet de la base de données
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Supprimer d'abord les tâches associées au projet
        cursor.execute("DELETE FROM tache WHERE idProjet = %s", (id,))
        # Ensuite supprimer le projet
        cursor.execute("DELETE FROM projet WHERE idProjet = %s", (id,))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'message': 'Projet supprimé avec succès'}), 200
    except Exception as e:
        print(f"Erreur lors de la suppression du projet: {e}")
        return jsonify({'message': 'Erreur lors de la suppression du projet'}), 500

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
        idTache = cursor.lastrowid  # Récupérer l'ID de la tâche créée
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'message': 'Tâche ajoutée avec succès', 'idTache': idTache}), 201
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

@app.route('/api/taches/<int:idTache>', methods=['PUT'])
def update_tache(idTache):
    # Modifie une tâche dans la base de données
    data = request.get_json(silent=True) or {}
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Gérer les valeurs None pour les champs optionnels
        titre = data.get('titreTache')
        description = data.get('descriptionTache')
        statut = data.get('statutTache')
        priorite = data.get('prioriteTache')
        date_debut = data.get('dateDebutTache') if data.get('dateDebutTache') else None
        date_fin = data.get('dateFinTache') if data.get('dateFinTache') else None
        heures = data.get('heuresEstimees') if data.get('heuresEstimees') else 0
        
        print(f"Mise à jour tâche {idTache}: {data}")
        
        cursor.execute(
            """
            UPDATE tache 
            SET titreTache = %s, nomTache = %s, descriptionTache = %s, 
                statutTache = %s, prioriteTache = %s, 
                dateDebutTache = %s, dateFinTache = %s, heuresEstimees = %s
            WHERE idTache = %s
            """,
            (
                titre,
                titre,  # nomTache = titreTache
                description,
                statut,
                priorite,
                date_debut,
                date_fin,
                heures,
                idTache
            )
        )
        conn.commit()
        
        # Si la tâche est marquée comme terminée, marquer toutes ses sous-tâches comme terminées
        if statut == 'Terminée':
            cursor.execute("UPDATE tache SET statutTache = 'Terminée' WHERE idTacheParent = %s", (idTache,))
            conn.commit()
            print(f"Toutes les sous-tâches de la tâche {idTache} ont été marquées comme terminées")
        
        # Mettre à jour le statut de la tâche parente si elle existe
        cursor.execute("SELECT idTacheParent, idProjet FROM tache WHERE idTache = %s", (idTache,))
        tache_info = cursor.fetchone()
        
        if tache_info:
            id_tache_parent = tache_info[0]
            id_projet = tache_info[1]
            
            # Si la tâche a une tâche parente, mettre à jour son statut
            if id_tache_parent:
                cursor.execute("SELECT statutTache FROM tache WHERE idTacheParent = %s", (id_tache_parent,))
                sous_taches = cursor.fetchall()
                
                if sous_taches:
                    # Vérifier si toutes les sous-tâches sont terminées
                    toutes_terminees = all(st[0] == 'Terminée' for st in sous_taches)
                    # Vérifier si au moins une est en cours
                    une_en_cours = any(st[0] in ['En cours', 'En révision'] for st in sous_taches)
                    
                    nouveau_statut_parent = None
                    if toutes_terminees:
                        nouveau_statut_parent = 'Terminée'
                    elif une_en_cours:
                        nouveau_statut_parent = 'En cours'
                    
                    if nouveau_statut_parent:
                        cursor.execute("UPDATE tache SET statutTache = %s WHERE idTache = %s", (nouveau_statut_parent, id_tache_parent))
                        conn.commit()
            
            # Mettre à jour le statut du projet
            cursor.execute("SELECT statutTache FROM tache WHERE idProjet = %s AND idTacheParent IS NULL", (id_projet,))
            taches_principales = cursor.fetchall()
            
            if taches_principales:
                # Vérifier si toutes les tâches principales sont terminées
                toutes_terminees = all(t[0] == 'Terminée' for t in taches_principales)
                # Vérifier si au moins une est en cours
                une_en_cours = any(t[0] in ['En cours', 'En révision'] for t in taches_principales)
                
                nouveau_statut_projet = None
                if toutes_terminees:
                    nouveau_statut_projet = 'Terminé'
                elif une_en_cours:
                    nouveau_statut_projet = 'En cours'
                
                if nouveau_statut_projet:
                    cursor.execute("UPDATE projet SET statutProjet = %s WHERE idProjet = %s", (nouveau_statut_projet, id_projet))
                    conn.commit()
        
        cursor.close()
        conn.close()
        return jsonify({'message': 'Tâche modifiée avec succès'}), 200
    except Exception as e:
        print(f"Erreur lors de la modification de la tâche: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'message': f'Erreur lors de la modification de la tâche: {str(e)}'}), 500

@app.route('/api/taches/<int:idTache>', methods=['DELETE'])
def delete_tache(idTache):
    # Supprime une tâche et toutes ses sous-tâches
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Supprimer récursivement toutes les sous-tâches
        cursor.execute("DELETE FROM tache WHERE idTacheParent = %s", (idTache,))
        # Supprimer la tâche elle-même
        cursor.execute("DELETE FROM tache WHERE idTache = %s", (idTache,))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'message': 'Tâche supprimée avec succès'}), 200
    except Exception as e:
        print(f"Erreur lors de la suppression de la tâche: {e}")
        return jsonify({'message': 'Erreur lors de la suppression de la tâche'}), 500

# ==================== GESTION DES ASSIGNATIONS ====================

@app.route('/api/projets/<int:idProjet>/membres', methods=['GET'])
def get_projet_membres(idProjet):
    # Retourne les membres assignés à un projet
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT e.idEmploye, e.nomEmploye, e.prenomEmploye, e.courrielEmploye
            FROM employe e
            INNER JOIN projet_employe pe ON e.idEmploye = pe.idEmploye
            WHERE pe.idProjet = %s
            """,
            (idProjet,)
        )
        membres = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(membres), 200
    except Exception as e:
        print(f"Erreur lors de la récupération des membres du projet: {e}")
        return jsonify([]), 200  # Retourner un tableau vide en cas d'erreur

@app.route('/api/projets/<int:idProjet>/membres', methods=['POST'])
def assign_projet_membres(idProjet):
    # Assigne des membres à un projet
    data = request.get_json(silent=True) or {}
    membres = data.get('membres', [])  # Liste des idEmploye
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Supprimer les anciennes assignations
        cursor.execute("DELETE FROM projet_employe WHERE idProjet = %s", (idProjet,))
        
        # Ajouter les nouvelles assignations
        for idEmploye in membres:
            cursor.execute(
                "INSERT INTO projet_employe (idProjet, idEmploye) VALUES (%s, %s)",
                (idProjet, idEmploye)
            )
        
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'message': 'Membres assignés au projet avec succès'}), 200
    except Exception as e:
        print(f"Erreur lors de l'assignation des membres au projet: {e}")
        return jsonify({'message': 'Erreur lors de l\'assignation des membres'}), 500

@app.route('/api/taches/<int:idTache>/membres', methods=['GET'])
def get_tache_membres(idTache):
    # Retourne les membres assignés à une tâche
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT e.idEmploye, e.nomEmploye, e.prenomEmploye, e.courrielEmploye
            FROM employe e
            INNER JOIN affectation_tache at ON e.idEmploye = at.idEmploye
            WHERE at.idTache = %s
            """,
            (idTache,)
        )
        membres = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(membres), 200
    except Exception as e:
        print(f"Erreur lors de la récupération des membres de la tâche: {e}")
        return jsonify([]), 200

@app.route('/api/taches/<int:idTache>/membres', methods=['POST'])
def assign_tache_membres(idTache):
    # Assigne des membres à une tâche
    data = request.get_json(silent=True) or {}
    membres = data.get('membres', [])  # Liste des idEmploye
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Supprimer les anciennes affectations
        cursor.execute("DELETE FROM affectation_tache WHERE idTache = %s", (idTache,))
        
        # Ajouter les nouvelles affectations
        for idEmploye in membres:
            cursor.execute(
                "INSERT INTO affectation_tache (idEmploye, idTache, roleSurLaTache) VALUES (%s, %s, %s)",
                (idEmploye, idTache, 'Collaborateur')
            )
        
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'message': 'Membres assignés à la tâche avec succès'}), 200
    except Exception as e:
        print(f"Erreur lors de l'assignation des membres à la tâche: {e}")
        return jsonify({'message': 'Erreur lors de l\'assignation des membres'}), 500

# --------------------
# 4) Lancement Flask
# --------------------

# Point d'entrée de l'application Flask
# Affiche le chemin du dossier frontend au démarrage
if __name__ == '__main__':
    print("Frontend dir:", FRONTEND_DIR)
    app.run(debug=True)
