from .models import User,TimeEntry
from datetime import datetime
from typing import Dict
from .Permission import PermissionService
from typing import Optional 
from .models import UserRole  
from .task_service import TaskStatus
from typing import List
from datetime import datetime, timedelta
from .timetracking_service import TimesheetStatus


class TimeTrackingService:
    def __init__(self, db_connection):
        self.db = db_connection
        self.permission_service = PermissionService(db_connection)
    
    def validate_time_entry(self, data: Dict) -> bool:
        """Valide les données d'une saisie de temps"""
        heures = data.get('heures', 0)
        
        if heures < 0.25 or heures > 24:
            raise ValueError("Les heures doivent être entre 0.25 et 24")
        
        # Vérifier que la tâche n'est pas complétée
        cursor = self.db.cursor()
        cursor.execute(
            "SELECT statut FROM taches WHERE id = %s",
            (data['tache_id'],)
        )
        result = cursor.fetchone()
        
        if result and result[0] == TaskStatus.COMPLETED.value:
            raise ValueError("Impossible de saisir du temps sur une tâche complétée")
        
        return True
    
    def create_time_entry(self, data: Dict, user: User) -> TimeEntry:
        """Crée une saisie de temps"""
        tache_id = data['tache_id']
        
        # Vérifier les permissions
        if not self.permission_service.can_create_timeentry(user, tache_id):
            raise PermissionError("Vous n'êtes pas assigné à cette tâche")
        
        # Valider les données
        self.validate_time_entry(data)
        
        query = """
        INSERT INTO saisies_temps (
            employe_id, tache_id, date_travail, heures, description,
            type_temps, approuve, date_creation
        ) VALUES (%s, %s, %s, %s, %s, %s, FALSE, %s)
        """
        
        cursor = self.db.cursor()
        cursor.execute(query, (
            user.id,
            tache_id,
            data['date_travail'],
            data['heures'],
            data.get('description', ''),
            data.get('type_temps', 'normal'),
            datetime.now()
        ))
        self.db.commit()
        
        entry_id = cursor.lastrowid
        
        # Mettre à jour les heures réelles de la tâche
        self._update_task_actual_hours(tache_id)
        
        return self.get_time_entry(entry_id)
    
    def _update_task_actual_hours(self, tache_id: int):
        """Met à jour les heures réelles d'une tâche"""
        query = """
        UPDATE taches 
        SET heures_reelles = (
            SELECT COALESCE(SUM(heures), 0) 
            FROM saisies_temps 
            WHERE tache_id = %s
        )
        WHERE id = %s
        """
        cursor = self.db.cursor()
        cursor.execute(query, (tache_id, tache_id))
        self.db.commit()
    
    def get_time_entry(self, entry_id: int) -> Optional[TimeEntry]:
        """Récupère une saisie de temps"""
        cursor = self.db.cursor()
        query = "SELECT * FROM saisies_temps WHERE id = %s"
        cursor.execute(query, (entry_id,))
        result = cursor.fetchone()
        
        if result:
            return TimeEntry(
                id=result[0],
                employe_id=result[1],
                tache_id=result[2],
                date_travail=result[3],
                heures=result[4],
                description=result[5],
                type_temps=result[6],
                approuve=result[7]
            )
        return None
    
    def get_week_entries(self, user_id: int, week_start: datetime) -> List[TimeEntry]:
        """Récupère les saisies d'une semaine"""
        week_end = week_start + timedelta(days=7)
        
        query = """
        SELECT * FROM saisies_temps
        WHERE employe_id = %s AND date_travail >= %s AND date_travail < %s
        ORDER BY date_travail, id
        """
        
        cursor = self.db.cursor()
        cursor.execute(query, (user_id, week_start, week_end))
        results = cursor.fetchall()
        
        entries = []
        for r in results:
            entries.append(TimeEntry(
                id=r[0], employe_id=r[1], tache_id=r[2],
                date_travail=r[3], heures=r[4], description=r[5]
            ))
        
        return entries
    
    def update_time_entry(self, entry_id: int, data: Dict, user: User) -> bool:
        """Met à jour une saisie de temps"""
        if not self.permission_service.can_edit_timeentry(user, entry_id):
            raise PermissionError("Permission refusée ou saisie verrouillée")
        
        updates = []
        params = []
        
        if 'heures' in data:
            if data['heures'] < 0.25 or data['heures'] > 24:
                raise ValueError("Heures invalides")
            updates.append("heures = %s")
            params.append(data['heures'])
        
        if 'description' in data:
            updates.append("description = %s")
            params.append(data['description'])
        
        if 'date_travail' in data:
            updates.append("date_travail = %s")
            params.append(data['date_travail'])
        
        if not updates:
            return False
        
        updates.append("modifie = TRUE")
        updates.append("date_modification = %s")
        params.append(datetime.now())
        
        query = f"UPDATE saisies_temps SET {', '.join(updates)} WHERE id = %s"
        params.append(entry_id)
        
        cursor = self.db.cursor()
        cursor.execute(query, tuple(params))
        self.db.commit()
        
        # Mettre à jour les heures de la tâche
        entry = self.get_time_entry(entry_id)
        self._update_task_actual_hours(entry.tache_id)
        
        return True
    
    def delete_time_entry(self, entry_id: int, user: User) -> bool:
        """Supprime une saisie de temps"""
        if not self.permission_service.can_edit_timeentry(user, entry_id):
            raise PermissionError("Permission refusée ou saisie verrouillée")
        
        entry = self.get_time_entry(entry_id)
        tache_id = entry.tache_id
        
        cursor = self.db.cursor()
        cursor.execute("DELETE FROM saisies_temps WHERE id = %s", (entry_id,))
        self.db.commit()
        
        # Mettre à jour les heures de la tâche
        self._update_task_actual_hours(tache_id)
        
        return True
    
    def submit_timesheet(self, user_id: int, week_start: datetime) -> bool:
        """Soumet une feuille de temps pour approbation"""
        week_end = week_start + timedelta(days=7)
        year = week_start.year
        week_num = week_start.isocalendar()[1]
        
        # Calculer le total d'heures
        cursor = self.db.cursor()
        cursor.execute(
            """SELECT COALESCE(SUM(heures), 0) FROM saisies_temps
               WHERE employe_id = %s AND date_travail >= %s AND date_travail < %s""",
            (user_id, week_start, week_end)
        )
        total_heures = cursor.fetchone()[0]
        
        # Créer ou mettre à jour la feuille de temps
        query = """
        INSERT INTO timesheets (
            employe_id, annee, numero_semaine, semaine_debut, semaine_fin,
            total_heures, statut, soumis_le
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE 
            total_heures = %s, statut = %s, soumis_le = %s
        """
        
        now = datetime.now()
        cursor.execute(query, (
            user_id, year, week_num, week_start, week_end,
            total_heures, TimesheetStatus.SUBMITTED.value, now,
            total_heures, TimesheetStatus.SUBMITTED.value, now
        ))
        self.db.commit()
        
        return True
    
    def approve_timesheet(self, timesheet_id: int, manager: User, comment: str = None) -> bool:
        """Approuve une feuille de temps"""
        cursor = self.db.cursor()
        
        # Récupérer la feuille de temps
        cursor.execute("SELECT employe_id FROM timesheets WHERE id = %s", (timesheet_id,))
        result = cursor.fetchone()
        
        if not result:
            raise ValueError("Feuille de temps introuvable")
        
        employee_id = result[0]
        
        if not self.permission_service.can_approve_timesheet(manager, employee_id):
            raise PermissionError("Permission refusée")
        
        # Approuver la feuille
        cursor.execute(
            """UPDATE timesheets 
               SET statut = %s, approuve_par_id = %s, date_approbation = %s, commentaire_gestionnaire = %s
               WHERE id = %s""",
            (TimesheetStatus.APPROVED.value, manager.id, datetime.now(), comment, timesheet_id)
        )
        
        # Verrouiller toutes les saisies de la semaine
        cursor.execute(
            """SELECT semaine_debut, semaine_fin FROM timesheets WHERE id = %s""",
            (timesheet_id,)
        )
        week_start, week_end = cursor.fetchone()
        
        cursor.execute(
            """UPDATE saisies_temps 
               SET approuve = TRUE, verrouille = TRUE, approuve_par_id = %s, date_approbation = %s
               WHERE employe_id = %s AND date_travail >= %s AND date_travail < %s""",
            (manager.id, datetime.now(), employee_id, week_start, week_end)
        )
        
        self.db.commit()
        return True
    
    def reject_timesheet(self, timesheet_id: int, manager: User, reason: str) -> bool:
        """Rejette une feuille de temps"""
        cursor = self.db.cursor()
        
        cursor.execute("SELECT employe_id FROM timesheets WHERE id = %s", (timesheet_id,))
        result = cursor.fetchone()
        
        if not result:
            raise ValueError("Feuille de temps introuvable")
        
        employee_id = result[0]
        
        if not self.permission_service.can_approve_timesheet(manager, employee_id):
            raise PermissionError("Permission refusée")
        
        cursor.execute(
            """UPDATE timesheets 
               SET statut = %s, commentaire_gestionnaire = %s
               WHERE id = %s""",
            (TimesheetStatus.REJECTED.value, reason, timesheet_id)
        )
        self.db.commit()
        
        return True
    
    def get_pending_timesheets(self, manager_id: int) -> List[Dict]:
        """Récupère les feuilles de temps en attente d'approbation"""
        cursor = self.db.cursor()
        
        query = """
        SELECT ts.id, ts.employe_id, u.nom, u.prenom, ts.semaine_debut, 
               ts.semaine_fin, ts.total_heures, ts.soumis_le
        FROM timesheets ts
        JOIN users u ON ts.employe_id = u.id
        JOIN taches t ON t.id IN (
            SELECT DISTINCT tache_id FROM saisies_temps 
            WHERE employe_id = ts.employe_id 
            AND date_travail >= ts.semaine_debut 
            AND date_travail < ts.semaine_fin
        )
        JOIN projets p ON t.projet_id = p.id
        WHERE ts.statut = %s AND p.createur_id = %s
        GROUP BY ts.id
        ORDER BY ts.soumis_le DESC
        """
        
        cursor.execute(query, (TimesheetStatus.SUBMITTED.value, manager_id))
        results = cursor.fetchall()
        
        timesheets = []
        for r in results:
            timesheets.append({
                'id': r[0],
                'employe_id': r[1],
                'employe_nom': f"{r[2]} {r[3]}",
                'semaine_debut': r[4],
                'semaine_fin': r[5],
                'total_heures': r[6],
                'soumis_le': r[7]
            })
        
        return timesheets
    
    def get_timesheet_summary(self, user_id: int, week_start: datetime) -> Dict:
        """Récupère un résumé de la feuille de temps"""
        entries = self.get_week_entries(user_id, week_start)
        
        total_heures = sum(e.heures for e in entries)
        nb_saisies = len(entries)
        toutes_approuvees = all(e.approuve for e in entries) if entries else False
        
        # Grouper par tâche
        by_task = {}
        for entry in entries:
            if entry.tache_id not in by_task:
                by_task[entry.tache_id] = {
                    'entries': [],
                    'total_heures': 0
                }
            by_task[entry.tache_id]['entries'].append(entry)
            by_task[entry.tache_id]['total_heures'] += entry.heures
        
        # Grouper par jour
        by_day = {}
        for entry in entries:
            day = entry.date_travail.date()
            if day not in by_day:
                by_day[day] = {
                    'entries': [],
                    'total_heures': 0
                }
            by_day[day]['entries'].append(entry)
            by_day[day]['total_heures'] += entry.heures
        
        return {
            'user_id': user_id,
            'semaine_debut': week_start,
            'total_heures': total_heures,
            'nb_saisies': nb_saisies,
            'approuve': toutes_approuvees,
            'entries': entries,
            'by_task': by_task,
            'by_day': by_day
        }
