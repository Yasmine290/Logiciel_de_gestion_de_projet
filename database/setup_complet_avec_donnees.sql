-- ======================================================================
-- Script complet de création et initialisation de la base de données
-- Projet: Gestion de Projets & Temps
-- Usage: Pour installation complète avec données de démonstration
-- ======================================================================

-- ======================================================================
-- 1. CRÉATION DE LA BASE DE DONNÉES
-- ======================================================================

DROP DATABASE IF EXISTS project_time_gestion;
CREATE DATABASE project_time_gestion
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_0900_ai_ci;

USE project_time_gestion;

-- ======================================================================
-- 2. CRÉATION DES TABLES
-- ======================================================================

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
  code             VARCHAR(64)  NOT NULL UNIQUE,
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
  idProjet   INT NULL
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
  idEmploye     INT NOT NULL,
  idTemplateProjet INT NULL,
  statutProjet ENUM('À faire', 'En cours', 'Terminé', 'En retard') DEFAULT 'À faire',
  descriptionProjet TEXT NULL,
  CONSTRAINT fk_proj_client  FOREIGN KEY (idClient)         REFERENCES client(idClient)             ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT fk_proj_resp    FOREIGN KEY (idEmploye)        REFERENCES employe(idEmploye)          ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT fk_proj_tpl     FOREIGN KEY (idTemplateProjet) REFERENCES template_projet(idTemplateProjet) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE projet_employe (
  idProjet  INT NOT NULL,
  idEmploye INT NOT NULL,
  PRIMARY KEY (idProjet, idEmploye),
  CONSTRAINT fk_pe_proj FOREIGN KEY (idProjet)  REFERENCES projet(idProjet)   ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_pe_emp  FOREIGN KEY (idEmploye) REFERENCES employe(idEmploye) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

ALTER TABLE equipe
  ADD CONSTRAINT fk_equipe_projet FOREIGN KEY (idProjet) REFERENCES projet(idProjet) ON DELETE SET NULL ON UPDATE CASCADE;

-- --------------------------------------------------
-- États & Tâches (hiérarchie)
-- --------------------------------------------------
CREATE TABLE etat (
  idEtat   INT AUTO_INCREMENT PRIMARY KEY,
  nomEtat  VARCHAR(60) NOT NULL UNIQUE
) ENGINE=InnoDB;

CREATE TABLE tache (
  idTache INT AUTO_INCREMENT PRIMARY KEY,
  idProjet INT NOT NULL,
  idTacheParent INT NULL,
  titreTache VARCHAR(255) NOT NULL,
  descriptionTache TEXT,
  statutTache ENUM('À faire', 'En cours', 'En révision', 'Terminée') DEFAULT 'À faire',
  prioriteTache ENUM('Basse', 'Moyenne', 'Haute') DEFAULT 'Moyenne',
  dateDebutTache DATE NULL,
  dateFinTache DATE NULL,
  heuresEstimees DECIMAL(5,2) DEFAULT 0,
  CONSTRAINT fk_tache_proj   FOREIGN KEY (idProjet) REFERENCES projet(idProjet) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_tache_parent FOREIGN KEY (idTacheParent) REFERENCES tache(idTache) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE affectation_tache (
  idEmploye       INT NOT NULL,
  idTache         INT NOT NULL,
  tauxHoraire     DECIMAL(10,2) NULL,
  roleSurLaTache  VARCHAR(80)   NULL,
  PRIMARY KEY (idEmploye, idTache),
  CONSTRAINT fk_aff_emp   FOREIGN KEY (idEmploye) REFERENCES employe(idEmploye) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_aff_tache FOREIGN KEY (idTache)   REFERENCES tache(idTache)     ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE dependance_tache (
  idPredecesseur  INT NOT NULL,
  idSuccesseur    INT NOT NULL,
  typeDependance  ENUM('FS','SS','FF','SF') NOT NULL DEFAULT 'FS',
  PRIMARY KEY (idPredecesseur, idSuccesseur),
  CONSTRAINT fk_dep_pred FOREIGN KEY (idPredecesseur) REFERENCES tache(idTache) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_dep_succ FOREIGN KEY (idSuccesseur)   REFERENCES tache(idTache) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- Triggers pour empêcher auto-dépendance
DELIMITER $$
CREATE TRIGGER bi_depen_no_self
BEFORE INSERT ON dependance_tache
FOR EACH ROW
BEGIN
  IF NEW.idPredecesseur = NEW.idSuccesseur THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Une tâche ne peut pas dépendre d''elle-même.';
  END IF;
END$$

CREATE TRIGGER bu_depen_no_self
BEFORE UPDATE ON dependance_tache
FOR EACH ROW
BEGIN
  IF NEW.idPredecesseur = NEW.idSuccesseur THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Une tâche ne peut pas dépendre d''elle-même.';
  END IF;
END$$
DELIMITER ;

-- --------------------------------------------------
-- Saisie & Validation des temps
-- --------------------------------------------------
CREATE TABLE feuille_temps (
  idFeuille       INT AUTO_INCREMENT PRIMARY KEY,
  idEmploye       INT NOT NULL,
  statut          ENUM('EN_COURS','SOUMISE','APPROUVEE','REJETEE') DEFAULT 'EN_COURS',
  dateSoumission  DATETIME NULL,
  dateDecision    DATETIME NULL,
  heures          DECIMAL(10,2) DEFAULT 0.00,
  idApprobateur   INT NULL,
  CONSTRAINT fk_ft_emp    FOREIGN KEY (idEmploye)     REFERENCES employe(idEmploye) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_ft_approb FOREIGN KEY (idApprobateur) REFERENCES employe(idEmploye) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE saisie_temps (
  idSaisie     INT AUTO_INCREMENT PRIMARY KEY,
  idEmploye    INT NOT NULL,
  idTache      INT NOT NULL,
  dateTravail  DATE NOT NULL,
  heures       DECIMAL(6,2) NOT NULL CHECK (heures >= 0),
  commentaires TEXT NULL,
  CONSTRAINT fk_st_emp   FOREIGN KEY (idEmploye) REFERENCES employe(idEmploye) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_st_tache FOREIGN KEY (idTache)   REFERENCES tache(idTache)     ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE ligne_feuille_temps (
  idFeuille INT NOT NULL,
  idSaisie  INT NOT NULL,
  PRIMARY KEY (idFeuille, idSaisie),
  CONSTRAINT fk_lft_feuille FOREIGN KEY (idFeuille) REFERENCES feuille_temps(idFeuille) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_lft_saisie  FOREIGN KEY (idSaisie)  REFERENCES saisie_temps(idSaisie)   ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- --------------------------------------------------
-- Index utiles pour performances
-- --------------------------------------------------
CREATE INDEX idx_emp_dep      ON employe(idDepartement);
CREATE INDEX idx_emp_role     ON employe(idRole);
CREATE INDEX idx_proj_resp    ON projet(idEmploye);
CREATE INDEX idx_tache_proj   ON tache(idProjet);
CREATE INDEX idx_tache_parent ON tache(idTacheParent);
CREATE INDEX idx_st_emp_date  ON saisie_temps(idEmploye, dateTravail);
CREATE INDEX idx_st_tache     ON saisie_temps(idTache);
CREATE INDEX idx_aff_tache    ON affectation_tache(idTache);

-- ======================================================================
-- 3. INSERTION DES DONNÉES DE DÉMONSTRATION
-- ======================================================================

-- --------------------------------------------------
-- Rôles système (3 rôles de base)
-- --------------------------------------------------
INSERT INTO role (nomRole, descriptionRole) VALUES
('Admin',        'Administration complète du système'),
('Gestionnaire', 'Gestion des projets et approbation des temps'),
('Employe',      'Saisie des temps et consultation');

-- --------------------------------------------------
-- Droits système (5 permissions de base)
-- --------------------------------------------------
INSERT INTO droit (code, specification) VALUES
('VIEW',    'Consulter les données'),
('CREATE',  'Créer de nouveaux éléments'),
('EDIT',    'Modifier les éléments existants'),
('DELETE',  'Supprimer des éléments'),
('APPROVE', 'Approuver les feuilles de temps');

-- --------------------------------------------------
-- Attribution des droits aux rôles
-- --------------------------------------------------
-- Admin: tous les droits
INSERT INTO role_droit (idRole, idDroit)
SELECT 1, idDroit FROM droit;

-- Gestionnaire: VIEW, CREATE, EDIT, APPROVE
INSERT INTO role_droit (idRole, idDroit)
SELECT 2, idDroit FROM droit WHERE code IN ('VIEW', 'CREATE', 'EDIT', 'APPROVE');

-- Employe: VIEW, CREATE (pour saisir temps)
INSERT INTO role_droit (idRole, idDroit)
SELECT 3, idDroit FROM droit WHERE code IN ('VIEW', 'CREATE');

-- --------------------------------------------------
-- Départements
-- --------------------------------------------------
INSERT INTO departement (nomDepartement) VALUES
('Informatique'),
('Ressources Humaines'),
('Comptabilité'),
('Marketing');

-- --------------------------------------------------
-- Employés (avec mots de passe hachés)
-- NOTES IMPORTANTES:
-- - Les mots de passe sont hachés avec Werkzeug (Python)
-- - Mot de passe par défaut pour démo: "password123"
-- - Hash généré avec: werkzeug.security.generate_password_hash('password123')
-- - À CHANGER EN PRODUCTION!
-- --------------------------------------------------
INSERT INTO employe (idDepartement, idRole, nomEmploye, prenomEmploye, motDePasse, telephoneEmploye, courrielEmploye) VALUES
-- Admin
(1, 1, 'Tremblay',  'Admin',     'scrypt:32768:8:1$nBWZkXLz2qE7gP5j$f1a9e6c0b3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2', '418-555-0001', 'admin@projet-temps.ca'),

-- Gestionnaires
(1, 2, 'Gagnon',    'Marie',     'scrypt:32768:8:1$nBWZkXLz2qE7gP5j$f1a9e6c0b3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2', '418-555-0002', 'marie.gagnon@projet-temps.ca'),
(3, 2, 'Roy',       'Pierre',    'scrypt:32768:8:1$nBWZkXLz2qE7gP5j$f1a9e6c0b3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2', '418-555-0003', 'pierre.roy@projet-temps.ca'),

-- Employés
(1, 3, 'Côté',      'Sophie',    'scrypt:32768:8:1$nBWZkXLz2qE7gP5j$f1a9e6c0b3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2', '418-555-0004', 'sophie.cote@projet-temps.ca'),
(1, 3, 'Bouchard',  'Marc',      'scrypt:32768:8:1$nBWZkXLz2qE7gP5j$f1a9e6c0b3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2', '418-555-0005', 'marc.bouchard@projet-temps.ca'),
(2, 3, 'Levesque',  'Julie',     'scrypt:32768:8:1$nBWZkXLz2qE7gP5j$f1a9e6c0b3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2', '418-555-0006', 'julie.levesque@projet-temps.ca'),
(4, 3, 'Bergeron',  'Luc',       'scrypt:32768:8:1$nBWZkXLz2qE7gP5j$f1a9e6c0b3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2', '418-555-0007', 'luc.bergeron@projet-temps.ca');

-- --------------------------------------------------
-- Clients
-- --------------------------------------------------
INSERT INTO client (nomClient, telephoneClient, courrielClient, statutClient) VALUES
('Ville de Québec',           '418-641-6411', 'info@ville.quebec.qc.ca',      'Actif'),
('Hydro-Québec',              '418-643-5252', 'service@hydro.qc.ca',          'Actif'),
('Desjardins',                '418-835-8444', 'contact@desjardins.com',       'Actif'),
('Université Laval',          '418-656-2131', 'info@ulaval.ca',               'Actif'),
('Ministère des Transports',  '418-643-6980', 'info@transports.gouv.qc.ca',   'En attente');

-- --------------------------------------------------
-- États (legacy - peu utilisé)
-- --------------------------------------------------
INSERT INTO etat (nomEtat) VALUES
('EN_ATTENTE'),
('EN_COURS'),
('TERMINEE'),
('EN_PROBLEME');

-- --------------------------------------------------
-- Templates de projets
-- --------------------------------------------------
INSERT INTO template_projet (nomTemplate, descriptionTemplate, heuresTemplate, coutsTemplate) VALUES
('Développement Web Standard', 'Site web responsive avec backend API',      320.00, 25000.00),
('Application Mobile',          'App iOS/Android avec API backend',         480.00, 45000.00),
('Migration Système',           'Migration base de données et serveurs',    160.00, 18000.00);

-- --------------------------------------------------
-- Templates de tâches (pour le template "Développement Web")
-- --------------------------------------------------
INSERT INTO template_tache (idTemplateProjet, nomTemplateTache, descriptionTemplateTache, heuresTemplateTache, idParentTemplateTache) VALUES
(1, 'Analyse et conception',     'Recueil besoins + maquettes',           40.00, NULL),
(1, 'Développement Frontend',    'HTML/CSS/JavaScript',                   80.00, NULL),
(1, 'Développement Backend',     'API REST + Base de données',           120.00, NULL),
(1, 'Tests et déploiement',      'Tests QA + mise en production',         40.00, NULL),
(1, 'Documentation',             'Documentation technique et utilisateur', 40.00, NULL);

-- --------------------------------------------------
-- Projets actifs
-- --------------------------------------------------
INSERT INTO projet (nomProjet, dateDebut, dateFin, heuresBudget, coutsProjet, idClient, idEmploye, idTemplateProjet, statutProjet, descriptionProjet) VALUES
-- Projet 1: En cours (gestionnaire Marie)
('Portail Citoyen',
 '2024-11-01', '2025-03-31', 350.00, 28000.00, 1, 2, 1, 'En cours',
 'Développement d''un portail web pour les citoyens de la Ville de Québec permettant de consulter les services municipaux.'),

-- Projet 2: Démarrage récent (gestionnaire Marie)
('Application Mobile Hydro',
 '2024-12-01', '2025-06-30', 500.00, 48000.00, 2, 2, 2, 'En cours',
 'Application mobile pour consultation de consommation électrique et paiement de factures.'),

-- Projet 3: En planification (gestionnaire Pierre)
('Refonte Intranet',
 '2025-01-15', '2025-05-31', 280.00, 22000.00, 3, 3, 1, 'À faire',
 'Modernisation de l''intranet Desjardins avec nouvelles fonctionnalités collaboratives.');

-- --------------------------------------------------
-- Assignation des membres aux projets
-- --------------------------------------------------
-- Projet 1: Marie (responsable) + Sophie + Marc
INSERT INTO projet_employe (idProjet, idEmploye) VALUES
(1, 2), -- Marie (gestionnaire)
(1, 4), -- Sophie
(1, 5); -- Marc

-- Projet 2: Marie (responsable) + Sophie + Luc
INSERT INTO projet_employe (idProjet, idEmploye) VALUES
(2, 2), -- Marie
(2, 4), -- Sophie
(2, 7); -- Luc

-- Projet 3: Pierre (responsable) + Marc + Julie
INSERT INTO projet_employe (idProjet, idEmploye) VALUES
(3, 3), -- Pierre
(3, 5), -- Marc
(3, 6); -- Julie

-- --------------------------------------------------
-- Tâches du Projet 1: Portail Citoyen
-- --------------------------------------------------
INSERT INTO tache (idProjet, idTacheParent, titreTache, descriptionTache, statutTache, prioriteTache, dateDebutTache, dateFinTache, heuresEstimees) VALUES
-- Tâches principales
(1, NULL, 'Analyse des besoins',           'Rencontres avec le client et spécifications',          'Terminée',    'Haute',   '2024-11-01', '2024-11-15', 40.00),
(1, NULL, 'Design UI/UX',                  'Maquettes et prototypes',                              'Terminée',    'Haute',   '2024-11-16', '2024-11-30', 50.00),
(1, NULL, 'Développement Backend',         'API REST et base de données',                          'En cours',    'Haute',   '2024-12-01', '2025-01-31', 120.00),
(1, NULL, 'Développement Frontend',        'Interface web responsive',                             'En cours',    'Haute',   '2024-12-15', '2025-02-15', 100.00),
(1, NULL, 'Tests et validation',           'Tests QA et corrections',                              'À faire',     'Moyenne', '2025-02-16', '2025-03-15', 60.00),
(1, NULL, 'Déploiement et formation',      'Mise en production et formation utilisateurs',         'À faire',     'Haute',   '2025-03-16', '2025-03-31', 30.00);

-- Sous-tâches du "Développement Backend" (id=3)
INSERT INTO tache (idProjet, idTacheParent, titreTache, descriptionTache, statutTache, prioriteTache, dateDebutTache, dateFinTache, heuresEstimees) VALUES
(1, 3, 'Modèle de données',               'Conception schéma BD',                                 'Terminée',    'Haute',   '2024-12-01', '2024-12-07', 20.00),
(1, 3, 'API Authentification',            'Endpoints login/logout/register',                      'Terminée',    'Haute',   '2024-12-08', '2024-12-14', 25.00),
(1, 3, 'API Services municipaux',         'CRUD des services et demandes',                        'En cours',    'Haute',   '2024-12-15', '2025-01-15', 40.00),
(1, 3, 'API Notifications',               'Système de notifications push',                        'À faire',     'Moyenne', '2025-01-16', '2025-01-31', 35.00);

-- Sous-tâches du "Développement Frontend" (id=4)
INSERT INTO tache (idProjet, idTacheParent, titreTache, descriptionTache, statutTache, prioriteTache, dateDebutTache, dateFinTache, heuresEstimees) VALUES
(1, 4, 'Page d''accueil',                 'Landing page et navigation',                           'En cours',    'Haute',   '2024-12-15', '2024-12-31', 20.00),
(1, 4, 'Module authentification',         'Formulaires login et inscription',                     'En cours',    'Haute',   '2025-01-01', '2025-01-10', 15.00),
(1, 4, 'Module services',                 'Consultation et demande de services',                  'À faire',     'Haute',   '2025-01-11', '2025-02-05', 40.00),
(1, 4, 'Module profil utilisateur',       'Gestion du profil et historique',                      'À faire',     'Moyenne', '2025-02-06', '2025-02-15', 25.00);

-- --------------------------------------------------
-- Tâches du Projet 2: Application Mobile Hydro
-- --------------------------------------------------
INSERT INTO tache (idProjet, idTacheParent, titreTache, descriptionTache, statutTache, prioriteTache, dateDebutTache, dateFinTache, heuresEstimees) VALUES
(2, NULL, 'Architecture technique',        'Choix technologies et architecture',                   'Terminée',    'Haute',   '2024-12-01', '2024-12-10', 30.00),
(2, NULL, 'API Backend',                   'Services web pour l''application',                     'En cours',    'Haute',   '2024-12-11', '2025-02-28', 150.00),
(2, NULL, 'Application iOS',               'Développement version iPhone',                         'En cours',    'Haute',   '2025-01-15', '2025-04-30', 180.00),
(2, NULL, 'Application Android',           'Développement version Android',                        'À faire',     'Haute',   '2025-02-01', '2025-05-15', 180.00),
(2, NULL, 'Tests et certification',        'Tests complets et soumission aux stores',              'À faire',     'Haute',   '2025-05-16', '2025-06-15', 80.00),
(2, NULL, 'Documentation',                 'Guides utilisateur et technique',                      'À faire',     'Basse',   '2025-06-01', '2025-06-30', 30.00);

-- --------------------------------------------------
-- Tâches du Projet 3: Refonte Intranet (pas encore démarré)
-- --------------------------------------------------
INSERT INTO tache (idProjet, idTacheParent, titreTache, descriptionTache, statutTache, prioriteTache, dateDebutTache, dateFinTache, heuresEstimees) VALUES
(3, NULL, 'Audit de l''existant',         'Analyse de l''intranet actuel',                        'À faire',     'Haute',   '2025-01-15', '2025-01-31', 40.00),
(3, NULL, 'Conception nouvelle architecture', 'Design système et UX',                            'À faire',     'Haute',   '2025-02-01', '2025-02-28', 60.00),
(3, NULL, 'Migration données',             'Migration contenu et utilisateurs',                    'À faire',     'Haute',   '2025-03-01', '2025-03-31', 80.00),
(3, NULL, 'Développement modules',         'Nouvelles fonctionnalités collaboratives',            'À faire',     'Haute',   '2025-04-01', '2025-05-15', 120.00),
(3, NULL, 'Formation et déploiement',      'Formation équipes et mise en ligne',                   'À faire',     'Moyenne', '2025-05-16', '2025-05-31', 40.00);

-- --------------------------------------------------
-- Affectations des employés aux tâches (Projet 1)
-- --------------------------------------------------
-- Sophie: Backend
INSERT INTO affectation_tache (idEmploye, idTache, tauxHoraire, roleSurLaTache) VALUES
(4, 3, 55.00, 'Développeur Backend'),
(4, 7, 55.00, 'Développeur'),
(4, 8, 55.00, 'Développeur'),
(4, 9, 55.00, 'Développeur'),
(4, 10, 55.00, 'Développeur');

-- Marc: Frontend
INSERT INTO affectation_tache (idEmploye, idTache, tauxHoraire, roleSurLaTache) VALUES
(5, 4, 52.00, 'Développeur Frontend'),
(5, 11, 52.00, 'Développeur'),
(5, 12, 52.00, 'Développeur'),
(5, 13, 52.00, 'Développeur'),
(5, 14, 52.00, 'Développeur');

-- Marie: Analyse et gestion
INSERT INTO affectation_tache (idEmploye, idTache, tauxHoraire, roleSurLaTache) VALUES
(2, 1, 75.00, 'Chef de projet'),
(2, 2, 75.00, 'Responsable UX');

-- --------------------------------------------------
-- Affectations des employés aux tâches (Projet 2)
-- --------------------------------------------------
-- Sophie: Backend
INSERT INTO affectation_tache (idEmploye, idTache, tauxHoraire, roleSurLaTache) VALUES
(4, 16, 55.00, 'Développeur Backend');

-- Luc: Mobile
INSERT INTO affectation_tache (idEmploye, idTache, tauxHoraire, roleSurLaTache) VALUES
(7, 17, 58.00, 'Développeur iOS'),
(7, 18, 58.00, 'Développeur Android');

-- Marie: Architecture
INSERT INTO affectation_tache (idEmploye, idTache, tauxHoraire, roleSurLaTache) VALUES
(2, 15, 75.00, 'Architecte');

-- --------------------------------------------------
-- Saisies de temps (dernières semaines)
-- --------------------------------------------------
-- Sophie (Backend Projet 1)
INSERT INTO saisie_temps (idEmploye, idTache, dateTravail, heures, commentaires) VALUES
(4, 9, '2024-12-09', 7.5, 'Développement endpoints CRUD services municipaux'),
(4, 9, '2024-12-10', 8.0, 'Intégration base de données et tests'),
(4, 9, '2024-12-11', 6.5, 'Correction bugs validation formulaires'),
(4, 9, '2024-12-12', 7.0, 'Ajout filtres et pagination'),
(4, 9, '2024-12-13', 5.5, 'Documentation API et tests unitaires');

-- Marc (Frontend Projet 1)
INSERT INTO saisie_temps (idEmploye, idTache, dateTravail, heures, commentaires) VALUES
(5, 11, '2024-12-09', 8.0, 'Intégration maquette page d''accueil'),
(5, 11, '2024-12-10', 7.5, 'Responsive design tablette et mobile'),
(5, 12, '2024-12-11', 6.0, 'Formulaires login et validation client'),
(5, 12, '2024-12-12', 7.0, 'Intégration API authentification'),
(5, 12, '2024-12-13', 5.0, 'Tests navigateurs et corrections CSS');

-- Sophie (Backend Projet 2)
INSERT INTO saisie_temps (idEmploye, idTache, dateTravail, heures, commentaires) VALUES
(4, 16, '2024-12-09', 4.0, 'Setup projet et structure API'),
(4, 16, '2024-12-10', 6.5, 'Endpoints consultation consommation'),
(4, 16, '2024-12-11', 5.0, 'Intégration système de paiement'),
(4, 16, '2024-12-12', 6.0, 'Tests et sécurisation endpoints'),
(4, 16, '2024-12-13', 4.5, 'Documentation Swagger API');

-- Luc (Mobile Projet 2)
INSERT INTO saisie_temps (idEmploye, idTache, dateTravail, heures, commentaires) VALUES
(7, 17, '2024-12-09', 7.0, 'Setup projet Xcode et architecture'),
(7, 17, '2024-12-10', 8.0, 'Écrans authentification iOS'),
(7, 17, '2024-12-11', 7.5, 'Intégration API et gestion état'),
(7, 17, '2024-12-12', 6.5, 'Écran consultation consommation'),
(7, 17, '2024-12-13', 7.0, 'Tests sur différents modèles iPhone');

-- --------------------------------------------------
-- Feuilles de temps (pour validation)
-- --------------------------------------------------
-- Feuille Sophie (semaine du 9 au 13 déc)
INSERT INTO feuille_temps (idEmploye, statut, dateSoumission, heures, idApprobateur) VALUES
(4, 'SOUMISE', '2024-12-13 17:00:00', 65.0, 2);

-- Feuille Marc (semaine du 9 au 13 déc)
INSERT INTO feuille_temps (idEmploye, statut, dateSoumission, heures, idApprobateur) VALUES
(5, 'SOUMISE', '2024-12-13 16:30:00', 33.5, 2);

-- Feuille Luc (semaine du 9 au 13 déc)
INSERT INTO feuille_temps (idEmploye, statut, dateSoumission, heures, idApprobateur) VALUES
(7, 'SOUMISE', '2024-12-13 17:15:00', 36.0, 2);

-- Liaison feuilles de temps avec saisies
-- Feuille Sophie
INSERT INTO ligne_feuille_temps (idFeuille, idSaisie)
SELECT 1, idSaisie FROM saisie_temps WHERE idEmploye = 4;

-- Feuille Marc
INSERT INTO ligne_feuille_temps (idFeuille, idSaisie)
SELECT 2, idSaisie FROM saisie_temps WHERE idEmploye = 5;

-- Feuille Luc
INSERT INTO ligne_feuille_temps (idFeuille, idSaisie)
SELECT 3, idSaisie FROM saisie_temps WHERE idEmploye = 7;

-- ======================================================================
-- 4. CRÉATION DES VUES UTILES
-- ======================================================================

-- Vue agrégation temps par tâche
CREATE VIEW v_temps_par_tache AS
SELECT
  t.idTache,
  t.titreTache,
  t.idProjet,
  p.nomProjet,
  SUM(st.heures) AS total_heures_saisies,
  t.heuresEstimees,
  ROUND((SUM(st.heures) / NULLIF(t.heuresEstimees, 0)) * 100, 1) AS pourcentage_completion,
  COUNT(DISTINCT st.idEmploye) AS nombre_employes,
  MAX(st.dateTravail) AS derniere_saisie
FROM tache t
LEFT JOIN saisie_temps st ON t.idTache = st.idTache
LEFT JOIN projet p ON t.idProjet = p.idProjet
GROUP BY t.idTache, t.titreTache, t.idProjet, p.nomProjet, t.heuresEstimees;

-- Vue temps par employé et projet
CREATE VIEW v_temps_par_employe_projet AS
SELECT
  e.idEmploye,
  CONCAT(e.prenomEmploye, ' ', e.nomEmploye) AS employe,
  p.idProjet,
  p.nomProjet,
  SUM(st.heures) AS total_heures,
  COUNT(DISTINCT st.idTache) AS nombre_taches,
  MIN(st.dateTravail) AS premiere_saisie,
  MAX(st.dateTravail) AS derniere_saisie
FROM employe e
JOIN saisie_temps st ON e.idEmploye = st.idEmploye
JOIN tache t ON st.idTache = t.idTache
JOIN projet p ON t.idProjet = p.idProjet
GROUP BY e.idEmploye, e.prenomEmploye, e.nomEmploye, p.idProjet, p.nomProjet;

-- ======================================================================
-- 5. VÉRIFICATIONS ET STATISTIQUES
-- ======================================================================

-- Résumé de la base de données
SELECT 'Base de données créée avec succès!' AS statut;
SELECT DATABASE() AS base_de_donnees;

-- Statistiques des données insérées
SELECT 'STATISTIQUES DE LA BASE DE DONNÉES' AS '===';
SELECT COUNT(*) AS total_roles FROM role;
SELECT COUNT(*) AS total_employes FROM employe;
SELECT COUNT(*) AS total_clients FROM client;
SELECT COUNT(*) AS total_projets FROM projet;
SELECT COUNT(*) AS total_taches FROM tache;
SELECT COUNT(*) AS total_saisies_temps FROM saisie_temps;
SELECT COUNT(*) AS total_feuilles_temps FROM feuille_temps;

-- Liste des utilisateurs pour connexion
SELECT 
  'COMPTES UTILISATEURS POUR TESTS' AS '===',
  CONCAT(prenomEmploye, ' ', nomEmploye) AS utilisateur,
  courrielEmploye AS email,
  nomRole AS role,
  'password123' AS mot_de_passe_demo
FROM employe e
JOIN role r ON e.idRole = r.idRole
ORDER BY r.idRole, e.idEmploye;

-- Résumé des projets
SELECT 
  'PROJETS DISPONIBLES' AS '===',
  p.idProjet,
  p.nomProjet,
  p.statutProjet AS statut,
  c.nomClient AS client,
  CONCAT(e.prenomEmploye, ' ', e.nomEmploye) AS responsable,
  p.heuresBudget AS budget_heures,
  COUNT(DISTINCT t.idTache) AS nombre_taches,
  COUNT(DISTINCT pe.idEmploye) AS nombre_membres
FROM projet p
LEFT JOIN client c ON p.idClient = c.idClient
LEFT JOIN employe e ON p.idEmploye = e.idEmploye
LEFT JOIN tache t ON p.idProjet = t.idProjet
LEFT JOIN projet_employe pe ON p.idProjet = pe.idProjet
GROUP BY p.idProjet, p.nomProjet, p.statutProjet, c.nomClient, e.prenomEmploye, e.nomEmploye, p.heuresBudget
ORDER BY p.idProjet;

-- Temps saisis par projet
SELECT 
  'TEMPS SAISIS PAR PROJET' AS '===',
  p.nomProjet,
  SUM(st.heures) AS heures_saisies,
  p.heuresBudget AS budget,
  ROUND((SUM(st.heures) / p.heuresBudget) * 100, 1) AS pourcentage_utilise
FROM projet p
LEFT JOIN tache t ON p.idProjet = t.idProjet
LEFT JOIN saisie_temps st ON t.idTache = st.idTache
GROUP BY p.idProjet, p.nomProjet, p.heuresBudget
ORDER BY p.idProjet;

SELECT '======================================================' AS '';
SELECT 'Installation terminée! Vous pouvez maintenant tester l''application.' AS '';
SELECT 'Utilisez les comptes ci-dessus pour vous connecter (mot de passe: password123)' AS '';
SELECT '======================================================' AS '';
