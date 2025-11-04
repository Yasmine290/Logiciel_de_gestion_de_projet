from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict
from dataclasses import dataclass, field

class UserRole(Enum):
    ADMIN = "administrateur"
    PROJECT_MANAGER = "gestionnaire_projet"
    EMPLOYEE = "employe"

class ProjectStatus(Enum):
    DRAFT = "brouillon"
    ACTIVE = "actif"
    PAUSED = "en_pause"
    COMPLETED = "termine"
    CANCELLED = "annule"

class TaskStatus(Enum):
    ACTIVE = "active"
    WAITING = "en_attente"
    IN_PROGRESS = "en_cours"
    COMPLETED = "terminee"
    BLOCKED = "bloquee"
    CANCELLED = "annulee"

class Priority(Enum):
    LOW = "basse"
    NORMAL = "normale"
    HIGH = "haute"
    CRITICAL = "critique"

class TimesheetStatus(Enum):
    DRAFT = "brouillon"
    SUBMITTED = "soumis"
    APPROVED = "approuve"
    REJECTED = "rejete"

@dataclass
class User:
    id: int
    nom: str
    prenom: str
    email: str
    mot_de_passe_hash: str
    role: UserRole
    actif: bool = True
    date_creation: datetime = field(default_factory=datetime.now)
    date_derniere_connexion: Optional[datetime] = None
    telephone: Optional[str] = None
    departement: Optional[str] = None

@dataclass
class Project:
    id: int
    nom: str
    code_projet: str
    description: str
    createur_id: int
    est_template: bool = False
    statut: ProjectStatus = ProjectStatus.ACTIVE
    priorite: Priority = Priority.NORMAL
    date_creation: datetime = field(default_factory=datetime.now)
    date_debut_prevue: Optional[datetime] = None
    date_fin_prevue: Optional[datetime] = None
    date_debut_reelle: Optional[datetime] = None
    date_fin_reelle: Optional[datetime] = None
    budget_estime: float = 0.0
    cout_reel: float = 0.0
    client_nom: Optional[str] = None
    archive: bool = False

@dataclass
class Task:
    id: int
    code_tache: str
    nom: str
    description: str
    projet_id: int
    tache_parent_id: Optional[int] = None
    niveau_profondeur: int = 0
    ordre_affichage: int = 0
    statut: TaskStatus = TaskStatus.ACTIVE
    priorite: Priority = Priority.NORMAL
    heures_estimees: float = 0.0
    heures_reelles: float = 0.0
    pourcentage_completion: int = 0
    date_creation: datetime = field(default_factory=datetime.now)
    date_debut_prevue: Optional[datetime] = None
    date_fin_prevue: Optional[datetime] = None
    date_debut_reelle: Optional[datetime] = None
    date_fin_reelle: Optional[datetime] = None
    createur_id: int = 0
    dependances: List[int] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)

@dataclass
class TimeEntry:
    id: int
    employe_id: int
    tache_id: int
    date_travail: datetime
    heures: float
    description: str = ""
    type_temps: str = "normal"
    approuve: bool = False
    approuve_par_id: Optional[int] = None
    date_approbation: Optional[datetime] = None
    date_creation: datetime = field(default_factory=datetime.now)
    date_modification: Optional[datetime] = None
    modifie: bool = False
    verrouille: bool = False

@dataclass
class TimeSheet:
    id: int
    employe_id: int
    annee: int
    numero_semaine: int
    semaine_debut: datetime
    semaine_fin: datetime
    total_heures: float = 0.0
    statut: TimesheetStatus = TimesheetStatus.DRAFT
    soumis_le: Optional[datetime] = None
    approuve_par_id: Optional[int] = None
    date_approbation: Optional[datetime] = None
    commentaire_gestionnaire: Optional[str] = None
