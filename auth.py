import hashlib
import jwt
import secrets
import os
from datetime import datetime, timedelta
from typing import Optional, Tuple
from .models import User, UserRole


SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'votre_cle_secrete_a_changer')
TOKEN_EXPIRATION = int(os.getenv('JWT_EXPIRATION', 3600))

class AuthService:
    def __init__(self, db_connection):
        self.db = db_connection
    
    @staticmethod
    def hash_password(password: str, salt: Optional[str] = None) -> Tuple[str, str]:
        """Hash un mot de passe avec un salt"""
        if salt is None:
            salt = secrets.token_hex(32)
        pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return pwd_hash.hex(), salt
    
    @staticmethod
    def verify_password(password: str, hashed: str, salt: str) -> bool:
        """Vérifie si le mot de passe correspond au hash"""
        pwd_hash, _ = AuthService.hash_password(password, salt)
        return pwd_hash == hashed
    
    def register_user(self, email: str, password: str, nom: str, 
                     prenom: str, role: UserRole) -> Optional[User]:
        """Inscrit un nouvel utilisateur"""
        # Vérifier si l'email existe déjà
        cursor = self.db.cursor()
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            raise ValueError("Cet email est déjà utilisé")
        
        # Hasher le mot de passe
        pwd_hash, salt = self.hash_password(password)
        
        # Insérer l'utilisateur
        query = """
        INSERT INTO users (nom, prenom, email, mot_de_passe_hash, salt, role, date_creation)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (nom, prenom, email, pwd_hash, salt, role.value, datetime.now()))
        self.db.commit()
        
        user_id = cursor.lastrowid
        return User(user_id, nom, prenom, email, pwd_hash, role)
    
    def login(self, email: str, password: str) -> Tuple[Optional[User], Optional[str]]:
        """Connecte un utilisateur et retourne le token"""
        cursor = self.db.cursor()
        query = """
        SELECT id, nom, prenom, email, mot_de_passe_hash, salt, role, actif 
        FROM users WHERE email = %s
        """
        cursor.execute(query, (email,))
        result = cursor.fetchone()
        
        if not result:
            return None, None
        
        user_id, nom, prenom, email, pwd_hash, salt, role, actif = result
        
        if not actif:
            raise ValueError("Compte désactivé")
        
        if not self.verify_password(password, pwd_hash, salt):
            return None, None
        
        # Mettre à jour la dernière connexion
        cursor.execute(
            "UPDATE users SET date_derniere_connexion = %s WHERE id = %s",
            (datetime.now(), user_id)
        )
        self.db.commit()
        
        user = User(user_id, nom, prenom, email, pwd_hash, UserRole(role))
        token = self.generate_token(user)
        
        return user, token
    
    @staticmethod
    def generate_token(user: User, expires_in: int = TOKEN_EXPIRATION) -> str:
        """Génère un token JWT pour l'utilisateur"""
        payload = {
            'user_id': user.id,
            'email': user.email,
            'role': user.role.value,
            'exp': datetime.utcnow() + timedelta(seconds=expires_in),
            'iat': datetime.utcnow()
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
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Récupère un utilisateur par son ID"""
        cursor = self.db.cursor()
        query = "SELECT * FROM users WHERE id = %s AND actif = TRUE"
        cursor.execute(query, (user_id,))
        result = cursor.fetchone()
        
        if result:
            return User(
                result[0], result[1], result[2], result[3], 
                result[4], UserRole(result[6])
            )
        return None
    
    def change_password(self, user_id: int, old_password: str, new_password: str) -> bool:
        """Change le mot de passe d'un utilisateur"""
        cursor = self.db.cursor()
        cursor.execute(
            "SELECT mot_de_passe_hash, salt FROM users WHERE id = %s",
            (user_id,)
        )
        result = cursor.fetchone()
        
        if not result:
            return False
        
        pwd_hash, salt = result
        
        if not self.verify_password(old_password, pwd_hash, salt):
            raise ValueError("Ancien mot de passe incorrect")
        
        # Générer nouveau hash
        new_hash, new_salt = self.hash_password(new_password)
        
        cursor.execute(
            "UPDATE users SET mot_de_passe_hash = %s, salt = %s WHERE id = %s",
            (new_hash, new_salt, user_id)
        )
        self.db.commit()
        return True
    
    def request_password_reset(self, email: str) -> Optional[str]:
        """Demande une réinitialisation de mot de passe"""
        cursor = self.db.cursor()
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        result = cursor.fetchone()
        
        if not result:
            return None
        
        user_id = result[0]
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(hours=1)
        
        cursor.execute(
            """INSERT INTO password_resets (user_id, token, expires_at) 
               VALUES (%s, %s, %s)""",
            (user_id, token, expires_at)
        )
        self.db.commit()
        
        return token
