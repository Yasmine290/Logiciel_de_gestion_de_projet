from typing import List, Optional
from datetime import datetime, timedelta
from models import TimeEntry, TimeSheet, TaskStatus

class TimeTrackingService:
    def __init__(self, db_connection):
        self.db = db_connection
    
    def create_time_entry(self, employe_id: int, tache_id: int, 
                         date: datetime, heures: float, 
                         description: str = "") -> TimeEntry:
        """Crée une saisie de temps"""
        # Vérifier que la tâche n'est pas complétée
        query = "SELECT statut FROM taches WHERE id = %s"
        cursor = self.db.cursor()
        cursor.execute(query, (tache_id,))
        result = cursor.fetchone()
        
        if result and result[0] == TaskStatus.COMPLETED.value:
            raise ValueError("Impossible de saisir du temps sur une tâche complétée")
        
        # Vérifier que l'employé est assigné à la tâche
        query = "SELECT 1 FROM tache_assignations WHERE tache_id = %s AND employe_id = %s"
        cursor.execute(query, (tache_id, employe_id))
        if not cursor.fetchone():
            raise ValueError("L'employé n'est pas assigné à cette tâche")
        
        # Créer la saisie
        query = """
        INSERT INTO saisies_temps (employe_id, tache_id, date, heures, 
                                   description, approuve)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (employe_id, tache_id, date, heures, description, False))
        self.db.commit()
        
        entry_id = cursor.lastrowid
        
        # Mettre à jour les heures réelles de la tâche
        self._update_task_actual_hours(tache_id)
        
        return TimeEntry(entry_id, employe_id, tache_id, date, heures, description)
    
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
    
    def get_time_entries_for_week(self, employe_id: int, 
                                  week_start: datetime) -> List[TimeEntry]:
        """Récupère les saisies de temps d'un employé pour une semaine"""
        week_end = week_start + timedelta(days=7)
        
        query = """
        SELECT * FROM saisies_temps
        WHERE employe_id = %s AND date >= %s AND date < %s
        ORDER BY date
        """
        cursor = self.db.cursor()
        cursor.execute(query, (employe_id, week_start, week_end))
        results = cursor.fetchall()
        
        entries = []
        for r in results:
            entry = TimeEntry(r[0], r[1], r[2], r[3], r[4], r[5])
            entry.approuve = r[6]
            entries.append(entry)
        
        return entries
    
    def update_time_entry(self, entry_id: int, heures: float = None, 
                         description: str = None) -> bool:
        """Met à jour une saisie de temps (si non approuvée)"""
        # Vérifier que la saisie n'est pas approuvée
        query = "SELECT approuve, tache_id FROM saisies_temps WHERE id = %s"
        cursor = self.db.cursor()
        cursor.execute(query, (entry_id,))
        result = cursor.fetchone()
        
        if result[0]:
            raise ValueError("Impossible de modifier une saisie approuvée")
        
        updates = []
        params = []
        
        if heures is not None:
            updates.append("heures = %s")
            params.append(heures)
        if description is not None:
            updates.append("description = %s")
            params.append(description)
        
        if not updates:
            return False
        
        query = f"UPDATE saisies_temps SET {', '.join(updates)} WHERE id = %s"
        params.append(entry_id)
        
        cursor.execute(query, tuple(params))
        self.db.commit()
        
        # Mettre à jour les heures réelles de la tâche
        self._update_task_actual_hours(result[1])
        
        return True
    
    def delete_time_entry(self, entry_id: int) -> bool:
        """Supprime une saisie de temps (si non approuvée)"""
        # Vérifier que la saisie n'est pas approuvée
        query = "SELECT approuve, tache_id FROM saisies_temps WHERE id = %s"
        cursor = self.db.cursor()
        cursor.execute(query, (entry_id,))
        result = cursor.fetchone()
        
        if result[0]:
            raise ValueError("Impossible de supprimer une saisie approuvée")
        
        tache_id = result[1]
        
        query = "DELETE FROM saisies_temps WHERE id = %s"
        cursor.execute(query, (entry_id,))
        self.db.commit()
        
        # Mettre à jour les heures réelles de la tâche
        self._update_task_actual_hours(tache_id)
        
        return True
    
    def approve_timesheet(self, employe_id: int, week_start: datetime, 
                         gestionnaire_id: int) -> bool:
        """Approuve toutes les saisies de temps d'un employé pour une semaine"""
        week_end = week_start + timedelta(days=7)
        
        query = """
        UPDATE saisies_temps
        SET approuve = TRUE, 
            approuve_par_id = %s,
            date_approbation = %s
        WHERE employe_id = %s AND date >= %s AND date < %s AND approuve = FALSE
        """
        cursor = self.db.cursor()
        cursor.execute(query, (gestionnaire_id, datetime.now(), 
                              employe_id, week_start, week_end))
        self.db.commit()
        
        return cursor.rowcount > 0
    
    def get_time_entries_by_task(self, tache_id: int) -> List[TimeEntry]:
        """Récupère toutes les saisies de temps pour une tâche"""
        query = """
        SELECT * FROM saisies_temps
        WHERE tache_id = %s
        ORDER BY date DESC
        """
        cursor = self.db.cursor()
        cursor.execute(query, (tache_id,))
        results = cursor.fetchall()
        
        entries = []
        for r in results:
            entry = TimeEntry(r[0], r[1], r[2], r[3], r[4], r[5])
            entry.approuve = r[6]
            entries.append(entry)
        
        return entries
    
    def get_pending_approvals(self, gestionnaire_id: int) -> List[dict]:
        """Récupère les feuilles de temps en attente d'approbation"""
        query = """
        SELECT DISTINCT 
            st.employe_id,
            u.nom,
            DATE(st.date) as semaine,
            COUNT(*) as nb_saisies,
            SUM(st.heures) as total_heures
        FROM saisies_temps st
        JOIN users u ON st.employe_id = u.id
        JOIN taches t ON st.tache_id = t.id
        JOIN projets p ON t.projet_id = p.id
        WHERE st.approuve = FALSE 
        AND p.createur_id = %s
        GROUP BY st.employe_id, u.nom, DATE(st.date)
        ORDER BY semaine DESC
        """
        cursor = self.db.cursor()
        cursor.execute(query, (gestionnaire_id,))
        results = cursor.fetchall()
        
        approvals = []
        for r in results:
            approvals.append({
                'employe_id': r[0],
                'employe_nom': r[1],
                'semaine': r[2],
                'nb_saisies': r[3],
                'total_heures': r[4]
            })
        
        return approvals
    
    def get_timesheet_summary(self, employe_id: int, 
                             week_start: datetime) -> dict:
        """Récupère un résumé de la feuille de temps d'un employé"""
        entries = self.get_time_entries_for_week(employe_id, week_start)
        
        total_heures = sum(e.heures for e in entries)
        nb_saisies = len(entries)
        toutes_approuvees = all(e.approuve for e in entries) if entries else False
        
        # Grouper par tâche
        by_task = {}
        for entry in entries:
            if entry.tache_id not in by_task:
                by_task[entry.tache_id] = []
            by_task[entry.tache_id].append(entry)
        
        return {
            'employe_id': employe_id,
            'semaine_debut': week_start,
            'total_heures': total_heures,
            'nb_saisies': nb_saisies,
            'approuve': toutes_approuvees,
            'entries': entries,
            'by_task': by_task
        }