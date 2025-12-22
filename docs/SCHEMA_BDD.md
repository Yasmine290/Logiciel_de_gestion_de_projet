# Schema de la base de données

Base de données : `project_time_gestion`

## Diagramme de la base de données

Voici le diagramme visuel de l'architecture de la base de données (tables actuellement utilisées) :

![Diagramme de la base de données](schema_database.png)

## Tables principales

### 1. Gestion des utilisateurs et permissions

#### Table `role`
Définit les rôles utilisateur dans le système.

| Colonne | Type | Contraintes | Description |
|---------|------|-------------|-------------|
| idRole | INT | PRIMARY KEY, AUTO_INCREMENT | Identifiant unique du rôle |
| nomRole | VARCHAR(80) | NOT NULL, UNIQUE | Nom du rôle (Admin, Gestionnaire, Employe) |
| descriptionRole | VARCHAR(255) | NULL | Description du rôle |

#### Table `droit`
Définit les permissions disponibles dans le système.

| Colonne | Type | Contraintes | Description |
|---------|------|-------------|-------------|
| idDroit | INT | PRIMARY KEY, AUTO_INCREMENT | Identifiant unique du droit |
| code | VARCHAR(64) | NOT NULL, UNIQUE | Code du droit (VIEW, CREATE, EDIT, DELETE, APPROVE) |
| specification | VARCHAR(255) | NULL | Description détaillée |

#### Table `role_droit`
Association entre rôles et droits (many-to-many).

| Colonne | Type | Contraintes | Description |
|---------|------|-------------|-------------|
| idRole | INT | PRIMARY KEY, FK -> role(idRole) | Référence au rôle |
| idDroit | INT | PRIMARY KEY, FK -> droit(idDroit) | Référence au droit |

**Contraintes :**
- ON DELETE CASCADE : Suppression automatique si le rôle ou droit est supprimé

#### Table `departement`
Départements de l'organisation.

| Colonne | Type | Contraintes | Description |
|---------|------|-------------|-------------|
| idDepartement | INT | PRIMARY KEY, AUTO_INCREMENT | Identifiant unique |
| nomDepartement | VARCHAR(120) | NOT NULL, UNIQUE | Nom du département |

#### Table `employe`
Employés/utilisateurs du système.

| Colonne | Type | Contraintes | Description |
|---------|------|-------------|-------------|
| idEmploye | INT | PRIMARY KEY, AUTO_INCREMENT | Identifiant unique |
| idDepartement | INT | NULL, FK -> departement | Département de rattachement |
| idRole | INT | NOT NULL, FK -> role | Rôle de l'employé |
| nomEmploye | VARCHAR(120) | NOT NULL | Nom de famille |
| prenomEmploye | VARCHAR(120) | NOT NULL | Prénom |
| motDePasse | VARCHAR(255) | NOT NULL | Hash du mot de passe |
| telephoneEmploye | VARCHAR(40) | NULL | Numéro de téléphone |
| courrielEmploye | VARCHAR(180) | NOT NULL, UNIQUE | Adresse email (login) |

**Contraintes :**
- `fk_emp_dep` : ON DELETE SET NULL (si département supprimé)
- `fk_emp_role` : ON DELETE RESTRICT (empêche suppression du rôle si utilisé)

**Index :**
- `idx_emp_dep` sur idDepartement
- `idx_emp_role` sur idRole

### 2. Gestion des équipes

#### Table `equipe`
Équipes de travail assignées aux projets.

| Colonne | Type | Contraintes | Description |
|---------|------|-------------|-------------|
| idEquipe | INT | PRIMARY KEY, AUTO_INCREMENT | Identifiant unique |
| nomEquipe | VARCHAR(120) | NOT NULL | Nom de l'équipe |
| idProjet | INT | NULL, FK -> projet | Projet associé (optionnel) |

**Contraintes :**
- `fk_equipe_projet` : ON DELETE SET NULL

#### Table `employe_equipe`
Association employés - équipes (many-to-many).

| Colonne | Type | Contraintes | Description |
|---------|------|-------------|-------------|
| idEmploye | INT | PRIMARY KEY, FK -> employe | Référence à l'employé |
| idEquipe | INT | PRIMARY KEY, FK -> equipe | Référence à l'équipe |

