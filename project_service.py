from typing import List, Optional, Dict
from datetime import datetime
from .project_service import ProjectStatus
from .Permission import PermissionService
from .project_service import Project
from .models import User, UserRole, Priority
from .task_service import TaskStatus
 
import json

class ProjectService:
    def __init__(self, db_connection):
        self.db = db_connection
        self.permission_service = PermissionService(db_connection)
    
    def generate_project_code(self) -> str:
        """Génère un code projet unique"""
        cursor = self.db.cursor()
        cursor.execute("SELECT MAX(CAST(SUBSTRING(code_projet, 5) AS UNSIGNED)) FROM projets")
        result = cursor.fetchone()
        
        next_num = (result[0] or 0) + 1
        return f"PRJ-{next_num:04d}"
    
    def create_project(self, data: Dict, creator_id: int) -> Project:
        """Crée un nouveau projet"""
        code_projet = self.generate_project_code()
        
        query = """
        INSERT INTO projets (
            nom, code_projet, description, createur_id, est_template, 
            statut, priorite, date_creation, date_debut_prevue, date_fin_prevue,
            budget_estime, client_nom
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        cursor = self.db.cursor()
        cursor.execute(query, (
            data['nom'],
            code_projet,
            data.get('description', ''),
            creator_id,
            data.get('est_template', False),
            data.get('statut', ProjectStatus.ACTIVE.value),
            data.get('priorite', Priority.NORMAL.value),
            datetime.now(),
            data.get('date_debut_prevue'),
            data.get('date_fin_prevue'),
            data.get('budget_estime', 0),
            data.get('client_nom')
        ))
        self.db.commit()
        
        project_id = cursor.lastrowid
        
        # Ajouter le créateur comme membre du projet
        self.add_member(project_id, creator_id, 'chef_projet', creator_id)
        
        return self.get_project_by_id(project_id)
    
    def get_project_by_id(self, project_id: int) -> Optional[Project]:
        """Récupère un projet par son ID"""
        cursor = self.db.cursor()
        query = "SELECT * FROM projets WHERE id = %s"
        cursor.execute(query, (project_id,))
        result = cursor.fetchone()
        
        if result:
            return Project(
                id=result[0],
                nom=result[1],
                code_projet=result[2],
                description=result[3],
                createur_id=result[4],
                est_template=result[5],
                statut=ProjectStatus(result[6]),
                priorite=Priority(result[7])
            )
        return None
    
    def list_projects(self, user: User, filters: Dict = None, 
                     page: int = 1, per_page: int = 20) -> List[Project]:
        """Liste les projets accessibles par l'utilisateur avec filtres"""
        cursor = self.db.cursor()
        offset = (page - 1) * per_page
        
        if user.role == UserRole.ADMIN:
            base_query = "SELECT * FROM projets WHERE 1=1"
            params = []
        elif user.role == UserRole.PROJECT_MANAGER:
            base_query = """
            SELECT DISTINCT p.* FROM projets p
            LEFT JOIN project_members pm ON p.id = pm.projet_id
            WHERE (p.createur_id = %s OR pm.user_id = %s)
            """
            params = [user.id, user.id]
        else:
            base_query = """
            SELECT DISTINCT p.* FROM projets p
            JOIN taches t ON p.id = t.projet_id
            JOIN tache_assignations ta ON t.id = ta.tache_id
            WHERE ta.employe_id = %s
            """
            params = [user.id]
        
        # Ajouter les filtres
        if filters:
            if filters.get('statut'):
                base_query += " AND p.statut = %s"
                params.append(filters['statut'])
            if filters.get('priorite'):
                base_query += " AND p.priorite = %s"
                params.append(filters['priorite'])
            if filters.get('archive') is not None:
                base_query += " AND p.archive = %s"
                params.append(filters['archive'])
        
        base_query += " ORDER BY p.date_creation DESC LIMIT %s OFFSET %s"
        params.extend([per_page, offset])
        
        cursor.execute(base_query, tuple(params))
        results = cursor.fetchall()
        
        projects = []
        for r in results:
            projects.append(Project(
                id=r[0], nom=r[1], code_projet=r[2], description=r[3],
                createur_id=r[4], est_template=r[5]
            ))
        
        return projects
    
    def update_project(self, project_id: int, data: Dict, user: User) -> bool:
        """Met à jour un projet"""
        if not self.permission_service.can_edit_project(user, project_id):
            raise PermissionError("Vous n'avez pas la permission de modifier ce projet")
        
        updates = []
        params = []
        
        allowed_fields = ['nom', 'description', 'statut', 'priorite', 
                         'date_debut_prevue', 'date_fin_prevue', 'budget_estime', 'client_nom']
        
        for field in allowed_fields:
            if field in data:
                updates.append(f"{field} = %s")
                params.append(data[field])
        
        if not updates:
            return False
        
        query = f"UPDATE projets SET {', '.join(updates)} WHERE id = %s"
        params.append(project_id)
        
        cursor = self.db.cursor()
        cursor.execute(query, tuple(params))
        self.db.commit()
        
        return True
    
    def delete_project(self, project_id: int, user: User, force: bool = False) -> bool:
        """Supprime un projet"""
        if not self.permission_service.can_delete_project(user, project_id):
            raise PermissionError("Vous n'avez pas la permission de supprimer ce projet")
        
        project = self.get_project_by_id(project_id)
        
        if project.est_template and not force:
            raise ValueError("Confirmation excessive requise pour supprimer un template")
        
        cursor = self.db.cursor()
        cursor.execute("DELETE FROM projets WHERE id = %s", (project_id,))
        self.db.commit()
        
        return True
    
    def duplicate_from_template(self, template_id: int, new_data: Dict, user: User) -> Project:
        """Duplique un projet à partir d'un template"""
        template = self.get_project_by_id(template_id)
        
        if not template.est_template:
            raise ValueError("Ce projet n'est pas un template")
        
        # Créer le nouveau projet
        new_project_data = {
            'nom': new_data['nom'],
            'description': template.description,
            'est_template': False,
            'date_debut_prevue': new_data.get('date_debut_prevue'),
            'date_fin_prevue': new_data.get('date_fin_prevue'),
            'budget_estime': new_data.get('budget_estime', template.budget_estime),
            'client_nom': new_data.get('client_nom')
        }
        
        new_project = self.create_project(new_project_data, user.id)
        
        # Copier les tâches
        self._copy_tasks_recursive(template_id, new_project.id, None)
        
        return new_project
    
    def _copy_tasks_recursive(self, old_project_id: int, new_project_id: int, 
                             parent_task_id: Optional[int], 
                             old_parent_id: Optional[int] = None):
        """Copie récursivement les tâches"""
        cursor = self.db.cursor()
        
        if old_parent_id is None:
            query = """
            SELECT id, nom, description, heures_estimees, priorite, ordre_affichage
            FROM taches WHERE projet_id = %s AND tache_parent_id IS NULL
            """
            cursor.execute(query, (old_project_id,))
        else:
            query = """
            SELECT id, nom, description, heures_estimees, priorite, ordre_affichage
            FROM taches WHERE projet_id = %s AND tache_parent_id = %s
            """
            cursor.execute(query, (old_project_id, old_parent_id))
        
        tasks = cursor.fetchall()
        
        for task in tasks:
            old_task_id = task[0]
            
            # Créer la nouvelle tâche
            insert_query = """
            INSERT INTO taches (
                nom, description, projet_id, tache_parent_id, 
                heures_estimees, priorite, ordre_affichage, date_creation,
                code_tache, statut
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            task_code = f"TSK-{new_project_id:03d}-{task[5]:03d}"
            
            cursor.execute(insert_query, (
                task[1], task[2], new_project_id, parent_task_id,
                task[3], task[4], task[5], datetime.now(),
                task_code, TaskStatus.ACTIVE.value
            ))
            
            new_task_id = cursor.lastrowid
            
            # Copier les sous-tâches
            self._copy_tasks_recursive(old_project_id, new_project_id, 
                                      new_task_id, old_task_id)
        
        self.db.commit()
    
    def add_member(self, project_id: int, user_id: int, role: str, added_by: int) -> bool:
        """Ajoute un membre au projet"""
        query = """
        INSERT INTO project_members (projet_id, user_id, role_projet, date_ajout, actif)
        VALUES (%s, %s, %s, %s, TRUE)
        ON DUPLICATE KEY UPDATE actif = TRUE, date_retrait = NULL
        """
        
        cursor = self.db.cursor()
        cursor.execute(query, (project_id, user_id, role, datetime.now()))
        self.db.commit()
        return True
    
    def remove_member(self, project_id: int, user_id: int, removed_by: int) -> bool:
        """Retire un membre du projet"""
        query = """
        UPDATE project_members 
        SET actif = FALSE, date_retrait = %s
        WHERE projet_id = %s AND user_id = %s
        """
        
        cursor = self.db.cursor()
        cursor.execute(query, (datetime.now(), project_id, user_id))
        self.db.commit()
        return True
    
    def get_project_statistics(self, project_id: int) -> Dict:
        """Récupère les statistiques d'un projet"""
        cursor = self.db.cursor()
        
        # Stats des tâches
        query = """
        SELECT 
            COUNT(*) as total_taches,
            SUM(CASE WHEN statut = 'terminee' THEN 1 ELSE 0 END) as taches_terminees,
            SUM(heures_estimees) as heures_estimees_total,
            SUM(heures_reelles) as heures_reelles_total
        FROM taches
        WHERE projet_id = %s
        """
        cursor.execute(query, (project_id,))
        result = cursor.fetchone()
        
        total_taches = result[0] or 0
        taches_terminees = result[1] or 0
        heures_estimees = result[2] or 0
        heures_reelles = result[3] or 0
        
        # Nombre de membres
        cursor.execute(
            "SELECT COUNT(*) FROM project_members WHERE projet_id = %s AND actif = TRUE",
            (project_id,)
        )
        nb_membres = cursor.fetchone()[0]
        
        return {
            'total_taches': total_taches,
            'taches_terminees': taches_terminees,
            'taches_en_cours': total_taches - taches_terminees,
            'pourcentage_completion': (taches_terminees / total_taches * 100) if total_taches > 0 else 0,
            'heures_estimees': heures_estimees,
            'heures_reelles': heures_reelles,
            'variance_heures': heures_reelles - heures_estimees,
            'nb_membres': nb_membres
        }
    
    def archive_project(self, project_id: int, user: User) -> bool:
        """Archive un projet"""
        if not self.permission_service.can_edit_project(user, project_id):
            raise PermissionError("Permission refusée")
        
        cursor = self.db.cursor()
        cursor.execute(
            "UPDATE projets SET archive = TRUE WHERE id = %s",
            (project_id,)
        )
        self.db.commit()
        return True
    
    def restore_project(self, project_id: int, user: User) -> bool:
        """Restaure un projet archivé"""
        if not self.permission_service.can_edit_project(user, project_id):
            raise PermissionError("Permission refusée")
        
        cursor = self.db.cursor()
        cursor.execute(
            "UPDATE projets SET archive = FALSE WHERE id = %s",
            (project_id,)
        )
        self.db.commit()
        return True