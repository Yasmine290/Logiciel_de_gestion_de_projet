from typing import List, Dict
from .models import User
from .project_service import ProjectService
from .task_service import TaskService
from .project_service import ProjectStatus
from datetime import datetime, timedelta
from .timetracking_service import TimeTrackingService

class DashboardService:
    def __init__(self, db_connection):
        self.db = db_connection
        self.project_service = ProjectService(db_connection)
        self.task_service = TaskService(db_connection)
        self.time_service = TimeTrackingService(db_connection)
    
    def get_user_dashboard(self, user: User) -> Dict:
        """Récupère le tableau de bord personnalisé d'un utilisateur"""
        return {
            'user': {
                'id': user.id,
                'nom': f"{user.nom} {user.prenom}",
                'role': user.role.value
            },
            'projets_actifs': self._get_active_projects_summary(user),
            'mes_taches': self._get_user_tasks_summary(user),
            'temps_cette_semaine': self._get_current_week_time(user),
            'taches_en_retard': self._get_overdue_tasks(user),
            'echeances_proches': self._get_upcoming_deadlines(user),
            'notifications': self._get_recent_notifications(user)
        }
    
    def _get_active_projects_summary(self, user: User) -> List[Dict]:
        """Résumé des projets actifs"""
        projects = self.project_service.list_projects(
            user, 
            filters={'statut': ProjectStatus.ACTIVE.value, 'archive': False}
        )
        
        summaries = []
        for project in projects[:5]:  # Top 5
            stats = self.project_service.get_project_statistics(project.id)
            summaries.append({
                'id': project.id,
                'nom': project.nom,
                'code': project.code_projet,
                'progression': stats['pourcentage_completion'],
                'taches_total': stats['total_taches'],
                'taches_terminees': stats['taches_terminees']
            })
        
        return summaries
    
    def _get_user_tasks_summary(self, user: User) -> Dict:
        """Résumé des tâches de l'utilisateur"""
        cursor = self.db.cursor()
        
        query = """
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN t.statut = 'en_cours' THEN 1 ELSE 0 END) as en_cours,
            SUM(CASE WHEN t.statut = 'terminee' THEN 1 ELSE 0 END) as terminees,
            SUM(CASE WHEN t.date_fin_prevue < CURDATE() AND t.statut != 'terminee' THEN 1 ELSE 0 END) as en_retard
        FROM taches t
        JOIN tache_assignations ta ON t.id = ta.tache_id
        WHERE ta.employe_id = %s AND ta.date_retrait IS NULL
        """
        
        cursor.execute(query, (user.id,))
        result = cursor.fetchone()
        
        return {
            'total': result[0] or 0,
            'en_cours': result[1] or 0,
            'terminees': result[2] or 0,
            'en_retard': result[3] or 0
        }
    
    def _get_current_week_time(self, user: User) -> Dict:
        """Temps saisi cette semaine"""
        from datetime import date
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        
        cursor = self.db.cursor()
        cursor.execute(
            """SELECT COALESCE(SUM(heures), 0) FROM saisies_temps
               WHERE employe_id = %s AND date_travail >= %s""",
            (user.id, week_start)
        )
        
        total_heures = cursor.fetchone()[0]
        
        return {
            'semaine_debut': week_start,
            'total_heures': total_heures,
            'objectif': 40,  # Heures standard
            'pourcentage': (total_heures / 40 * 100) if total_heures else 0
        }
    
    def _get_overdue_tasks(self, user: User) -> List[Dict]:
        """Tâches en retard"""
        cursor = self.db.cursor()
        
        query = """
        SELECT t.id, t.nom, t.date_fin_prevue, p.nom as projet_nom
        FROM taches t
        JOIN projets p ON t.projet_id = p.id
        JOIN tache_assignations ta ON t.id = ta.tache_id
        WHERE ta.employe_id = %s 
        AND t.date_fin_prevue < CURDATE()
        AND t.statut != 'terminee'
        AND ta.date_retrait IS NULL
        ORDER BY t.date_fin_prevue
        LIMIT 10
        """
        
        cursor.execute(query, (user.id,))
        results = cursor.fetchall()
        
        tasks = []
        for r in results:
            tasks.append({
                'id': r[0],
                'nom': r[1],
                'date_fin_prevue': r[2],
                'projet_nom': r[3],
                'jours_retard': (datetime.now().date() - r[2]).days
            })
        
        return tasks
    
    def _get_upcoming_deadlines(self, user: User, days: int = 7) -> List[Dict]:
        """Échéances dans les prochains jours"""
        cursor = self.db.cursor()
        
        query = """
        SELECT t.id, t.nom, t.date_fin_prevue, p.nom as projet_nom, t.priorite
        FROM taches t
        JOIN projets p ON t.projet_id = p.id
        JOIN tache_assignations ta ON t.id = ta.tache_id
        WHERE ta.employe_id = %s 
        AND t.date_fin_prevue BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL %s DAY)
        AND t.statut != 'terminee'
        AND ta.date_retrait IS NULL
        ORDER BY t.date_fin_prevue, t.priorite DESC
        LIMIT 10
        """
        
        cursor.execute(query, (user.id, days))
        results = cursor.fetchall()
        
        tasks = []
        for r in results:
            tasks.append({
                'id': r[0],
                'nom': r[1],
                'date_fin_prevue': r[2],
                'projet_nom': r[3],
                'priorite': r[4],
                'jours_restants': (r[2] - datetime.now().date()).days
            })
        
        return tasks
    
    def _get_recent_notifications(self, user: User) -> List[Dict]:
        """Notifications récentes"""
        cursor = self.db.cursor()
        
        query = """
        SELECT id, type, titre, message, date_creation, lue
        FROM notifications
        WHERE user_id = %s
        ORDER BY date_creation DESC
        LIMIT 10
        """
        
        cursor.execute(query, (user.id,))
        results = cursor.fetchall()
        
        notifications = []
        for r in results:
            notifications.append({
                'id': r[0],
                'type': r[1],
                'titre': r[2],
                'message': r[3],
                'date_creation': r[4],
                'lue': r[5]
            })
        
        return notifications
    
    def get_project_gantt_data(self, project_id: int) -> Dict:
        """Récupère les données pour un diagramme de Gantt"""
        cursor = self.db.cursor()
        
        query = """
        SELECT 
            t.id, t.nom, t.date_debut_prevue, t.date_fin_prevue,
            t.date_debut_reelle, t.date_fin_reelle, t.statut,
            t.tache_parent_id, t.pourcentage_completion,
            GROUP_CONCAT(DISTINCT u.nom SEPARATOR ', ') as assignes
        FROM taches t
        LEFT JOIN tache_assignations ta ON t.id = ta.tache_id AND ta.date_retrait IS NULL
        LEFT JOIN users u ON ta.employe_id = u.id
        WHERE t.projet_id = %s
        GROUP BY t.id
        ORDER BY t.ordre_affichage
        """
        
        cursor.execute(query, (project_id,))
        results = cursor.fetchall()
        
        tasks = []
        for r in results:
            task = {
                'id': r[0],
                'nom': r[1],
                'date_debut_prevue': r[2],
                'date_fin_prevue': r[3],
                'date_debut_reelle': r[4],
                'date_fin_reelle': r[5],
                'statut': r[6],
                'parent_id': r[7],
                'progression': r[8],
                'assignes': r[9] or ''
            }
            
            # Calculer la durée en jours
            if r[2] and r[3]:
                task['duree_jours'] = (r[3] - r[2]).days
            
            tasks.append(task)
        
        return {
            'project_id': project_id,
            'tasks': tasks,
            'date_min': min((t['date_debut_prevue'] for t in tasks if t['date_debut_prevue']), default=None),
            'date_max': max((t['date_fin_prevue'] for t in tasks if t['date_fin_prevue']), default=None)
        }