**Contraintes :**
- ON DELETE CASCADE pour les deux clés étrangères

#### Table `projet_employe`
Association employés - projets (members assignés).

| Colonne | Type | Contraintes | Description |
|---------|------|-------------|-------------|
| idProjet | INT | PRIMARY KEY, FK -> projet | Référence au projet |
| idEmploye | INT | PRIMARY KEY, FK -> employe | Référence à l'employé |

**Contraintes :**
- ON DELETE CASCADE pour les deux clés étrangères

### 3. Gestion des clients

#### Table `client`
Clients externes pour lesquels des projets sont réalisés.

| Colonne | Type | Contraintes | Description |
|---------|------|-------------|-------------|
| idClient | INT | PRIMARY KEY, AUTO_INCREMENT | Identifiant unique |
| nomClient | VARCHAR(160) | NOT NULL | Nom du client |
| telephoneClient | VARCHAR(40) | NULL | Téléphone |
| courrielClient | VARCHAR(180) | NULL | Email |
| statutClient | VARCHAR(60) | NULL | Statut (Actif, Inactif, etc.) |

### 4. Templates de projets et tâches

#### Table `template_projet`
Modèles de projets réutilisables.

| Colonne | Type | Contraintes | Description |
|---------|------|-------------|-------------|
| idTemplateProjet | INT | PRIMARY KEY, AUTO_INCREMENT | Identifiant unique |
| nomTemplate | VARCHAR(160) | NOT NULL | Nom du template |
| descriptionTemplate | TEXT | NULL | Description |
| heuresTemplate | DECIMAL(10,2) | DEFAULT 0.00 | Heures estimées |
| coutsTemplate | DECIMAL(12,2) | DEFAULT 0.00 | Coûts estimés |

#### Table `template_tache`
Modèles de tâches associés aux templates de projets.

| Colonne | Type | Contraintes | Description |
|---------|------|-------------|-------------|
| idTemplateTache | INT | PRIMARY KEY, AUTO_INCREMENT | Identifiant unique |
| idTemplateProjet | INT | NOT NULL, FK -> template_projet | Template parent |
| nomTemplateTache | VARCHAR(160) | NOT NULL | Nom de la tâche type |
| descriptionTemplateTache | TEXT | NULL | Description |
| heuresTemplateTache | DECIMAL(10,2) | DEFAULT 0.00 | Heures estimées |
| idParentTemplateTache | INT | NULL, FK -> template_tache | Tâche parent (hiérarchie) |

**Contraintes :**
- `fk_tt_tpl` : ON DELETE CASCADE
- `fk_tt_parent` : ON DELETE SET NULL

### 5. Gestion des projets

#### Table `projet`
Projets de l'organisation.

| Colonne | Type | Contraintes | Description |
|---------|------|-------------|-------------|
| idProjet | INT | PRIMARY KEY, AUTO_INCREMENT | Identifiant unique |
| nomProjet | VARCHAR(200) | NOT NULL | Nom du projet |
| dateDebut | DATE | NOT NULL | Date de début |
| dateFin | DATE | NULL | Date de fin prévue |
| heuresBudget | DECIMAL(10,2) | DEFAULT 0.00 | Budget en heures |
| coutsProjet | DECIMAL(12,2) | DEFAULT 0.00 | Coûts du projet |
| idClient | INT | NULL, FK -> client | Client associé |
| idEmploye | INT | NOT NULL, FK -> employe | Gestionnaire responsable |
| idTemplateProjet | INT | NULL, FK -> template_projet | Template utilisé |
| statutProjet | ENUM | DEFAULT 'À faire' | Statut : 'À faire', 'En cours', 'Terminé', 'En retard' |

**Contraintes :**
- `fk_proj_client` : ON DELETE SET NULL
- `fk_proj_resp` : ON DELETE RESTRICT
- `fk_proj_tpl` : ON DELETE SET NULL

**Index :**
- `idx_proj_resp` sur idEmploye

**Note :** Une colonne `progressionProjet` calculée automatiquement par l'application (non stockée en BDD)

