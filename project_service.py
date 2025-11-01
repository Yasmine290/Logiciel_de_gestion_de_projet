from typing import List, Optional
from datetime import datetime
from models import Project, Task, TaskStatus, User

class ProjectService:
    def __init__(self, db_connection):
        self.db = db_connection
    
    def create_project(self, nom: str, description: str, createur_id: int, 
                      est_template: bool = False) -> Project:
        """Crée un nouveau projet"""
        query = """
        INSERT INTO projets (nom, description, createur_id, est_template, date_creation)
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor = self.db.cursor()
        cursor.execute(query, (nom, description, createur_id, est_template, datetime.now()))
        self.db.commit()
        
        project_id = cursor.lastrowid
        return Project(project_id, nom, description, createur_id, est_template)
    
    def duplicate_project_from_template(self, template_id: int, nouveau_nom: str, 
                                       createur_id: int) -> Project:
        """Duplique un projet template"""
        # Récupérer le template
        template = self.get_project_by_id(template_id)
        if not template.est_template:
            raise ValueError("Ce projet n'est pas un template")
        
        # Créer le nouveau projet
        new_project = self.create_project(nouveau_nom, template.description, 
                                          createur_id, False)
        
        # Copier toutes les tâches du template
        self._copy_tasks_recursive(template_id, new_project.id, None)
        
        return new_project
    
    def _copy_tasks_recursive(self, old_project_id: int, new_project_id: int, 
                             parent_task_id: Optional[int]):
        """Copie récursivement les tâches d'un projet"""
        query = """
        SELECT id, nom, description, heures_estimees 
        FROM taches 
        WHERE projet_id = %s AND tache_parent_id %s
        """
        cursor = self.db.cursor()
        
        if parent_task_id is None:
            cursor.execute(query + "IS NULL", (old_project_id,))
        else:
            cursor.execute(query + "= %s", (old_project_id, parent_task_id))
        
        tasks = cursor.fetchall()
        
        for task in tasks:
            # Créer la nouvelle tâche
            new_task_id = self._create_task_copy(task, new_project_id, parent_task_id)
            # Copier les sous-tâches récursivement
            self._copy_tasks_recursive(old_project_id, new_project_id, new_task_id)
    
    def get_project_by_id(self, project_id: int) -> Optional[Project]:
        """Récupère un projet par son ID"""
        query = "SELECT * FROM projets WHERE id = %s"
        cursor = self.db.cursor()
        cursor.execute(query, (project_id,))
        result = cursor.fetchone()
        
        if result:
            return Project(result[0], result[1], result[2], result[3], result[4])
        return None
    
    def get_projects_by_user(self, user: User) -> List[Project]:
        """Récupère les projets accessibles par un utilisateur"""
        if user.role.value == "administrateur":
            query = "SELECT * FROM projets"
            cursor = self.db.cursor()
            cursor.execute(query)
        elif user.role.value == "gestionnaire_projet":
            query = "SELECT * FROM projets WHERE createur_id = %s"
            cursor = self.db.cursor()
            cursor.execute(query, (user.id,))
        else:
            # Pour les employés, récupérer les projets où ils ont des tâches assignées
            query = """
            SELECT DISTINCT p.* FROM projets p
            JOIN taches t ON p.id = t.projet_id
            JOIN tache_assignations ta ON t.id = ta.tache_id
            WHERE ta.employe_id = %s
            """
            cursor = self.db.cursor()
            cursor.execute(query, (user.id,))
        
        results = cursor.fetchall()
        projects = []
        for r in results:
            projects.append(Project(r[0], r[1], r[2], r[3], r[4]))
        return projects
    
    def update_project(self, project_id: int, nom: str = None, 
                      description: str = None) -> bool:
        """Met à jour un projet"""
        updates = []
        params = []
        
        if nom:
            updates.append("nom = %s")
            params.append(nom)
        if description:
            updates.append("description = %s")
            params.append(description)
        
        if not updates:
            return False
        
        query = f"UPDATE projets SET {', '.join(updates)} WHERE id = %s"
        params.append(project_id)
        
        cursor = self.db.cursor()
        cursor.execute(query, tuple(params))
        self.db.commit()
        return True
    
    def delete_project(self, project_id: int, force: bool = False) -> bool:
        """Supprime un projet (avec confirmation si template)"""
        project = self.get_project_by_id(project_id)
        
        if project.est_template and not force:
            raise ValueError("Confirmation excessive requise pour supprimer un template")
        
        query = "DELETE FROM projets WHERE id = %s"
        cursor = self.db.cursor()
        cursor.execute(query, (project_id,))
        self.db.commit()
        return True
    
    def get_project_statistics(self, project_id: int) -> dict:
        """Récupère les statistiques d'un projet"""
        query = """
        SELECT 
            SUM(heures_estimees) as total_estime,
            SUM(heures_reelles) as total_reel,
            COUNT(CASE WHEN statut = 'terminee' THEN 1 END) as taches_completees,
            COUNT(*) as total_taches
        FROM taches
        WHERE projet_id = %s
        """
        cursor = self.db.cursor()
        cursor.execute(query, (project_id,))
        result = cursor.fetchone()
        
        return {
            'heures_estimees': result[0] or 0,
            'heures_reelles': result[1] or 0,
            'taches_completees': result[2] or 0,
            'total_taches': result[3] or 0,
            'pourcentage_completion': (result[2] / result[3] * 100) if result[3] > 0 else 0
        }