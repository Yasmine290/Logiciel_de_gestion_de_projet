from datetime import datetime
from typing import Optional, List, Dict

class NotificationService:
    def __init__(self, db_connection):
        self.db = db_connection
    
    def create_notification(self, user_id: int, type_notif: str, 
                          titre: str, message: str,
                          entite_type: str = None, entite_id: int = None) -> int:
        """Crée une notification"""
        query = """
        INSERT INTO notifications (
            user_id, type, titre, message, date_creation, 
            entite_type, entite_id, lue
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, FALSE)
        """
        
        cursor = self.db.cursor()
        cursor.execute(query, (
            user_id, type_notif, titre, message, datetime.now(),
            entite_type, entite_id
        ))
        self.db.commit()
        
        return cursor.lastrowid
    
    def notify_task_assignment(self, task_id: int, user_id: int, assigner_name: str):
        """Notifie l'assignation à une tâche"""
        cursor = self.db.cursor()
        cursor.execute("SELECT nom FROM taches WHERE id = %s", (task_id,))
        result = cursor.fetchone()
        
        if result:
            task_name = result[0]
            titre = "Nouvelle tâche assignée"
            message = f"{assigner_name} vous a assigné à la tâche: {task_name}"
            
            self.create_notification(
                user_id, 'assignation_tache', titre, message,
                'tache', task_id
            )
    
    def notify_timesheet_status(self, timesheet_id: int, status: str, comment: str = None):
        """Notifie le changement de statut d'une feuille de temps"""
        cursor = self.db.cursor()
        cursor.execute(
            "SELECT employe_id FROM timesheets WHERE id = %s",
            (timesheet_id,)
        )
        result = cursor.fetchone()
        
        if result:
            user_id = result[0]
            
            if status == 'approuve':
                titre = "Feuille de temps approuvée"
                message = "Votre feuille de temps a été approuvée"
            elif status == 'rejete':
                titre = "Feuille de temps rejetée"
                message = f"Votre feuille de temps a été rejetée. Raison: {comment}"
            else:
                return
            
            self.create_notification(
                user_id, 'approbation_temps', titre, message,
                'timesheet', timesheet_id
            )
    
    def notify_approaching_deadline(self, task_id: int):
        """Notifie d'une échéance proche"""
        cursor = self.db.cursor()
        
        # Récupérer la tâche et les assignés
        query = """
        SELECT t.nom, t.date_fin_prevue, ta.employe_id
        FROM taches t
        JOIN tache_assignations ta ON t.id = ta.tache_id
        WHERE t.id = %s AND ta.date_retrait IS NULL
        """
        
        cursor.execute(query, (task_id,))
        results = cursor.fetchall()
        
        if results:
            task_name = results[0][0]
            date_fin = results[0][1]
            jours_restants = (date_fin - datetime.now().date()).days
            
            titre = "Échéance proche"
            message = f"La tâche '{task_name}' arrive à échéance dans {jours_restants} jour(s)"
            
            for row in results:
                user_id = row[2]
                self.create_notification(
                    user_id, 'echeance_proche', titre, message,
                    'tache', task_id
                )
    
    def mark_as_read(self, notification_id: int, user_id: int) -> bool:
        """Marque une notification comme lue"""
        cursor = self.db.cursor()
        cursor.execute(
            """UPDATE notifications 
               SET lue = TRUE, date_lecture = %s 
               WHERE id = %s AND user_id = %s""",
            (datetime.now(), notification_id, user_id)
        )
        self.db.commit()
        return True
    
    def mark_all_as_read(self, user_id: int) -> bool:
        """Marque toutes les notifications comme lues"""
        cursor = self.db.cursor()
        cursor.execute(
            """UPDATE notifications 
               SET lue = TRUE, date_lecture = %s 
               WHERE user_id = %s AND lue = FALSE""",
            (datetime.now(), user_id)
        )
        self.db.commit()
        return True
    
    def get_user_notifications(self, user_id: int, unread_only: bool = False) -> List[Dict]:
        """Récupère les notifications d'un utilisateur"""
        cursor = self.db.cursor()
        
        if unread_only:
            query = """
            SELECT * FROM notifications 
            WHERE user_id = %s AND lue = FALSE
            ORDER BY date_creation DESC
            """
        else:
            query = """
            SELECT * FROM notifications 
            WHERE user_id = %s
            ORDER BY date_creation DESC
            LIMIT 50
            """
        
        cursor.execute(query, (user_id,))
        results = cursor.fetchall()
        
        notifications = []
        for r in results:
            notifications.append({
                'id': r[0],
                'type': r[2],
                'titre': r[3],
                'message': r[4],
                'date_creation': r[5],
                'lue': r[6],
                'entite_type': r[7],
                'entite_id': r[8]
            })
        
        return notifications
