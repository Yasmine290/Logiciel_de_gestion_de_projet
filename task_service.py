from typing import List, Optional
from datetime import datetime
from models import Task, TaskStatus

class TaskService:
    def __init__(self, db_connection):
        self.db = db_connection
    
    def create_task(self, nom: str, description: str, projet_id: int,
                   tache_parent_id: Optional[int] = None,
                   heures_estimees: float = 0.0) -> Task:
        """Crée une nouvelle tâche (ou sous-tâche)"""
        query = """
        INSERT INTO taches (nom, description, projet_id, tache_parent_id, 
                           statut, heures_estimees, date_creation)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor = self.db.cursor()
        cursor.execute(query, (nom, description, projet_id, tache_parent_id,
                              TaskStatus.ACTIVE.value, heures_estimees, datetime.now()))
        self.db.commit()
        
        task_id = cursor.lastrowid
        task = Task(task_id, nom, description, projet_id, tache_parent_id)
        task.heures_estimees = heures_estimees
        return task
    
    def get_task_by_id(self, task_id: int) -> Optional[Task]:
        """Récupère une tâche par son ID"""
        query = "SELECT * FROM taches WHERE id = %s"
        cursor = self.db.cursor()
        cursor.execute(query, (task_id,))
        result = cursor.fetchone()
        
        if result:
            task = Task(result[0], result[1], result[2], result[3], result[4])
            task.statut = TaskStatus(result[5])
            task.heures_estimees = result[6]
            task.heures_reelles = result[7]
            return task
        return None
    
    def get_tasks_by_project(self, project_id: int, 
                            parent_id: Optional[int] = None) -> List[Task]:
        """Récupère les tâches d'un projet (avec profondeur illimitée)"""
        if parent_id is None:
            query = """
            SELECT * FROM taches 
            WHERE projet_id = %s AND tache_parent_id IS NULL
            """
            cursor = self.db.cursor()
            cursor.execute(query, (project_id,))
        else:
            query = """
            SELECT * FROM taches 
            WHERE projet_id = %s AND tache_parent_id = %s
            """
            cursor = self.db.cursor()
            cursor.execute(query, (project_id, parent_id))
        
        results = cursor.fetchall()
        tasks = []
        for r in results:
            task = Task(r[0], r[1], r[2], r[3], r[4])
            task.statut = TaskStatus(r[5])
            task.heures_estimees = r[6]
            task.heures_reelles = r[7]
            tasks.append(task)
        
        return tasks
    
    def get_task_hierarchy(self, task_id: int) -> dict:
        """Récupère une tâche avec toutes ses sous-tâches (récursif)"""
        task = self.get_task_by_id(task_id)
        if not task:
            return None
        
        subtasks = self.get_tasks_by_project(task.projet_id, task_id)
        
        result = {
            'task': task,
            'subtasks': []
        }
        
        for subtask in subtasks:
            result['subtasks'].append(self.get_task_hierarchy(subtask.id))
        
        return result
    
    def assign_user_to_task(self, task_id: int, user_id: int) -> bool:
        """Assigne un utilisateur à une tâche"""
        query = """
        INSERT INTO tache_assignations (tache_id, employe_id, date_assignation)
        VALUES (%s, %s, %s)
        """
        cursor = self.db.cursor()
        try:
            cursor.execute(query, (task_id, user_id, datetime.now()))
            self.db.commit()
            return True
        except:
            return False
    
    def unassign_user_from_task(self, task_id: int, user_id: int) -> bool:
        """Retire un utilisateur d'une tâche"""
        query = "DELETE FROM tache_assignations WHERE tache_id = %s AND employe_id = %s"
        cursor = self.db.cursor()
        cursor.execute(query, (task_id, user_id))
        self.db.commit()
        return True
    
    def get_assigned_users(self, task_id: int) -> List[int]:
        """Récupère les IDs des utilisateurs assignés à une tâche"""
        query = "SELECT employe_id FROM tache_assignations WHERE tache_id = %s"
        cursor = self.db.cursor()
        cursor.execute(query, (task_id,))
        results = cursor.fetchall()
        return [r[0] for r in results]
    
    def update_task_status(self, task_id: int, new_status: TaskStatus) -> bool:
        """Met à jour le statut d'une tâche"""
        query = "UPDATE taches SET statut = %s WHERE id = %s"
        cursor = self.db.cursor()
        cursor.execute(query, (new_status.value, task_id))
        self.db.commit()
        return True
    
    def complete_task(self, task_id: int, user_id: int) -> bool:
        """Termine/ferme une tâche"""
        # Vérifier que l'utilisateur est assigné
        assigned = self.get_assigned_users(task_id)
        if user_id not in assigned:
            raise ValueError("L'utilisateur n'est pas assigné à cette tâche")
        
        return self.update_task_status(task_id, TaskStatus.COMPLETED)
    
    def update_task(self, task_id: int, nom: str = None, description: str = None,
                   heures_estimees: float = None) -> bool:
        """Met à jour une tâche"""
        updates = []
        params = []
        
        if nom:
            updates.append("nom = %s")
            params.append(nom)
        if description:
            updates.append("description = %s")
            params.append(description)
        if heures_estimees is not None:
            updates.append("heures_estimees = %s")
            params.append(heures_estimees)
        
        if not updates:
            return False
        
        query = f"UPDATE taches SET {', '.join(updates)} WHERE id = %s"
        params.append(task_id)
        
        cursor = self.db.cursor()
        cursor.execute(query, tuple(params))
        self.db.commit()
        return True
    
    def get_task_progress(self, task_id: int) -> dict:
        """Récupère la progression d'une tâche (incluant sous-tâches)"""
        task = self.get_task_by_id(task_id)
        
        # Calculer les heures totales incluant les sous-tâches
        query = """
        WITH RECURSIVE task_tree AS (
            SELECT id, heures_estimees, heures_reelles
            FROM taches
            WHERE id = %s
            
            UNION ALL
            
            SELECT t.id, t.heures_estimees, t.heures_reelles
            FROM taches t
            INNER JOIN task_tree tt ON t.tache_parent_id = tt.id
        )
        SELECT 
            SUM(heures_estimees) as total_estime,
            SUM(heures_reelles) as total_reel
        FROM task_tree
        """
        
        cursor = self.db.cursor()
        cursor.execute(query, (task_id,))
        result = cursor.fetchone()
        
        return {
            'task_id': task_id,
            'heures_estimees': result[0] or 0,
            'heures_reelles': result[1] or 0,
            'pourcentage': (result[1] / result[0] * 100) if result[0] > 0 else 0
        }
    
    def delete_task(self, task_id: int) -> bool:
        """Supprime une tâche et toutes ses sous-tâches"""
        # Supprimer récursivement les sous-tâches
        subtasks = self.get_tasks_by_project(
            self.get_task_by_id(task_id).projet_id, 
            task_id
        )
        for subtask in subtasks:
            self.delete_task(subtask.id)
        
        # Supprimer la tâche
        query = "DELETE FROM taches WHERE id = %s"
        cursor = self.db.cursor()
        cursor.execute(query, (task_id,))
        self.db.commit()
        return True