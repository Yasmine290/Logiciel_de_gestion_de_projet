-- ======================================================================
-- Base de données Projet & Gestion de temps 
-- ======================================================================

CREATE DATABASE IF NOT EXISTS project_time_gestion
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_0900_ai_ci;
USE project_time_gestion;

-- --------------------------------------------------
-- Référentiels Rôles & Droits
-- --------------------------------------------------
CREATE TABLE role (
  idRole           INT AUTO_INCREMENT PRIMARY KEY,
  nomRole          VARCHAR(80)  NOT NULL UNIQUE,
  descriptionRole  VARCHAR(255) NULL
) ENGINE=InnoDB;

CREATE TABLE droit (
  idDroit          INT AUTO_INCREMENT PRIMARY KEY,
  code             VARCHAR(64)  NOT NULL UNIQUE,   -- ex: VIEW, CREATE, EDIT, DELETE, APPROVE
  specification    VARCHAR(255) NULL
) ENGINE=InnoDB;

CREATE TABLE role_droit (
  idRole  INT NOT NULL,
  idDroit INT NOT NULL,
  PRIMARY KEY (idRole, idDroit),
  CONSTRAINT fk_roledroit_role  FOREIGN KEY (idRole)  REFERENCES role(idRole)   ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_roledroit_droit FOREIGN KEY (idDroit) REFERENCES droit(idDroit) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- --------------------------------------------------
-- Organisation & Utilisateurs
-- --------------------------------------------------
CREATE TABLE departement (
  idDepartement   INT AUTO_INCREMENT PRIMARY KEY,
  nomDepartement  VARCHAR(120) NOT NULL UNIQUE
) ENGINE=InnoDB;

CREATE TABLE employe (
  idEmploye        INT AUTO_INCREMENT PRIMARY KEY,
  idDepartement    INT NULL,
  idRole           INT NOT NULL,
  nomEmploye       VARCHAR(120) NOT NULL,
  prenomEmploye    VARCHAR(120) NOT NULL,
  motDePasse       VARCHAR(255) NOT NULL,
  telephoneEmploye VARCHAR(40)  NULL,
  courrielEmploye  VARCHAR(180) NOT NULL UNIQUE,
  CONSTRAINT fk_emp_dep  FOREIGN KEY (idDepartement) REFERENCES departement(idDepartement) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT fk_emp_role FOREIGN KEY (idRole)        REFERENCES role(idRole)              ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE equipe (
  idEquipe   INT AUTO_INCREMENT PRIMARY KEY,
  nomEquipe  VARCHAR(120) NOT NULL,
  idProjet   INT NULL      -- équipe optionnellement rattachée à un projet
) ENGINE=InnoDB;

CREATE TABLE employe_equipe (
  idEmploye INT NOT NULL,
  idEquipe  INT NOT NULL,
  PRIMARY KEY (idEmploye, idEquipe),
  CONSTRAINT fk_ee_emp   FOREIGN KEY (idEmploye) REFERENCES employe(idEmploye) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_ee_equip FOREIGN KEY (idEquipe)  REFERENCES equipe(idEquipe)   ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- --------------------------------------------------
-- Clients
-- --------------------------------------------------
CREATE TABLE client (
  idClient        INT AUTO_INCREMENT PRIMARY KEY,
  nomClient       VARCHAR(160) NOT NULL,
  telephoneClient VARCHAR(40)  NULL,
  courrielClient  VARCHAR(180) NULL,
  statutClient    VARCHAR(60)  NULL
) ENGINE=InnoDB;

-- --------------------------------------------------
-- Templates de projets & de tâches
-- --------------------------------------------------
CREATE TABLE template_projet (
  idTemplateProjet  INT AUTO_INCREMENT PRIMARY KEY,
  nomTemplate       VARCHAR(160) NOT NULL,
  descriptionTemplate TEXT NULL,
  heuresTemplate    DECIMAL(10,2) DEFAULT 0.00,
  coutsTemplate     DECIMAL(12,2) DEFAULT 0.00
) ENGINE=InnoDB;

CREATE TABLE template_tache (
  idTemplateTache      INT AUTO_INCREMENT PRIMARY KEY,
  idTemplateProjet     INT NOT NULL,
  nomTemplateTache     VARCHAR(160) NOT NULL,
  descriptionTemplateTache TEXT NULL,
  heuresTemplateTache  DECIMAL(10,2) DEFAULT 0.00,
  idParentTemplateTache INT NULL,
  CONSTRAINT fk_tt_tpl        FOREIGN KEY (idTemplateProjet)     REFERENCES template_projet(idTemplateProjet) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_tt_parent     FOREIGN KEY (idParentTemplateTache) REFERENCES template_tache(idTemplateTache)  ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB;

-- --------------------------------------------------
-- Projets
-- --------------------------------------------------
CREATE TABLE projet (
  idProjet      INT AUTO_INCREMENT PRIMARY KEY,
  nomProjet     VARCHAR(200) NOT NULL,
  dateDebut     DATE NOT NULL,
  dateFin       DATE NULL,
  heuresBudget  DECIMAL(10,2) DEFAULT 0.00,
  coutsProjet   DECIMAL(12,2) DEFAULT 0.00,
  idClient      INT NULL,
  idEmploye     INT NOT NULL,            -- gestionnaire / responsable
  idTemplateProjet INT NULL,
  CONSTRAINT fk_proj_client  FOREIGN KEY (idClient)         REFERENCES client(idClient)             ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT fk_proj_resp    FOREIGN KEY (idEmploye)        REFERENCES employe(idEmploye)          ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT fk_proj_tpl     FOREIGN KEY (idTemplateProjet) REFERENCES template_projet(idTemplateProjet) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB;

-- rattachement optionnel d'une équipe à un projet (clé étrangère posée après création de projet)
ALTER TABLE equipe
  ADD CONSTRAINT fk_equipe_projet FOREIGN KEY (idProjet) REFERENCES projet(idProjet) ON DELETE SET NULL ON UPDATE CASCADE;

-- --------------------------------------------------
-- États & Tâches (hiérarchie)
-- --------------------------------------------------
CREATE TABLE etat (
  idEtat   INT AUTO_INCREMENT PRIMARY KEY,
  nomEtat  VARCHAR(60) NOT NULL UNIQUE  -- ex: 'EN_COURS','EN_ATTENTE','TERMINEE','EN_PROBLEME'
) ENGINE=InnoDB;

CREATE TABLE tache (
  idTache          INT AUTO_INCREMENT PRIMARY KEY,
  idProjet         INT NOT NULL,
  nomTache         VARCHAR(200) NOT NULL,
  descriptionTache TEXT NULL,
  dateDebutTache   DATE NULL,
  dateFinTache     DATE NULL,
  heuresAllouees   DECIMAL(10,2) DEFAULT 0.00,
  idEtat           INT NOT NULL,
  idParentTache    INT NULL,                 -- pour sous-tâches (arbre)
  CONSTRAINT fk_tache_projet FOREIGN KEY (idProjet)      REFERENCES projet(idProjet) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_tache_etat   FOREIGN KEY (idEtat)        REFERENCES etat(idEtat)     ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT fk_tache_parent FOREIGN KEY (idParentTache) REFERENCES tache(idTache)   ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB;

-- Affectations (M:N) des employés sur les tâches
CREATE TABLE affectation_tache (
  idEmploye       INT NOT NULL,
  idTache         INT NOT NULL,
  tauxHoraire     DECIMAL(10,2) NULL,
  roleSurLaTache  VARCHAR(80)   NULL, -- ex: 'Responsable', 'Collaborateur'
  PRIMARY KEY (idEmploye, idTache),
  CONSTRAINT fk_aff_emp   FOREIGN KEY (idEmploye) REFERENCES employe(idEmploye) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_aff_tache FOREIGN KEY (idTache)   REFERENCES tache(idTache)     ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- Dépendances entre tâches (prédécesseur → successeur)
CREATE TABLE dependance_tache (
  idPredecesseur  INT NOT NULL,
  idSuccesseur    INT NOT NULL,
  typeDependance  ENUM('FS','SS','FF','SF') NOT NULL DEFAULT 'FS',
  PRIMARY KEY (idPredecesseur, idSuccesseur),
  CONSTRAINT fk_dep_pred FOREIGN KEY (idPredecesseur)
    REFERENCES tache(idTache) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_dep_succ FOREIGN KEY (idSuccesseur)
    REFERENCES tache(idTache) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

DELIMITER $$
CREATE TRIGGER bi_depen_no_self
BEFORE INSERT ON dependance_tache
FOR EACH ROW
BEGIN
  IF NEW.idPredecesseur = NEW.idSuccesseur THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Une tâche ne peut pas dépendre d’elle-même.';
  END IF;
END$$

CREATE TRIGGER bu_depen_no_self
BEFORE UPDATE ON dependance_tache
FOR EACH ROW
BEGIN
  IF NEW.idPredecesseur = NEW.idSuccesseur THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Une tâche ne peut pas dépendre d’elle-même.';
  END IF;
END$$
DELIMITER ;

-- --------------------------------------------------
-- Saisie & Validation des temps
-- --------------------------------------------------
CREATE TABLE feuille_temps (
  idFeuille       INT AUTO_INCREMENT PRIMARY KEY,
  idEmploye       INT NOT NULL,                 -- propriétaire de la feuille
  statut          ENUM('EN_COURS','SOUMISE','APPROUVEE','REJETEE') DEFAULT 'EN_COURS',
  dateSoumission  DATETIME NULL,
  dateDecision    DATETIME NULL,
  heures          DECIMAL(10,2) DEFAULT 0.00,   -- total agrégé (optionnel)
  idApprobateur   INT NULL,                     -- gestionnaire qui approuve
  CONSTRAINT fk_ft_emp    FOREIGN KEY (idEmploye)     REFERENCES employe(idEmploye) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_ft_approb FOREIGN KEY (idApprobateur) REFERENCES employe(idEmploye) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE saisie_temps (
  idSaisie     INT AUTO_INCREMENT PRIMARY KEY,
  idEmploye    INT NOT NULL,          -- qui a saisi
  idTache      INT NOT NULL,          -- sur quelle tâche
  dateTravail  DATE NOT NULL,
  heures       DECIMAL(6,2) NOT NULL CHECK (heures >= 0),
  commentaires TEXT NULL,
  CONSTRAINT fk_st_emp   FOREIGN KEY (idEmploye) REFERENCES employe(idEmploye) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_st_tache FOREIGN KEY (idTache)   REFERENCES tache(idTache)     ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;

-- Association N:N entre feuilles et saisies (une feuille regroupe plusieurs saisies d’une semaine)
CREATE TABLE ligne_feuille_temps (
  idFeuille INT NOT NULL,
  idSaisie  INT NOT NULL,
  PRIMARY KEY (idFeuille, idSaisie),
  CONSTRAINT fk_lft_feuille FOREIGN KEY (idFeuille) REFERENCES feuille_temps(idFeuille) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_lft_saisie  FOREIGN KEY (idSaisie)  REFERENCES saisie_temps(idSaisie)   ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- --------------------------------------------------
-- Index utiles
-- --------------------------------------------------
CREATE INDEX idx_emp_dep   ON employe(idDepartement);
CREATE INDEX idx_emp_role  ON employe(idRole);
CREATE INDEX idx_proj_resp ON projet(idEmploye);
CREATE INDEX idx_tache_proj ON tache(idProjet);
CREATE INDEX idx_tache_parent ON tache(idParentTache);
CREATE INDEX idx_st_emp_date ON saisie_temps(idEmploye, dateTravail);
CREATE INDEX idx_st_tache ON saisie_temps(idTache);
CREATE INDEX idx_aff_tache ON affectation_tache(idTache);



-- ==================  DONNÉES DE TEST ==================
USE project_time_gestion;

-- Rôles & droits
INSERT INTO role (nomRole, descriptionRole) VALUES
('Admin','Administration globale'),
('Gestionnaire','Gère projets & approbations'),
('Employe','Saisie des temps');

INSERT INTO droit (code, specification) VALUES
('VIEW','Consulter'),
('CREATE','Créer'),
('EDIT','Modifier'),
('DELETE','Supprimer'),
('APPROVE','Approuver');

-- Donner tous les droits à Admin, lecture+création+édition à Gestionnaire, lecture + création (saisie) à Employé
INSERT INTO role_droit
SELECT r.idRole, d.idDroit FROM role r JOIN droit d
WHERE r.nomRole='Admin'
UNION ALL
SELECT r.idRole, d.idDroit FROM role r JOIN droit d
WHERE r.nomRole='Gestionnaire' AND d.code IN ('VIEW','CREATE','EDIT','APPROVE')
UNION ALL
SELECT r.idRole, d.idDroit FROM role r JOIN droit d
WHERE r.nomRole='Employe' AND d.code IN ('VIEW','CREATE');

-- Départements
INSERT INTO departement (nomDepartement) VALUES ('Informatique'),('Comptabilité');

-- Employés (MOT DE PASSE A CHANGER en prod)
INSERT INTO employe (idDepartement, idRole, nomEmploye, prenomEmploye, motDePasse, telephoneEmploye, courrielEmploye) VALUES
(1, 1, 'Admin', 'Alpha',  '$2y$10$hashFake', '000-000-0000', 'alpha.admin@exemple.com'),
(1, 2, 'Gestion', 'Beta', '$2y$10$hashFake', '000-000-0001', 'beta.gestion@exemple.com'),
(1, 3, 'Employe', 'Gamma','$2y$10$hashFake', '000-000-0002', 'gamma.employe@exemple.com');

-- États
INSERT INTO etat (nomEtat) VALUES ('EN_ATTENTE'),('EN_COURS'),('TERMINEE'),('EN_PROBLEME');

-- Client
INSERT INTO client (nomClient, telephoneClient, courrielClient, statutClient)
VALUES ('Client Démo', '418-000-0000', 'contact@clientdemo.ca', 'Actif');

-- Template 
INSERT INTO template_projet (nomTemplate, descriptionTemplate, heuresTemplate, coutsTemplate)
VALUES ('Template Agile', 'Backlog + Sprint + Revue', 120, 0);

-- Projet (responsable = idEmploye 2 = Gestionnaire)
INSERT INTO projet (nomProjet, dateDebut, dateFin, heuresBudget, coutsProjet, idClient, idEmploye, idTemplateProjet)
VALUES ('Projet Démo GT&P', CURDATE(), DATE_ADD(CURDATE(), INTERVAL 60 DAY), 200, 0, 1, 2, 1);

-- Tâches (idProjet = 1)
INSERT INTO tache (idProjet, nomTache, descriptionTache, dateDebutTache, dateFinTache, heuresAllouees, idEtat, idParentTache)
VALUES
(1, 'Analyse', 'Recueil des besoins', CURDATE(), DATE_ADD(CURDATE(), INTERVAL 7 DAY), 40, (SELECT idEtat FROM etat WHERE nomEtat='EN_COURS'), NULL),
(1, 'Développement', 'Implémentation', DATE_ADD(CURDATE(), INTERVAL 7 DAY), DATE_ADD(CURDATE(), INTERVAL 40 DAY), 120, (SELECT idEtat FROM etat WHERE nomEtat='EN_ATTENTE'), NULL),
(1, 'Tests', 'Validation & QA', DATE_ADD(CURDATE(), INTERVAL 40 DAY), DATE_ADD(CURDATE(), INTERVAL 55 DAY), 40, (SELECT idEtat FROM etat WHERE nomEtat='EN_ATTENTE'), NULL);

-- Dépendances : Analyse -> Développement -> Tests
INSERT INTO dependance_tache (idPredecesseur, idSuccesseur, typeDependance)
VALUES
((SELECT MIN(idTache) FROM tache WHERE idProjet=1 AND nomTache='Analyse'),
 (SELECT MIN(idTache) FROM tache WHERE idProjet=1 AND nomTache='Développement'), 'FS'),
((SELECT MIN(idTache) FROM tache WHERE idProjet=1 AND nomTache='Développement'),
 (SELECT MIN(idTache) FROM tache WHERE idProjet=1 AND nomTache='Tests'), 'FS');

-- Affectations (Gamma sur Dév & Tests ; Gestionnaire sur Analyse)
INSERT INTO affectation_tache (idEmploye, idTache, tauxHoraire, roleSurLaTache)
VALUES
(2, (SELECT idTache FROM tache WHERE nomTache='Analyse' AND idProjet=1 LIMIT 1), 75, 'Responsable'),
(3, (SELECT idTache FROM tache WHERE nomTache='Développement' AND idProjet=1 LIMIT 1), 55, 'Développeur'),
(3, (SELECT idTache FROM tache WHERE nomTache='Tests' AND idProjet=1 LIMIT 1), 55, 'QA');

-- Feuille de temps + saisies
INSERT INTO feuille_temps (idEmploye, statut) VALUES (3,'EN_COURS'); -- feuille Gamma
INSERT INTO saisie_temps (idEmploye, idTache, dateTravail, heures, commentaires)
VALUES
(3, (SELECT idTache FROM tache WHERE nomTache='Développement' AND idProjet=1 LIMIT 1), CURDATE(), 3.5, 'Setup projet'),
(3, (SELECT idTache FROM tache WHERE nomTache='Développement' AND idProjet=1 LIMIT 1), DATE_ADD(CURDATE(), INTERVAL 1 DAY), 6.0, 'Endpoints API');

-- Lier la feuille aux saisies
INSERT INTO ligne_feuille_temps (idFeuille, idSaisie)
SELECT (SELECT MAX(idFeuille) FROM feuille_temps), s.idSaisie
FROM saisie_temps s
WHERE s.idEmploye=3
ORDER BY s.idSaisie DESC
LIMIT 2;

-- Vérifs rapides
SELECT DATABASE() AS db;
SELECT * FROM projet;
SELECT idTache, nomTache FROM tache WHERE idProjet=1;
SELECT * FROM v_temps_par_tache WHERE idProjet=1;


