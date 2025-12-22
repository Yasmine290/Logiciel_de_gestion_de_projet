"""
Blueprint pour les routes de gestion du temps
Gère l'ajout et la consultation des saisies de temps
"""
from flask import Blueprint, jsonify, request
import os
import sys
# Ajout du répertoire parent au path pour les imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db import get_db_connection

# Création du Blueprint pour la gestion du temps
temps_bp = Blueprint('temps', __name__, url_prefix='/api')


@temps_bp.route('/temps', methods=['GET'])
def api_temps_get():
    """
    Récupère les saisies de temps pour un employé (optionnel)
    
    Query params:
        idEmploye: (optionnel) Identifiant de l'employé pour filtrer
        
    Retourne:
        Liste des saisies de temps avec les informations du projet et de la tâche
    """
    idEmploye = request.args.get('idEmploye')
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        if idEmploye:
            # Récupérer les temps pour un employé spécifique avec les infos du projet et de la tâche
            cursor.execute("""
                SELECT st.*, 
                       t.titreTache, t.nomTache, t.heuresEstimees,
                       p.nomProjet,
                       e.nomEmploye, e.prenomEmploye,
                       DATE_FORMAT(st.dateTravail, '%Y-%m-%d') as dateTravail
                FROM saisie_temps st
                INNER JOIN tache t ON st.idTache = t.idTache
                INNER JOIN projet p ON t.idProjet = p.idProjet
                INNER JOIN employe e ON st.idEmploye = e.idEmploye
                WHERE st.idEmploye = %s
                ORDER BY st.dateTravail DESC
            """, (idEmploye,))
        else:
            # Récupérer tous les temps (pour Admin et Gestionnaire)
            cursor.execute("""
                SELECT st.*, 
                       t.titreTache, t.nomTache, t.heuresEstimees,
                       p.nomProjet,
                       e.nomEmploye, e.prenomEmploye,
                       DATE_FORMAT(st.dateTravail, '%Y-%m-%d') as dateTravail
                FROM saisie_temps st
                INNER JOIN tache t ON st.idTache = t.idTache
                INNER JOIN projet p ON t.idProjet = p.idProjet
                INNER JOIN employe e ON st.idEmploye = e.idEmploye
                ORDER BY st.dateTravail DESC
            """)
        
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(data)
    except Exception as e:
        print(f"Erreur lors de la récupération des temps: {e}")
        return jsonify([]), 500


@temps_bp.route('/temps', methods=['POST'])
def api_temps_post():
    """
    Ajoute une saisie de temps dans la base de données
    
    Body attendu (JSON):
    {
        "idEmploye": 1,
        "idTache": 5,
        "date": "2024-01-15",
        "heures": 8.5,
        "commentaire": "Travail sur la fonctionnalité X"
    }
    """
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
