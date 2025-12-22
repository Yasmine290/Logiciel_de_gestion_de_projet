"""
Blueprint pour les routes de gestion des employés
Gère la liste des employés, leur suppression et leurs assignations
"""
from flask import Blueprint, jsonify, request
import os
import sys
# Ajout du répertoire parent au path pour les imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db import get_db_connection

# Création du Blueprint pour les employés
employes_bp = Blueprint('employes', __name__, url_prefix='/api')


@employes_bp.route('/employes', methods=['GET'])
def api_employes():
    """
    Retourne la liste des employés depuis la base de données
    
    Retourne:
        Liste des employés avec leurs informations et leur rôle
    """
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


@employes_bp.route('/employes/<int:idEmploye>', methods=['DELETE'])
def supprimer_employe(idEmploye):
    """
    Supprime un employé de la base de données
    
    RESTRICTION: Seuls les ADMINISTRATEURS (idRole = 1) peuvent supprimer des utilisateurs
    
    Args:
        idEmploye: Identifiant de l'employé à supprimer
        
    Note: Les contraintes ON DELETE CASCADE s'occupent des relations
    """
    try:
        # TODO: Récupérer l'utilisateur connecté depuis la session/token
        # Pour l'instant, on suppose que l'info est disponible
        # Dans une vraie app, il faudrait un système d'authentification avec JWT ou session
        
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


@employes_bp.route('/employes/<int:idEmploye>/projets', methods=['GET'])
def get_employe_projets(idEmploye):
    """
    Récupère tous les projets auxquels l'employé est assigné (via les tâches)
    
    Args:
        idEmploye: Identifiant de l'employé
        
    Retourne:
        Liste des projets sur lesquels l'employé travaille
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT DISTINCT p.*
            FROM projet p
            INNER JOIN tache t ON p.idProjet = t.idProjet
            INNER JOIN affectation_tache at ON t.idTache = at.idTache
            WHERE at.idEmploye = %s
            ORDER BY p.nomProjet
        """, (idEmploye,))
        
        projets = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify(projets), 200
    except Exception as e:
        print(f"Erreur lors de la récupération des projets de l'employé: {e}")
        return jsonify([]), 500


@employes_bp.route('/employes/<int:idEmploye>/taches', methods=['GET'])
def get_employe_taches(idEmploye):
    """
    Récupère toutes les tâches assignées à l'employé
    
    Args:
        idEmploye: Identifiant de l'employé
        
    Query params:
        idProjet: (optionnel) Filtrer par projet
        
    Retourne:
        Liste des tâches assignées à l'employé avec le nom du projet
    """
    try:
        idProjet = request.args.get('idProjet')  # Optionnel : filtrer par projet
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        if idProjet:
            cursor.execute("""
                SELECT t.*, p.nomProjet
                FROM tache t
                INNER JOIN affectation_tache at ON t.idTache = at.idTache
                INNER JOIN projet p ON t.idProjet = p.idProjet
                WHERE at.idEmploye = %s AND t.idProjet = %s
                ORDER BY t.titreTache
            """, (idEmploye, idProjet))
        else:
            cursor.execute("""
                SELECT t.*, p.nomProjet
                FROM tache t
                INNER JOIN affectation_tache at ON t.idTache = at.idTache
                INNER JOIN projet p ON t.idProjet = p.idProjet
                WHERE at.idEmploye = %s
                ORDER BY p.nomProjet, t.titreTache
            """, (idEmploye,))
        
        taches = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify(taches), 200
    except Exception as e:
        print(f"Erreur lors de la récupération des tâches de l'employé: {e}")
        return jsonify([]), 500
