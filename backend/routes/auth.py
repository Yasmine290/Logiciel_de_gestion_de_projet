"""
Blueprint pour les routes d'authentification
Gère l'inscription et la connexion des utilisateurs
"""
from flask import Blueprint, jsonify, request
from werkzeug.security import generate_password_hash, check_password_hash
import os
import sys
# Ajout du répertoire parent au path pour les imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db import get_db_connection

# Création du Blueprint pour l'authentification
auth_bp = Blueprint('auth', __name__, url_prefix='/api')


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Inscription d'un nouvel utilisateur (employé)
    
    Body attendu (JSON):
    {
        "nomEmploye": "Nom",
        "courrielEmploye": "email@example.com",
        "motDePasse": "password123",
        "role": "Admin|Gestionnaire|Employe"  (optionnel, défaut: Employe)
    }
    """
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


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Connexion utilisateur : vérifie l'email et le mot de passe
    
    Body attendu (JSON):
    {
        "courrielEmploye": "email@example.com",
        "motDePasse": "password123"
    }
    
    Retourne les informations de l'utilisateur si la connexion réussit
    """
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


@auth_bp.route('/test', methods=['GET'])
def api_test():
    """API de test (pour vérifier la connexion frontend ↔ backend)"""
    return jsonify({"message": "Connexion Frontend ↔ Backend OK"})