### 6. Gestion des tâches

#### Table `etat`
États possibles pour les tâches (système legacy, peu utilisé actuellement).

| Colonne | Type | Contraintes | Description |
|---------|------|-------------|-------------|
| idEtat | INT | PRIMARY KEY, AUTO_INCREMENT | Identifiant unique |
| nomEtat | VARCHAR(60) | NOT NULL, UNIQUE | Nom de l'état |

#### Table `tache`
Tâches et sous-tâches des projets (structure hiérarchique).

| Colonne | Type | Contraintes | Description |
|---------|------|-------------|-------------|
| idTache | INT | PRIMARY KEY, AUTO_INCREMENT | Identifiant unique |
| idProjet | INT | FK -> projet | Projet parent |
| idTacheParent | INT | NULL, FK -> tache | Tâche parente (pour hiérarchie) |
| titreTache | VARCHAR(255) | NOT NULL | Titre de la tâche |
| descriptionTache | TEXT | NULL | Description détaillée |
| statutTache | ENUM | DEFAULT 'À faire' | 'À faire', 'En cours', 'En révision', 'Terminée' |
| prioriteTache | ENUM | DEFAULT 'Moyenne' | 'Basse', 'Moyenne', 'Haute' |
| dateDebut | DATE | NULL | Date de début |
| dateFin | DATE | NULL | Date de fin |
| heuresEstimees | DECIMAL(5,2) | DEFAULT 0 | Heures estimées |

**Contraintes :**
- `FK idProjet` : Référence au projet
- `FK idTacheParent` : ON DELETE CASCADE (suppression récursive)

**Index :**
- `idx_tache_proj` sur idProjet
- `idx_tache_parent` sur idTacheParent (si colonne renommée)

**Règles métier :**
- Hiérarchie illimitée (tâches, sous-tâches, sous-sous-tâches...)
- Progression calculée automatiquement de manière récursive
- Statut mis à jour automatiquement selon les sous-tâches

#### Table `affectation_tache`
Assignation des employés aux tâches (many-to-many).

| Colonne | Type | Contraintes | Description |
|---------|------|-------------|-------------|
| idEmploye | INT | PRIMARY KEY, FK -> employe | Employé assigné |
| idTache | INT | PRIMARY KEY, FK -> tache | Tâche assignée |
| tauxHoraire | DECIMAL(10,2) | NULL | Taux horaire spécifique |
| roleSurLaTache | VARCHAR(80) | NULL | Rôle (Responsable, Collaborateur, etc.) |

**Contraintes :**
- ON DELETE CASCADE pour les deux clés étrangères

**Index :**
- `idx_aff_tache` sur idTache

#### Table `dependance_tache`
Dépendances entre tâches (type MS Project).

| Colonne | Type | Contraintes | Description |
|---------|------|-------------|-------------|
| idPredecesseur | INT | PRIMARY KEY, FK -> tache | Tâche prédécesseur |
| idSuccesseur | INT | PRIMARY KEY, FK -> tache | Tâche successeur |
| typeDependance | ENUM | DEFAULT 'FS' | FS (Finish-Start), SS, FF, SF |

**Contraintes :**
- ON DELETE CASCADE pour les deux clés étrangères
- Trigger `bi_depen_no_self` : Empêche qu'une tâche dépende d'elle-même
- Trigger `bu_depen_no_self` : Idem pour UPDATE

### 7. Gestion du temps

#### Table `feuille_temps`
Feuilles de temps hebdomadaires pour validation.

| Colonne | Type | Contraintes | Description |
|---------|------|-------------|-------------|
| idFeuille | INT | PRIMARY KEY, AUTO_INCREMENT | Identifiant unique |
| idEmploye | INT | NOT NULL, FK -> employe | Propriétaire de la feuille |
| statut | ENUM | DEFAULT 'EN_COURS' | EN_COURS, SOUMISE, APPROUVEE, REJETEE |
| dateSoumission | DATETIME | NULL | Date de soumission |
| dateDecision | DATETIME | NULL | Date d'approbation/rejet |
| heures | DECIMAL(10,2) | DEFAULT 0.00 | Total des heures |
| idApprobateur | INT | NULL, FK -> employe | Gestionnaire approbateur |

