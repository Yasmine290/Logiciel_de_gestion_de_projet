"""
Blueprint pour les routes de gestion des projets
Gère le CRUD des projets et l'assignation des membres
"""
from flask import Blueprint, jsonify, request
import os
import sys
# Ajout du répertoire parent au path pour les imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db import get_db_connection

# Création du Blueprint pour les projets
projets_bp = Blueprint('projets', __name__, url_prefix='/api')


def verifier_projets_en_retard(conn, idProjet=None):
    """
    Vérifie et met à jour automatiquement le statut des projets en retard.
    Un projet est en retard si sa date de fin est dépassée et qu'il n'est pas terminé.
    
    Args:
        conn: Connexion à la base de données
        idProjet (optional): Si fourni, vérifie uniquement ce projet
    
    Returns:
        Nombre de projets mis à jour
    """
    from datetime import date
    
    cursor = conn.cursor(dictionary=True)
    
    # Construire la requête selon si on filtre par projet ou non
    if idProjet:
        query = """
            SELECT idProjet, nomProjet, dateFin, statutProjet
            FROM projet
            WHERE idProjet = %s
            AND dateFin < %s
            AND statutProjet NOT IN ('Terminé', 'En retard')
        """
        cursor.execute(query, (idProjet, date.today()))
    else:
        query = """
            SELECT idProjet, nomProjet, dateFin, statutProjet
            FROM projet
            WHERE dateFin < %s
            AND statutProjet NOT IN ('Terminé', 'En retard')
        """
        cursor.execute(query, (date.today(),))
    
    projets_en_retard = cursor.fetchall()
    
    # Mettre à jour chaque projet en retard
    for projet in projets_en_retard:
        cursor.execute("""
            UPDATE projet
            SET statutProjet = 'En retard'
            WHERE idProjet = %s
        """, (projet['idProjet'],))
        
        print(f"[RETARD] Projet {projet['idProjet']} '{projet['nomProjet']}' "
              f"(échéance: {projet['dateFin']}) → statut 'En retard'")
    
    conn.commit()
    cursor.close()
    
    return len(projets_en_retard)


@projets_bp.route('/projets', methods=['GET'])
def api_projets():
    """
    Récupère la liste de tous les projets avec leur progression calculée.
    Vérifie automatiquement les projets en retard avant de retourner les données.
    
    Retourne:
        Liste des projets avec leurs informations complètes + progression
    """
    from .taches import calculer_progression_projet
    
    conn = get_db_connection()
    
    # Vérifier et mettre à jour les projets en retard
    verifier_projets_en_retard(conn)
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM projet")
    data = cursor.fetchall()
    
    # Calculer la progression pour chaque projet
    for projet in data:
        projet['progressionProjet'] = calculer_progression_projet(conn, projet['idProjet'])
    
    cursor.close()
    conn.close()
    return jsonify(data)


@projets_bp.route('/projets', methods=['POST'])
def add_projet():
    """
    Ajoute un nouveau projet dans la base de données
    
    Body attendu (JSON):
    {
        "nomProjet": "Nom du projet",
        "dateDebut": "2024-01-01",
        "dateFin": "2024-12-31",
        "heuresBudget": 100,
        "coutsProjet": 5000,
        "idClient": 1,
        "idEmploye": 1,  (chef de projet)
        "idTemplateProjet": null,
        "descriptionProjet": "Description",
        "statutProjet": "À faire"
    }
    """
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


@projets_bp.route('/projets/<int:id>', methods=['GET'])
def get_projet_by_id(id):
    """
    Retourne les détails d'un projet selon son identifiant avec progression calculée.
    Vérifie automatiquement si le projet est en retard avant de retourner les données.
    
    Args:
        id: Identifiant du projet
    """
    from .taches import calculer_progression_projet
    
    conn = get_db_connection()
    
    # Vérifier si ce projet est en retard
    verifier_projets_en_retard(conn, idProjet=id)
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM projet WHERE idProjet = %s", (id,))
    projet = cursor.fetchone()
    
    if projet:
        # Calculer la progression du projet
        projet['progressionProjet'] = calculer_progression_projet(conn, projet['idProjet'])
        cursor.close()
        conn.close()
        return jsonify(projet)
    else:
        cursor.close()
        conn.close()
        return jsonify({'message': 'Projet introuvable'}), 404


@projets_bp.route('/projets/<int:id>', methods=['PUT'])
def update_projet(id):
    """
    Modifie un projet dans la base de données
    
    Args:
        id: Identifiant du projet à modifier
        
    Body attendu (JSON):
    {
        "nomProjet": "Nouveau nom",
        "descriptionProjet": "Nouvelle description",
        "dateDebut": "2024-01-01",
        "dateFin": "2024-12-31",
        "statutProjet": "En cours"
    }
    """
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


@projets_bp.route('/projets/<int:id>', methods=['DELETE'])
def delete_projet(id):
    """
    Supprime un projet de la base de données
    
    Args:
        id: Identifiant du projet à supprimer
        
    Note: Supprime d'abord les saisies de temps, les affectations, puis les tâches, 
          les membres du projet et enfin le projet
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 1. Récupérer toutes les tâches du projet
        cursor.execute("SELECT idTache FROM tache WHERE idProjet = %s", (id,))
        taches = cursor.fetchall()
        
        # 2. Supprimer les saisies de temps pour chaque tâche (contrainte RESTRICT)
        for tache in taches:
            cursor.execute("DELETE FROM saisie_temps WHERE idTache = %s", (tache[0],))
        
        # 3. Supprimer les affectations de tâches (cascade automatique mais on le fait explicitement)
        for tache in taches:
            cursor.execute("DELETE FROM affectation_tache WHERE idTache = %s", (tache[0],))
        
        # 4. Supprimer les dépendances entre tâches
        for tache in taches:
            cursor.execute("DELETE FROM dependance_tache WHERE idPredecesseur = %s OR idSuccesseur = %s", 
                         (tache[0], tache[0]))
        
        # 5. Supprimer les tâches du projet
        cursor.execute("DELETE FROM tache WHERE idProjet = %s", (id,))
        
        # 6. Supprimer les membres du projet (table projet_employe)
        cursor.execute("DELETE FROM projet_employe WHERE idProjet = %s", (id,))
        
        # 7. Finalement supprimer le projet
        cursor.execute("DELETE FROM projet WHERE idProjet = %s", (id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'message': 'Projet supprimé avec succès'}), 200
    except Exception as e:
        print(f"Erreur lors de la suppression du projet: {e}")
        if conn:
            conn.rollback()
        return jsonify({'message': f'Erreur lors de la suppression du projet: {str(e)}'}), 500


# ==================== GESTION DES MEMBRES DU PROJET ====================

@projets_bp.route('/projets/<int:idProjet>/membres', methods=['GET'])
def get_projet_membres(idProjet):
    """
    Retourne les membres assignés à un projet
    
    Args:
        idProjet: Identifiant du projet
        
    Retourne:
        Liste des employés assignés au projet avec leurs informations
    """
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


@projets_bp.route('/projets/<int:idProjet>/membres', methods=['POST'])
def assign_projet_membres(idProjet):
    """
    Assigne des membres à un projet
    
    Args:
        idProjet: Identifiant du projet
        
    Body attendu (JSON):
    {
        "membres": [1, 2, 3]  // Liste des idEmploye
    }
    
    Note: Remplace les assignations existantes
    """
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
