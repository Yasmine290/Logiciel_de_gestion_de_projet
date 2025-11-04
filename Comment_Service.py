from datetime import datetime
from typing import List, Dict

class CommentService:
    def __init__(self, db_connection):
        self.db = db_connection
    
    def add_comment(self, entite_type: str, entite_id: int, 
                   auteur_id: int, contenu: str,
                   parent_comment_id: int = None) -> int:
        """Ajoute un commentaire"""
        query = """
        INSERT INTO comments (
            entite_type, entite_id, auteur_id, contenu, 
            date_creation, parent_comment_id
        ) VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        cursor = self.db.cursor()
        cursor.execute(query, (
    entite_type, 
    entite_id, 
    auteur_id, 
    contenu,
    datetime.now(), 
    parent_comment_id
))
        self.db.commit()
        
        return cursor.lastrowid
    
    def get_comments(self, entite_type: str, entite_id: int) -> List[Dict]:
        """Récupère les commentaires d'une entité"""
        query = """
        SELECT c.id, c.contenu, c.date_creation, c.date_modification,
               c.parent_comment_id, u.nom, u.prenom, u.id as auteur_id
        FROM comments c
        JOIN users u ON c.auteur_id = u.id
        WHERE c.entite_type = %s AND c.entite_id = %s
        ORDER BY c.date_creation DESC
        """
        
        cursor = self.db.cursor()
        cursor.execute(query, (entite_type, entite_id))
        results = cursor.fetchall()
        
        comments = []
        for r in results:
            comments.append({
                'id': r[0],
                'contenu': r[1],
                'date_creation': r[2],
                'date_modification': r[3],
                'parent_id': r[4],
                'auteur_nom': f"{r[5]} {r[6]}",
                'auteur_id': r[7]
            })
        
        return comments
    
    def update_comment(self, comment_id: int, contenu: str, user_id: int) -> bool:
        """Met à jour un commentaire"""
        cursor = self.db.cursor()
        
        # Vérifier que l'utilisateur est l'auteur
        cursor.execute(
            "SELECT auteur_id FROM comments WHERE id = %s",
            (comment_id,)
        )
        result = cursor.fetchone()
        
        if not result or result[0] != user_id:
            raise PermissionError("Vous ne pouvez modifier que vos propres commentaires")
        
        cursor.execute(
            """UPDATE comments 
               SET contenu = %s, date_modification = %s 
               WHERE id = %s""",
            (contenu, datetime.now(), comment_id)
        )
        self.db.commit()
        
        return True
    
    def delete_comment(self, comment_id: int, user_id: int, is_admin: bool = False) -> bool:
        """Supprime un commentaire"""
        cursor = self.db.cursor()
        
        if not is_admin:
            # Vérifier que l'utilisateur est l'auteur
            cursor.execute(
                "SELECT auteur_id FROM comments WHERE id = %s",
                (comment_id,)
            )
            result = cursor.fetchone()
            
            if not result or result[0] != user_id:
                raise PermissionError("Vous ne pouvez supprimer que vos propres commentaires")
        
        cursor.execute("DELETE FROM comments WHERE id = %s", (comment_id,))
        self.db.commit()
        
        return True