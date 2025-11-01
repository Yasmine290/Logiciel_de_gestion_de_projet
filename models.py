from datetime import datetime
from enum import Enum
from typing import Optional, List

class UserRole(Enum):
    ADMIN = "administrateur"
    PROJECT_MANAGER = "gestionnaire_projet"
    EMPLOYEE = "employe"

class TaskStatus(Enum):
    ACTIVE = "active"
    WAITING = "en_attente"
    COMPLETED = "terminee"

class User:
    def __init__(self, id: int, nom: str, email: str, role: UserRole, mot_de_passe_hash: str):
        self.id = id
        self.nom = nom
        self.email = email
        self.role = role
        self.mot_de_passe_hash = mot_de_passe_hash
        self.date_creation = datetime.now()

class Project:
    def __init__(self, id: int, nom: str, description: str, createur_id: int, 
                 est_template: bool = False):
        self.id = id
        self.nom = nom
        self.description = description
        self.createur_id = createur_id
        self.est_template = est_template
        self.date_creation = datetime.now()
        self.date_debut = None
        self.date_fin_prevue = None

class Task:
    def __init__(self, id: int, nom: str, description: str, projet_id: int,
                 tache_parent_id: Optional[int] = None):
        self.id = id
        self.nom = nom
        self.description = description
        self.projet_id = projet_id
        self.tache_parent_id = tache_parent_id
        self.statut = TaskStatus.ACTIVE
        self.heures_estimees = 0.0
        self.heures_reelles = 0.0
        self.date_creation = datetime.now()
        self.date_debut = None
        self.date_fin_prevue = None
        self.assignes: List[int] = []  # Liste des user_id

class TimeEntry:
    def __init__(self, id: int, employe_id: int, tache_id: int, 
                 date: datetime, heures: float, description: str = ""):
        self.id = id
        self.employe_id = employe_id
        self.tache_id = tache_id
        self.date = date
        self.heures = heures
        self.description = description
        self.approuve = False
        self.approuve_par_id = None
        self.date_approbation = None

class TimeSheet:
    def __init__(self, id: int, employe_id: int, semaine_debut: datetime):
        self.id = id
        self.employe_id = employe_id
        self.semaine_debut = semaine_debut
        self.entrees: List[TimeEntry] = []
        self.approuve = False
        self.approuve_par_id = None
        self.date_approbation = None