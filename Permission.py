from .models import User, UserRole

class PermissionService:
    def __init__(self, db_connection):
        self.db = db_connection
    
    def can_view_project(self, user: User, project_id: int) -> bool:
        """Vérifie si l'utilisateur peut voir le projet"""
        if user.role == UserRole.ADMIN:
            return True
        
        cursor = self.db.cursor()
        
        # Vérifier si gestionnaire du projet
        cursor.execute(
            "SELECT 1 FROM projets WHERE id = %s AND createur_id = %s",
            (project_id, user.id)
        )
        if cursor.fetchone():
            return True
        
        # Vérifier si membre du projet
        cursor.execute(
            "SELECT 1 FROM project_members WHERE projet_id = %s AND user_id = %s AND actif = TRUE",
            (project_id, user.id)
        )
        if cursor.fetchone():
            return True
        
        # Vérifier si assigné à une tâche du projet
        cursor.execute(
            """SELECT 1 FROM tache_assignations ta
               JOIN taches t ON ta.tache_id = t.id
               WHERE t.projet_id = %s AND ta.employe_id = %s""",
            (project_id, user.id)
        )
        if cursor.fetchone():
            return True
        
        return False
    
    def can_edit_project(self, user: User, project_id: int) -> bool:
        """Vérifie si l'utilisateur peut modifier le projet"""
        if user.role == UserRole.ADMIN:
            return True
        
        cursor = self.db.cursor()
        cursor.execute(
            "SELECT createur_id FROM projets WHERE id = %s",
            (project_id,)
        )
        result = cursor.fetchone()
        
        if result and result[0] == user.id:
            return True
        
        return False
    
    def can_delete_project(self, user: User, project_id: int) -> bool:
        """Vérifie si l'utilisateur peut supprimer le projet"""
        return user.role == UserRole.ADMIN or self.can_edit_project(user, project_id)
    
    def can_manage_project_members(self, user: User, project_id: int) -> bool:
        """Vérifie si l'utilisateur peut gérer les membres du projet"""
        return self.can_edit_project(user, project_id)
    
    def can_view_task(self, user: User, task_id: int) -> bool:
        """Vérifie si l'utilisateur peut voir la tâche"""
        if user.role == UserRole.ADMIN:
            return True
        
        cursor = self.db.cursor()
        
        # Récupérer le projet de la tâche
        cursor.execute("SELECT projet_id FROM taches WHERE id = %s", (task_id,))
        result = cursor.fetchone()
        
        if not result:
            return False
        
        project_id = result[0]
        
        # Vérifier accès au projet
        if self.can_view_project(user, project_id):
            return True
        
        # Vérifier si assigné à la tâche
        cursor.execute(
            "SELECT 1 FROM tache_assignations WHERE tache_id = %s AND employe_id = %s",
            (task_id, user.id)
        )
        if cursor.fetchone():
            return True
        
        return False
    
    def can_edit_task(self, user: User, task_id: int) -> bool:
        """Vérifie si l'utilisateur peut modifier la tâche"""
        if user.role == UserRole.ADMIN:
            return True
        
        cursor = self.db.cursor()
        cursor.execute("SELECT projet_id FROM taches WHERE id = %s", (task_id,))
        result = cursor.fetchone()
        
        if result:
            return self.can_edit_project(user, result[0])
        
        return False
    
    def can_create_timeentry(self, user: User, task_id: int) -> bool:
        """Vérifie si l'utilisateur peut créer une saisie de temps"""
        cursor = self.db.cursor()
        
        # Vérifier si assigné à la tâche
        cursor.execute(
            "SELECT 1 FROM tache_assignations WHERE tache_id = %s AND employe_id = %s",
            (task_id, user.id)
        )
        
        return cursor.fetchone() is not None
    
    def can_edit_timeentry(self, user: User, entry_id: int) -> bool:
        """Vérifie si l'utilisateur peut modifier la saisie"""
        cursor = self.db.cursor()
        cursor.execute(
            "SELECT employe_id, verrouille FROM saisies_temps WHERE id = %s",
            (entry_id,)
        )
        result = cursor.fetchone()
        
        if not result:
            return False
        
        employe_id, verrouille = result
        
        # Admin peut tout modifier
        if user.role == UserRole.ADMIN:
            return True
        
        # Pas de modification si verrouillé
        if verrouille:
            return False
        
        # L'employé peut modifier sa propre saisie
        return employe_id == user.id
    
    def can_approve_timesheet(self, user: User, employee_id: int) -> bool:
        """Vérifie si l'utilisateur peut approuver une feuille de temps"""
        if user.role == UserRole.ADMIN:
            return True
        
        if user.role == UserRole.PROJECT_MANAGER:
            # Vérifier si gestionnaire d'un projet où l'employé a des tâches
            cursor = self.db.cursor()
            cursor.execute(
                """SELECT 1 FROM projets p
                   JOIN taches t ON p.id = t.projet_id
                   JOIN tache_assignations ta ON t.id = ta.tache_id
                   WHERE p.createur_id = %s AND ta.employe_id = %s
                   LIMIT 1""",
                (user.id, employee_id)
            )
            return cursor.fetchone() is not None
        
        return False
    
    def is_project_member(self, user_id: int, project_id: int) -> bool:
        """Vérifie si l'utilisateur est membre du projet"""
        cursor = self.db.cursor()
        cursor.execute(
            """SELECT 1 FROM project_members 
               WHERE projet_id = %s AND user_id = %s AND actif = TRUE""",
            (project_id, user_id)
        )
        return cursor.fetchone() is not None
