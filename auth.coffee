import hashlib
import jwt
from datetime import datetime, timedelta
from typing import Optional
from models import User, UserRole

SECRET_KEY = "votre_cle_secrete_a_changer"  # À stocker dans variables d'environnement

class AuthService:
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash un mot de passe avec SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Vérifie si le mot de passe correspond au hash"""
        return AuthService.hash_password(password) == hashed
    
    @staticmethod
    def generate_token(user: User, expires_in: int = 3600) -> str:
        """Génère un token JWT pour l'utilisateur"""
        payload = {
            'user_id': user.id,
            'email': user.email,
            'role': user.role.value,
            'exp': datetime.utcnow() + timedelta(seconds=expires_in)
        }
        return jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    
    @staticmethod
    def verify_token(token: str) -> Optional[dict]:
        """Vérifie et décode un token JWT"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

class PermissionService:
    @staticmethod
    def can_access_project(user: User, project_id: int, createur_id: int) -> bool:
        """Vérifie si l'utilisateur peut accéder au projet"""
        if user.role == UserRole.ADMIN:
            return True
        if user.role == UserRole.PROJECT_MANAGER:
            return True  # Lecture sur tous les projets
        return False  # Employés n'ont pas accès direct aux projets
    
    @staticmethod
    def can_modify_project(user: User, createur_id: int) -> bool:
        """Vérifie si l'utilisateur peut modifier le projet"""
        if user.role == UserRole.ADMIN:
            return True
        if user.role == UserRole.PROJECT_MANAGER and user.id == createur_id:
            return True
        return False
    
    @staticmethod
    def can_access_task(user: User, task_assignes: list, createur_projet_id: int) -> bool:
        """Vérifie si l'utilisateur peut accéder à une tâche"""
        if user.role == UserRole.ADMIN:
            return True
        if user.role == UserRole.PROJECT_MANAGER:
            return True
        if user.role == UserRole.EMPLOYEE and user.id in task_assignes:
            return True
        return False
    
    @staticmethod
    def can_approve_timesheet(user: User) -> bool:
        """Vérifie si l'utilisateur peut approuver des feuilles de temps"""
        return user.role in [UserRole.ADMIN, UserRole.PROJECT_MANAGER]
    
    @staticmethod
    def can_modify_timeentry(user: User, timeentry_approuve: bool) -> bool:
        """Vérifie si l'utilisateur peut modifier une saisie de temps"""
        if timeentry_approuve:
            return False  # Personne ne peut modifier après approbation
        return True