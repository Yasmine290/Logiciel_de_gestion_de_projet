import re

class ValidationService:
    @staticmethod
    def validate_email(email: str) -> bool:
        """Valide un email"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_password_strength(password: str) -> Dict:
        """Vérifie la force d'un mot de passe"""
        errors = []
        
        if len(password) < 8:
            errors.append("Le mot de passe doit contenir au moins 8 caractères")
        
        if not re.search(r'[A-Z]', password):
            errors.append("Le mot de passe doit contenir au moins une majuscule")
        
        if not re.search(r'[a-z]', password):
            errors.append("Le mot de passe doit contenir au moins une minuscule")
        
        if not re.search(r'\d', password):
            errors.append("Le mot de passe doit contenir au moins un chiffre")
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("Le mot de passe doit contenir au moins un caractère spécial")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'strength': 'forte' if len(errors) == 0 else 'faible'
        }
    
    @staticmethod
    def validate_dates(date_debut: datetime, date_fin: datetime) -> bool:
        """Valide une plage de dates"""
        if date_debut and date_fin:
            if date_fin < date_debut:
                raise ValueError("La date de fin doit être postérieure à la date de début")
        return True
    
    @staticmethod
    def sanitize_input(text: str) -> str:
        """Nettoie les entrées utilisateur"""
        if not text:
            return ""
        
        # Supprimer les caractères dangereux
        text = text.strip()
        text = re.sub(r'[<>]', '', text)  # Prévenir XSS basique
        
        return text
    
    @staticmethod
    def validate_hours(hours: float) -> bool:
        """Valide un nombre d'heures"""
        if hours < 0 or hours > 24:
            raise ValueError("Les heures doivent être entre 0 et 24")
        
        # Vérifier multiples de 0.25
        if (hours * 4) % 1 != 0:
            raise ValueError("Les heures doivent être en multiples de 0.25 (15 minutes)")
        
        return True
