-- Table de liaison pour les membres assignés aux projets
CREATE TABLE IF NOT EXISTS projet_employe (
  idProjet INT NOT NULL,
  idEmploye INT NOT NULL,
  PRIMARY KEY (idProjet, idEmploye),
  CONSTRAINT fk_pe_projet FOREIGN KEY (idProjet) REFERENCES projet(idProjet) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_pe_employe FOREIGN KEY (idEmploye) REFERENCES employe(idEmploye) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- Exemple de données de test : assigner quelques employés à des projets existants
-- Vous pouvez adapter les valeurs selon vos besoins
INSERT IGNORE INTO projet_employe (idProjet, idEmploye) VALUES
(1, 1),  -- Projet 1 : Admin Alpha
(1, 2),  -- Projet 1 : Gestionnaire Beta  
(1, 3);  -- Projet 1 : Employé Gamma