**Contraintes :**
- `fk_ft_emp` : ON DELETE CASCADE
- `fk_ft_approb` : ON DELETE SET NULL

#### Table `saisie_temps`
Saisies individuelles de temps de travail.

| Colonne | Type | Contraintes | Description |
|---------|------|-------------|-------------|
| idSaisie | INT | PRIMARY KEY, AUTO_INCREMENT | Identifiant unique |
| idEmploye | INT | NOT NULL, FK -> employe | Qui a saisi |
| idTache | INT | NOT NULL, FK -> tache | Sur quelle tâche |
| dateTravail | DATE | NOT NULL | Date du travail |
| heures | DECIMAL(6,2) | NOT NULL, CHECK >= 0 | Nombre d'heures |
| commentaires | TEXT | NULL | Commentaires |

**Contraintes :**
- `fk_st_emp` : ON DELETE CASCADE
- `fk_st_tache` : ON DELETE RESTRICT (empêche suppression tâche avec heures saisies - contourné par code applicatif)

**Index :**
- `idx_st_emp_date` sur (idEmploye, dateTravail)
- `idx_st_tache` sur idTache

#### Table `ligne_feuille_temps`
Association entre feuilles de temps et saisies (many-to-many).

| Colonne | Type | Contraintes | Description |
|---------|------|-------------|-------------|
| idFeuille | INT | PRIMARY KEY, FK -> feuille_temps | Feuille de temps |
| idSaisie | INT | PRIMARY KEY, FK -> saisie_temps | Saisie de temps |

**Contraintes :**
- ON DELETE CASCADE pour les deux clés étrangères

## Relations principales

### Hiérarchie des projets
```
client (1) ----< (N) projet
employe (1) ----< (N) projet (responsable)
template_projet (1) ----< (N) projet
projet (1) ----< (N) tache
```

### Hiérarchie des tâches (récursive)
```
tache (1) ----< (N) tache (idTacheParent)
Profondeur illimitée : tâche > sous-tâche > sous-sous-tâche...
```

### Assignations
```
projet (N) ----< >---- (N) employe (via projet_employe)
tache (N) ----< >---- (N) employe (via affectation_tache)
equipe (N) ----< >---- (N) employe (via employe_equipe)
```

### Temps de travail
```
employe (1) ----< (N) saisie_temps
tache (1) ----< (N) saisie_temps
feuille_temps (N) ----< >---- (N) saisie_temps (via ligne_feuille_temps)
```

## Règles métier importantes

### Calcul de progression
La progression est calculée de manière **récursive et pondérée** :
- Formule : `Σ(progression × heures) / Σ(heures)`
- Prend en compte toutes les sous-tâches (tous niveaux)
- Utilise le maximum entre progression par heures et progression par statut

### Mise à jour automatique des statuts
- **Tâches** : Statut mis à jour récursivement vers la tâche parente
- **Projets** : Statut mis à jour selon l'état de toutes les tâches
- **Détection automatique "En retard"** : Si dateFin < aujourd'hui et statut != Terminé

### Validation des dates
- dateDebut <= dateFin pour les tâches et projets
- Dates des sous-tâches doivent être dans l'intervalle de la tâche parent
- Dates des tâches doivent être dans l'intervalle du projet

### Suppression en cascade
- Suppression d'un projet : supprime toutes les tâches et données associées
- Suppression d'une tâche : supprime récursivement toutes les sous-tâches
- Suppression automatique : affectations, dépendances, saisies de temps

## Vue utile

### v_temps_par_tache
Vue SQL pour agréger les temps par tâche.

```sql
SELECT
  t.idTache,
  t.nomTache,
  t.idProjet,
  SUM(st.heures) AS total_heures,
  GROUP_CONCAT(st.commentaires SEPARATOR '; ') AS commentaires
FROM tache t
LEFT JOIN saisie_temps st ON t.idTache = st.idTache
GROUP BY t.idTache, t.nomTache, t.idProjet
```

## Configuration

Encodage : `utf8mb4`  
Collation : `utf8mb4_0900_ai_ci`  
Moteur : `InnoDB` (toutes les tables)
