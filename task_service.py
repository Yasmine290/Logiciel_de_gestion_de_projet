import json
from typing import Optional, List, Dict
from datetime import datetime
from .Permission import PermissionService
from .task_service import Task, TaskStatus
from .models import User, UserRole, Priority 

class TaskService:
    def __init__(self, db_connection):
        self.db = db_connection
        self.permission_service = PermissionService(db_connection)
    
    def generate_task_code(self, project_id: int, parent_id: Optional[int] = None) -> str:
        """Génère un code tâche unique"""
        cursor = self.db.cursor()
        
        if parent_id is None:
            # Tâche racine
            cursor.execute(
                "SELECT MAX(CAST(SUBSTRING(code_tache, -3) AS UNSIGNED)) FROM taches WHERE projet_id = %s AND tache_parent_id IS NULL",
                (project_id,)
            )
            result = cursor.fetchone()
            next_num = (result[0] or 0) + 1
            return f"TSK-{project_id:03d}-{next_num:03d}"
        else:
            # Sous-tâche
            cursor.execute("SELECT code_tache FROM taches WHERE id = %s", (parent_id,))
            parent_code = cursor.fetchone()[0]
            
            cursor.execute(
                "SELECT MAX(CAST(SUBSTRING(code_tache, -2) AS UNSIGNED)) FROM taches WHERE tache_parent_id = %s",
                (parent_id,)
            )
            result = cursor.fetchone()
            next_num = (result[0] or 0) + 1
            return f"{parent_code}.{next_num:02d}"
    
    def calculate_depth(self, parent_id: Optional[int]) -> int:
        """Calcule la profondeur d'une tâche dans la hiérarchie"""
        if parent_id is None:
            return 0
        
        cursor = self.db.cursor()
        cursor.execute("SELECT niveau_profondeur FROM taches WHERE id = %s", (parent_id,))
        result = cursor.fetchone()
        
        return (result[0] + 1) if result else 0
    
    def create_task(self, data: Dict, creator_id: int) -> Task:
        """Crée une nouvelle tâche"""
        projet_id = data['projet_id']
        parent_id = data.get('tache_parent_id')
        
        code_tache = self.generate_task_code(projet_id, parent_id)
        niveau_profondeur = self.calculate_depth(parent_id)
        
        query = """
        INSERT INTO taches (
            code_tache, nom, description, projet_id, tache_parent_id,
            niveau_profondeur, ordre_affichage, statut, priorite,
            heures_estimees, date_creation, date_debut_prevue, date_fin_prevue,
            createur_id, pourcentage_completion
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        cursor = self.db.cursor()
        cursor.execute(query, (
            code_tache,
            data['nom'],
            data.get('description', ''),
            projet_id,
            parent_id,
            niveau_profondeur,
            data.get('ordre_affichage', 0),
            data.get('statut', TaskStatus.ACTIVE.value),
            data.get('priorite', Priority.NORMAL.value),
            data.get('heures_estimees', 0),
            datetime.now(),
            data.get('date_debut_prevue'),
            data.get('date_fin_prevue'),
            creator_id,
            0
        ))
        self.db.commit()
        
        task_id = cursor.lastrowid
        return self.get_task_by_id(task_id)
    
    def get_task_by_id(self, task_id: int) -> Optional[Task]:
        """Récupère une tâche par son ID"""
        cursor = self.db.cursor()
        query = "SELECT * FROM taches WHERE id = %s"
        cursor.execute(query, (task_id,))
        result = cursor.fetchone()
        
        if result:
            return Task(
                id=result[0],
                code_tache=result[1],
                nom=result[2],
                description=result[3],
                projet_id=result[4],
                tache_parent_id=result[5],
                niveau_profondeur=result[6],
                ordre_affichage=result[7],
                statut=TaskStatus(result[8]),
                priorite=Priority(result[9]),
                heures_estimees=result[10],
                heures_reelles=result[11],
                pourcentage_completion=result[12]
            )
        return None
    
    def list_tasks(self, project_id: int, filters: Dict = None, user: User = None) -> List[Task]:
        """Liste les tâches d'un projet avec filtres"""
        base_query = "SELECT * FROM taches WHERE projet_id = %s"
        params = [project_id]
        
        if filters:
            if filters.get('statut'):
                base_query += " AND statut = %s"
                params.append(filters['statut'])
            
            if filters.get('priorite'):
                base_query += " AND priorite = %s"
                params.append(filters['priorite'])
            
            if filters.get('parent_id') is not None:
                if filters['parent_id'] == 'null':
                    base_query += " AND tache_parent_id IS NULL"
                else:
                    base_query += " AND tache_parent_id = %s"
                    params.append(filters['parent_id'])
            
            if filters.get('assigne_a'):
                base_query += """ AND id IN (
                    SELECT tache_id FROM tache_assignations WHERE employe_id = %s
                )"""
                params.append(filters['assigne_a'])
        
        base_query += " ORDER BY ordre_affichage, date_creation"
        
        cursor = self.db.cursor()
        cursor.execute(base_query, tuple(params))
        results = cursor.fetchall()
        
        tasks = []
        for r in results:
            tasks.append(Task(
                id=r[0], code_tache=r[1], nom=r[2], description=r[3],
                projet_id=r[4], tache_parent_id=r[5], niveau_profondeur=r[6]
            ))
        
        return tasks
    
    def get_task_hierarchy(self, task_id: int) -> Dict:
        """Récupère une tâche avec toutes ses sous-tâches (récursif)"""
        task = self.get_task_by_id(task_id)
        if not task:
            return None
        
        cursor = self.db.cursor()
        cursor.execute(
            "SELECT id FROM taches WHERE tache_parent_id = %s ORDER BY ordre_affichage",
            (task_id,)
        )
        subtask_ids = [row[0] for row in cursor.fetchall()]
        
        result = {
            'task': task,
            'subtasks': []
        }
        
        for subtask_id in subtask_ids:
            result['subtasks'].append(self.get_task_hierarchy(subtask_id))
        
        return result
    
    def get_all_subtasks(self, task_id: int) -> List[int]:
        """Récupère tous les IDs de sous-tâches (liste plate)"""
        cursor = self.db.cursor()
        
        # Utiliser une requête récursive CTE
        query = """
        WITH RECURSIVE task_tree AS (
            SELECT id FROM taches WHERE id = %s
            UNION ALL
            SELECT t.id FROM taches t
            INNER JOIN task_tree tt ON t.tache_parent_id = tt.id
        )
        SELECT id FROM task_tree WHERE id != %s
        """
        
        cursor.execute(query, (task_id, task_id))
        return [row[0] for row in cursor.fetchall()]
    
    def update_task(self, task_id: int, data: Dict, user: User) -> bool:
        """Met à jour une tâche"""
        if not self.permission_service.can_edit_task(user, task_id):
            raise PermissionError("Permission refusée")
        
        updates = []
        params = []
        
        allowed_fields = ['nom', 'description', 'statut', 'priorite', 
                         'heures_estimees', 'date_debut_prevue', 'date_fin_prevue',
                         'pourcentage_completion']
        
        for field in allowed_fields:
            if field in data:
                updates.append(f"{field} = %s")
                params.append(data[field])
        
        if not updates:
            return False
        
        query = f"UPDATE taches SET {', '.join(updates)} WHERE id = %s"
        params.append(task_id)
        
        cursor = self.db.cursor()
        cursor.execute(query, tuple(params))
        self.db.commit()
        
        return True
    
    def delete_task(self, task_id: int, user: User, cascade: bool = True) -> bool:
        """Supprime une tâche"""
        if not self.permission_service.can_edit_task(user, task_id):
            raise PermissionError("Permission refusée")
        
        if cascade:
            # Supprimer récursivement les sous-tâches
            subtask_ids = self.get_all_subtasks(task_id)
            for subtask_id in subtask_ids:
                self.delete_task(subtask_id, user, cascade=False)
        
        cursor = self.db.cursor()
        cursor.execute("DELETE FROM taches WHERE id = %s", (task_id,))
        self.db.commit()
        
        return True
    
    def assign_user(self, task_id: int, user_id: int, role: str, assigned_by: int) -> bool:
        """Assigne un utilisateur à une tâche"""
        query = """
        INSERT INTO tache_assignations (
            tache_id, employe_id, role_assignation, date_assignation, assigne_par_id
        ) VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE role_assignation = %s
        """
        
        cursor = self.db.cursor()
        cursor.execute(query, (task_id, user_id, role, datetime.now(), assigned_by, role))
        self.db.commit()
        return True
    
    def unassign_user(self, task_id: int, user_id: int, unassigned_by: int) -> bool:
        """Retire un utilisateur d'une tâche"""
        query = """
        UPDATE tache_assignations 
        SET date_retrait = %s
        WHERE tache_id = %s AND employe_id = %s
        """
        
        cursor = self.db.cursor()
        cursor.execute(query, (datetime.now(), task_id, user_id))
        self.db.commit()
        return True
    
    def get_assigned_users(self, task_id: int) -> List[Dict]:
        """Récupère les utilisateurs assignés à une tâche"""
        query = """
        SELECT u.id, u.nom, u.prenom, u.email, ta.role_assignation, ta.date_assignation
        FROM tache_assignations ta
        JOIN users u ON ta.employe_id = u.id
        WHERE ta.tache_id = %s AND ta.date_retrait IS NULL
        """
        
        cursor = self.db.cursor()
        cursor.execute(query, (task_id,))
        results = cursor.fetchall()
        
        users = []
        for r in results:
            users.append({
                'id': r[0],
                'nom': r[1],
                'prenom': r[2],
                'email': r[3],
                'role': r[4],
                'date_assignation': r[5]
            })
        
        return users
    
    def complete_task(self, task_id: int, user: User) -> bool:
        """Termine/ferme une tâche"""
        # Vérifier que l'utilisateur est assigné
        cursor = self.db.cursor()
        cursor.execute(
            "SELECT 1 FROM tache_assignations WHERE tache_id = %s AND employe_id = %s AND date_retrait IS NULL",
            (task_id, user.id)
        )
        
        if not cursor.fetchone() and user.role != UserRole.ADMIN:
            raise PermissionError("Vous n'êtes pas assigné à cette tâche")
        
        cursor.execute(
            """UPDATE taches 
               SET statut = %s, date_fin_reelle = %s, pourcentage_completion = 100
               WHERE id = %s""",
            (TaskStatus.COMPLETED.value, datetime.now(), task_id)
        )
        self.db.commit()
        
        return True
    
    def move_task(self, task_id: int, new_parent_id: Optional[int], user: User) -> bool:
        """Déplace une tâche dans la hiérarchie"""
        if not self.permission_service.can_edit_task(user, task_id):
            raise PermissionError("Permission refusée")
        
        # Vérifier qu'on ne crée pas de cycle
        if new_parent_id is not None:
            all_subtasks = self.get_all_subtasks(task_id)
            if new_parent_id in all_subtasks:
                raise ValueError("Impossible de déplacer une tâche sous l'une de ses sous-tâches")
        
        niveau_profondeur = self.calculate_depth(new_parent_id)
        
        cursor = self.db.cursor()
        cursor.execute(
            "UPDATE taches SET tache_parent_id = %s, niveau_profondeur = %s WHERE id = %s",
            (new_parent_id, niveau_profondeur, task_id)
        )
        self.db.commit()
        
        return True
    
    def get_task_progress(self, task_id: int) -> Dict:
        """Calcule la progression d'une tâche incluant ses sous-tâches"""
        cursor = self.db.cursor()
        
        # Récupérer toutes les sous-tâches
        query = """
        WITH RECURSIVE task_tree AS (
            SELECT id, heures_estimees, heures_reelles, pourcentage_completion
            FROM taches WHERE id = %s
            
            UNION ALL
            
            SELECT t.id, t.heures_estimees, t.heures_reelles, t.pourcentage_completion
            FROM taches t
            INNER JOIN task_tree tt ON t.tache_parent_id = tt.id
        )
        SELECT 
            SUM(heures_estimees) as total_estime,
            SUM(heures_reelles) as total_reel,
            AVG(pourcentage_completion) as avg_completion
        FROM task_tree
        """
        
        cursor.execute(query, (task_id,))
        result = cursor.fetchone()
        
        return {
            'task_id': task_id,
            'heures_estimees': result[0] or 0,
            'heures_reelles': result[1] or 0,
            'pourcentage_completion': result[2] or 0,
            'variance': (result[1] or 0) - (result[0] or 0)
        }
    
    def add_dependency(self, task_id: int, depends_on_task_id: int) -> bool:
        """Ajoute une dépendance entre tâches"""
        # Vérifier qu'on ne crée pas de cycle
        cursor = self.db.cursor()
        cursor.execute(
            "SELECT dependances FROM taches WHERE id = %s",
            (depends_on_task_id,)
        )
        result = cursor.fetchone()
        
        if result and result[0]:
            existing_deps = json.loads(result[0])
            if task_id in existing_deps:
                raise ValueError("Dépendance circulaire détectée")
        
        # Ajouter la dépendance
        cursor.execute("SELECT dependances FROM taches WHERE id = %s", (task_id,))
        result = cursor.fetchone()
        
        deps = json.loads(result[0]) if result[0] else []
        
        if depends_on_task_id not in deps:
            deps.append(depends_on_task_id)
            cursor.execute(
                "UPDATE taches SET dependances = %s WHERE id = %s",
                (json.dumps(deps), task_id)
            )
            self.db.commit()
        
        return True