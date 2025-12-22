-- MySQL dump 10.13  Distrib 8.0.41, for Win64 (x86_64)
--
-- Host: localhost    Database: project_time_gestion
-- ------------------------------------------------------
-- Server version	8.0.41

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Current Database: `project_time_gestion`
--

/*!40000 DROP DATABASE IF EXISTS `project_time_gestion`*/;

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `project_time_gestion` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;

USE `project_time_gestion`;

--
-- Table structure for table `affectation_tache`
--

DROP TABLE IF EXISTS `affectation_tache`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `affectation_tache` (
  `idEmploye` int NOT NULL,
  `idTache` int NOT NULL,
  `tauxHoraire` decimal(10,2) DEFAULT NULL,
  `roleSurLaTache` varchar(80) DEFAULT NULL,
  PRIMARY KEY (`idEmploye`,`idTache`),
  KEY `idx_aff_tache` (`idTache`),
  CONSTRAINT `fk_aff_emp` FOREIGN KEY (`idEmploye`) REFERENCES `employe` (`idEmploye`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_aff_tache` FOREIGN KEY (`idTache`) REFERENCES `tache` (`idTache`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `affectation_tache`
--

LOCK TABLES `affectation_tache` WRITE;
/*!40000 ALTER TABLE `affectation_tache` DISABLE KEYS */;
INSERT INTO `affectation_tache` (`idEmploye`, `idTache`, `tauxHoraire`, `roleSurLaTache`) VALUES (2,48,NULL,'Collaborateur'),(8,43,NULL,'Collaborateur'),(8,44,NULL,'Collaborateur'),(8,48,NULL,'Collaborateur'),(8,49,NULL,'Collaborateur'),(9,28,NULL,'Collaborateur'),(9,29,NULL,'Collaborateur'),(9,30,NULL,'Collaborateur'),(9,31,NULL,'Collaborateur'),(9,32,NULL,'Collaborateur'),(9,33,NULL,'Collaborateur'),(9,35,NULL,'Collaborateur'),(9,36,NULL,'Collaborateur'),(9,37,NULL,'Collaborateur'),(9,38,NULL,'Collaborateur'),(9,43,NULL,'Collaborateur'),(9,44,NULL,'Collaborateur'),(9,46,NULL,'Collaborateur'),(9,47,NULL,'Collaborateur'),(9,48,NULL,'Collaborateur'),(9,49,NULL,'Collaborateur'),(9,50,NULL,'Collaborateur'),(10,32,NULL,'Collaborateur'),(10,33,NULL,'Collaborateur'),(10,37,NULL,'Collaborateur'),(10,38,NULL,'Collaborateur'),(10,48,NULL,'Collaborateur'),(10,49,NULL,'Collaborateur'),(12,31,NULL,'Collaborateur'),(12,46,NULL,'Collaborateur'),(12,47,NULL,'Collaborateur'),(12,48,NULL,'Collaborateur'),(12,49,NULL,'Collaborateur'),(12,50,NULL,'Collaborateur'),(41,48,NULL,'Collaborateur'),(42,48,NULL,'Collaborateur'),(42,49,NULL,'Collaborateur');
/*!40000 ALTER TABLE `affectation_tache` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `client`
--

DROP TABLE IF EXISTS `client`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `client` (
  `idClient` int NOT NULL AUTO_INCREMENT,
  `nomClient` varchar(160) NOT NULL,
  `telephoneClient` varchar(40) DEFAULT NULL,
  `courrielClient` varchar(180) DEFAULT NULL,
  `statutClient` varchar(60) DEFAULT NULL,
  PRIMARY KEY (`idClient`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `client`
--

LOCK TABLES `client` WRITE;
/*!40000 ALTER TABLE `client` DISABLE KEYS */;
INSERT INTO `client` (`idClient`, `nomClient`, `telephoneClient`, `courrielClient`, `statutClient`) VALUES (1,'Client D├®mo','418-000-0000','contact@clientdemo.ca','Actif'),(2,'Client D├®mo','418-000-0000','contact@clientdemo.ca','Actif');
/*!40000 ALTER TABLE `client` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `departement`
--

DROP TABLE IF EXISTS `departement`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `departement` (
  `idDepartement` int NOT NULL AUTO_INCREMENT,
  `nomDepartement` varchar(120) NOT NULL,
  PRIMARY KEY (`idDepartement`),
  UNIQUE KEY `nomDepartement` (`nomDepartement`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `departement`
--

LOCK TABLES `departement` WRITE;
/*!40000 ALTER TABLE `departement` DISABLE KEYS */;
INSERT INTO `departement` (`idDepartement`, `nomDepartement`) VALUES (2,'Comptabilit├®'),(1,'Informatique');
/*!40000 ALTER TABLE `departement` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `dependance_tache`
--

DROP TABLE IF EXISTS `dependance_tache`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `dependance_tache` (
  `idPredecesseur` int NOT NULL,
  `idSuccesseur` int NOT NULL,
  `typeDependance` enum('FS','SS','FF','SF') NOT NULL DEFAULT 'FS',
  PRIMARY KEY (`idPredecesseur`,`idSuccesseur`),
  KEY `fk_dep_succ` (`idSuccesseur`),
  CONSTRAINT `fk_dep_pred` FOREIGN KEY (`idPredecesseur`) REFERENCES `tache` (`idTache`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_dep_succ` FOREIGN KEY (`idSuccesseur`) REFERENCES `tache` (`idTache`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `dependance_tache`
--

LOCK TABLES `dependance_tache` WRITE;
/*!40000 ALTER TABLE `dependance_tache` DISABLE KEYS */;
/*!40000 ALTER TABLE `dependance_tache` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = cp850 */ ;
/*!50003 SET character_set_results = cp850 */ ;
/*!50003 SET collation_connection  = cp850_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `bi_depen_no_self` BEFORE INSERT ON `dependance_tache` FOR EACH ROW BEGIN
  IF NEW.idPredecesseur = NEW.idSuccesseur THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Une tâche ne peut pas dépendre d’elle-même.';
  END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = cp850 */ ;
/*!50003 SET character_set_results = cp850 */ ;
/*!50003 SET collation_connection  = cp850_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `bu_depen_no_self` BEFORE UPDATE ON `dependance_tache` FOR EACH ROW BEGIN
  IF NEW.idPredecesseur = NEW.idSuccesseur THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Une tâche ne peut pas dépendre d’elle-même.';
  END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `droit`
--

DROP TABLE IF EXISTS `droit`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `droit` (
  `idDroit` int NOT NULL AUTO_INCREMENT,
  `code` varchar(64) NOT NULL,
  `specification` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`idDroit`),
  UNIQUE KEY `code` (`code`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `droit`
--

LOCK TABLES `droit` WRITE;
/*!40000 ALTER TABLE `droit` DISABLE KEYS */;
INSERT INTO `droit` (`idDroit`, `code`, `specification`) VALUES (1,'VIEW','Consulter'),(2,'CREATE','Cr├®er'),(3,'EDIT','Modifier'),(4,'DELETE','Supprimer'),(5,'APPROVE','Approuver');
/*!40000 ALTER TABLE `droit` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `employe`
--

DROP TABLE IF EXISTS `employe`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `employe` (
  `idEmploye` int NOT NULL AUTO_INCREMENT,
  `idDepartement` int DEFAULT NULL,
  `idRole` int NOT NULL,
  `nomEmploye` varchar(120) NOT NULL,
  `prenomEmploye` varchar(120) NOT NULL,
  `motDePasse` varchar(255) NOT NULL,
  `telephoneEmploye` varchar(40) DEFAULT NULL,
  `courrielEmploye` varchar(180) NOT NULL,
  PRIMARY KEY (`idEmploye`),
  UNIQUE KEY `courrielEmploye` (`courrielEmploye`),
  KEY `idx_emp_dep` (`idDepartement`),
  KEY `idx_emp_role` (`idRole`),
  CONSTRAINT `fk_emp_dep` FOREIGN KEY (`idDepartement`) REFERENCES `departement` (`idDepartement`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_emp_role` FOREIGN KEY (`idRole`) REFERENCES `role` (`idRole`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=43 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `employe`
--

LOCK TABLES `employe` WRITE;
/*!40000 ALTER TABLE `employe` DISABLE KEYS */;
INSERT INTO `employe` (`idEmploye`, `idDepartement`, `idRole`, `nomEmploye`, `prenomEmploye`, `motDePasse`, `telephoneEmploye`, `courrielEmploye`) VALUES (2,1,2,'Gestion','Beta','$2y$10$hashFake','000-000-0001','beta.gestion@exemple.com'),(8,1,3,'quewel','','scrypt:32768:8:1$ZbxAB6hMVouzJ0ng$0f686007df79a91bc781652eebfeff8318c7965dc4fe1937a0a2c3fda178227e4648970500093304b4434f81cb0100c49004f06deefc64aecc936f5595c2075b','','quewel@gmail.com'),(9,1,1,'Yasmine Kagone','','scrypt:32768:8:1$vXipQuo5eHZ6algQ$4ea9649210dc137b7ea8a9f92d8cedba51bf49ac6cb27d5459410547490e866f0f739a5ec96932387852a63966700645c5efaa8442884796da35d0aa27d7e2a2','','yas@gmail.com'),(10,1,3,'mo','','scrypt:32768:8:1$wSN99GznMfhfszAY$4d987dc09f635fa00c7aed4fe5bbb708fdb170fd7c82b68095ac91ad1b29c6b10ceb53e55d22413d3bc80e4aa77f33a9e9db96bcfa9cd9a47971d788b558401b','','mo@gmail.com'),(12,1,2,'Samuel Kouakou','','scrypt:32768:8:1$41WsIa0byi8LJG4M$1d7424d40f7d054de255608d9bc8f729cf70739045f9d15aa21974e70437981439385e5056b0db5113c788b8c4d6b528bf9a7acc79a658d3b365ec8996c5816a','','sam@gmail.com'),(41,1,2,'Catherine Bonlook','','scrypt:32768:8:1$WbTryGmwIsbJWLRf$5be619bb06a365dc134bbd0447b752ceb55ab476ebcbb9b6e43473b2c0e4cda18cff63cd908853c11df505e8593cd5e28a17b0803b7ebe692a4aeddd98a66a24','','cath@gmail.com'),(42,1,1,'dernier test','','scrypt:32768:8:1$nIj3kMHfUGa5Ftgf$79e09bcd767628e34c8500b49217fe40f67977b244de569aa1a33aa70f7813733946776a9c85709f0c071ced1a537ba9c15481d9aa00556d2d08cf78fd0ddf51','','test@gmail.com');
/*!40000 ALTER TABLE `employe` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `employe_equipe`
--

DROP TABLE IF EXISTS `employe_equipe`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `employe_equipe` (
  `idEmploye` int NOT NULL,
  `idEquipe` int NOT NULL,
  PRIMARY KEY (`idEmploye`,`idEquipe`),
  KEY `fk_ee_equip` (`idEquipe`),
  CONSTRAINT `fk_ee_emp` FOREIGN KEY (`idEmploye`) REFERENCES `employe` (`idEmploye`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_ee_equip` FOREIGN KEY (`idEquipe`) REFERENCES `equipe` (`idEquipe`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `employe_equipe`
--

LOCK TABLES `employe_equipe` WRITE;
/*!40000 ALTER TABLE `employe_equipe` DISABLE KEYS */;
/*!40000 ALTER TABLE `employe_equipe` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `equipe`
--

DROP TABLE IF EXISTS `equipe`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `equipe` (
  `idEquipe` int NOT NULL AUTO_INCREMENT,
  `nomEquipe` varchar(120) NOT NULL,
  `idProjet` int DEFAULT NULL,
  PRIMARY KEY (`idEquipe`),
  KEY `fk_equipe_projet` (`idProjet`),
  CONSTRAINT `fk_equipe_projet` FOREIGN KEY (`idProjet`) REFERENCES `projet` (`idProjet`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `equipe`
--

LOCK TABLES `equipe` WRITE;
/*!40000 ALTER TABLE `equipe` DISABLE KEYS */;
/*!40000 ALTER TABLE `equipe` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `etat`
--

DROP TABLE IF EXISTS `etat`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `etat` (
  `idEtat` int NOT NULL AUTO_INCREMENT,
  `nomEtat` varchar(60) NOT NULL,
  PRIMARY KEY (`idEtat`),
  UNIQUE KEY `nomEtat` (`nomEtat`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `etat`
--

LOCK TABLES `etat` WRITE;
/*!40000 ALTER TABLE `etat` DISABLE KEYS */;
INSERT INTO `etat` (`idEtat`, `nomEtat`) VALUES (1,'EN_ATTENTE'),(2,'EN_COURS'),(4,'EN_PROBLEME'),(3,'TERMINEE');
/*!40000 ALTER TABLE `etat` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `feuille_temps`
--

DROP TABLE IF EXISTS `feuille_temps`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `feuille_temps` (
  `idFeuille` int NOT NULL AUTO_INCREMENT,
  `idEmploye` int NOT NULL,
  `statut` enum('EN_COURS','SOUMISE','APPROUVEE','REJETEE') DEFAULT 'EN_COURS',
  `dateSoumission` datetime DEFAULT NULL,
  `dateDecision` datetime DEFAULT NULL,
  `heures` decimal(10,2) DEFAULT '0.00',
  `idApprobateur` int DEFAULT NULL,
  PRIMARY KEY (`idFeuille`),
  KEY `fk_ft_emp` (`idEmploye`),
  KEY `fk_ft_approb` (`idApprobateur`),
  CONSTRAINT `fk_ft_approb` FOREIGN KEY (`idApprobateur`) REFERENCES `employe` (`idEmploye`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_ft_emp` FOREIGN KEY (`idEmploye`) REFERENCES `employe` (`idEmploye`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `feuille_temps`
--

LOCK TABLES `feuille_temps` WRITE;
/*!40000 ALTER TABLE `feuille_temps` DISABLE KEYS */;
/*!40000 ALTER TABLE `feuille_temps` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ligne_feuille_temps`
--

DROP TABLE IF EXISTS `ligne_feuille_temps`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ligne_feuille_temps` (
  `idFeuille` int NOT NULL,
  `idSaisie` int NOT NULL,
  PRIMARY KEY (`idFeuille`,`idSaisie`),
  KEY `fk_lft_saisie` (`idSaisie`),
  CONSTRAINT `fk_lft_feuille` FOREIGN KEY (`idFeuille`) REFERENCES `feuille_temps` (`idFeuille`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_lft_saisie` FOREIGN KEY (`idSaisie`) REFERENCES `saisie_temps` (`idSaisie`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ligne_feuille_temps`
--

LOCK TABLES `ligne_feuille_temps` WRITE;
/*!40000 ALTER TABLE `ligne_feuille_temps` DISABLE KEYS */;
/*!40000 ALTER TABLE `ligne_feuille_temps` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `projet`
--

DROP TABLE IF EXISTS `projet`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `projet` (
  `idProjet` int NOT NULL AUTO_INCREMENT,
  `nomProjet` varchar(200) NOT NULL,
  `dateDebut` date NOT NULL,
  `dateFin` date DEFAULT NULL,
  `heuresBudget` decimal(10,2) DEFAULT '0.00',
  `coutsProjet` decimal(12,2) DEFAULT '0.00',
  `idClient` int DEFAULT NULL,
  `idEmploye` int NOT NULL,
  `idTemplateProjet` int DEFAULT NULL,
  `descriptionProjet` text,
  `statutProjet` enum('À faire','En cours','Terminé','En retard') DEFAULT 'À faire',
  PRIMARY KEY (`idProjet`),
  KEY `fk_proj_client` (`idClient`),
  KEY `fk_proj_tpl` (`idTemplateProjet`),
  KEY `idx_proj_resp` (`idEmploye`),
  CONSTRAINT `fk_proj_client` FOREIGN KEY (`idClient`) REFERENCES `client` (`idClient`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_proj_resp` FOREIGN KEY (`idEmploye`) REFERENCES `employe` (`idEmploye`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_proj_tpl` FOREIGN KEY (`idTemplateProjet`) REFERENCES `template_projet` (`idTemplateProjet`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=20 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `projet`
--

LOCK TABLES `projet` WRITE;
/*!40000 ALTER TABLE `projet` DISABLE KEYS */;
INSERT INTO `projet` (`idProjet`, `nomProjet`, `dateDebut`, `dateFin`, `heuresBudget`, `coutsProjet`, `idClient`, `idEmploye`, `idTemplateProjet`, `descriptionProjet`, `statutProjet`) VALUES (11,'test de lancement','2025-12-08','2026-01-04',0.00,0.00,NULL,2,1,'faire une serie de test de validation','En cours'),(12,'test de projet en retard','2025-11-12','2025-11-28',0.00,0.00,NULL,2,1,'','En retard'),(15,'Mikael','2025-12-08','2026-01-11',0.00,0.00,NULL,2,1,'test dugagjaehnjzu','À faire'),(16,'creation de nouvelle lunette','2026-03-01','2026-04-05',0.00,0.00,NULL,2,1,'','À faire'),(19,'site petrol','2025-12-01','2025-12-12',0.00,0.00,NULL,2,1,'','Terminé');
/*!40000 ALTER TABLE `projet` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `projet_employe`
--

DROP TABLE IF EXISTS `projet_employe`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `projet_employe` (
  `idProjet` int NOT NULL,
  `idEmploye` int NOT NULL,
  PRIMARY KEY (`idProjet`,`idEmploye`),
  KEY `fk_pe_employe` (`idEmploye`),
  CONSTRAINT `fk_pe_employe` FOREIGN KEY (`idEmploye`) REFERENCES `employe` (`idEmploye`) ON DELETE CASCADE,
  CONSTRAINT `fk_pe_projet` FOREIGN KEY (`idProjet`) REFERENCES `projet` (`idProjet`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `projet_employe`
--

LOCK TABLES `projet_employe` WRITE;
/*!40000 ALTER TABLE `projet_employe` DISABLE KEYS */;
INSERT INTO `projet_employe` (`idProjet`, `idEmploye`) VALUES (19,2),(12,8),(15,8),(16,8),(19,8),(11,9),(12,9),(15,9),(16,9),(19,9),(11,10),(15,10),(16,10),(19,10),(16,12),(19,12),(16,41),(19,41),(19,42);
/*!40000 ALTER TABLE `projet_employe` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `role`
--

DROP TABLE IF EXISTS `role`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `role` (
  `idRole` int NOT NULL AUTO_INCREMENT,
  `nomRole` varchar(80) NOT NULL,
  `descriptionRole` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`idRole`),
  UNIQUE KEY `nomRole` (`nomRole`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `role`
--

LOCK TABLES `role` WRITE;
/*!40000 ALTER TABLE `role` DISABLE KEYS */;
INSERT INTO `role` (`idRole`, `nomRole`, `descriptionRole`) VALUES (1,'Admin','Administration globale'),(2,'Gestionnaire','G├¿re projets & approbations'),(3,'Employe','Saisie des temps');
/*!40000 ALTER TABLE `role` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `role_droit`
--

DROP TABLE IF EXISTS `role_droit`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `role_droit` (
  `idRole` int NOT NULL,
  `idDroit` int NOT NULL,
  PRIMARY KEY (`idRole`,`idDroit`),
  KEY `fk_roledroit_droit` (`idDroit`),
  CONSTRAINT `fk_roledroit_droit` FOREIGN KEY (`idDroit`) REFERENCES `droit` (`idDroit`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_roledroit_role` FOREIGN KEY (`idRole`) REFERENCES `role` (`idRole`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `role_droit`
--

LOCK TABLES `role_droit` WRITE;
/*!40000 ALTER TABLE `role_droit` DISABLE KEYS */;
INSERT INTO `role_droit` (`idRole`, `idDroit`) VALUES (1,1),(2,1),(3,1),(1,2),(2,2),(3,2),(1,3),(2,3),(1,4),(1,5),(2,5);
/*!40000 ALTER TABLE `role_droit` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `saisie_temps`
--

DROP TABLE IF EXISTS `saisie_temps`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `saisie_temps` (
  `idSaisie` int NOT NULL AUTO_INCREMENT,
  `idEmploye` int NOT NULL,
  `idTache` int NOT NULL,
  `dateTravail` date NOT NULL,
  `heures` decimal(6,2) NOT NULL,
  `commentaires` text,
  PRIMARY KEY (`idSaisie`),
  KEY `idx_st_emp_date` (`idEmploye`,`dateTravail`),
  KEY `idx_st_tache` (`idTache`),
  CONSTRAINT `fk_st_emp` FOREIGN KEY (`idEmploye`) REFERENCES `employe` (`idEmploye`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_st_tache` FOREIGN KEY (`idTache`) REFERENCES `tache` (`idTache`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `saisie_temps_chk_1` CHECK ((`heures` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `saisie_temps`
--

LOCK TABLES `saisie_temps` WRITE;
/*!40000 ALTER TABLE `saisie_temps` DISABLE KEYS */;
INSERT INTO `saisie_temps` (`idSaisie`, `idEmploye`, `idTache`, `dateTravail`, `heures`, `commentaires`) VALUES (15,10,37,'2025-12-02',2.00,NULL),(16,9,35,'2025-12-04',2.00,'YGHIQU'),(17,10,38,'2025-12-04',1.00,NULL),(18,9,44,'2025-12-06',1.00,NULL),(19,10,32,'2025-12-06',1.00,NULL),(20,10,48,'2025-12-14',0.50,'kjsvj');
/*!40000 ALTER TABLE `saisie_temps` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tache`
--

DROP TABLE IF EXISTS `tache`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tache` (
  `idTache` int NOT NULL AUTO_INCREMENT,
  `idProjet` int NOT NULL,
  `nomTache` varchar(200) NOT NULL,
  `descriptionTache` text,
  `dateDebutTache` date DEFAULT NULL,
  `dateFinTache` date DEFAULT NULL,
  `heuresAllouees` decimal(10,2) DEFAULT '0.00',
  `idEtat` int NOT NULL,
  `idParentTache` int DEFAULT NULL,
  `idTacheParent` int DEFAULT NULL,
  `titreTache` varchar(255) DEFAULT NULL,
  `statutTache` enum('À faire','En cours','En révision','Terminée') DEFAULT 'À faire',
  `prioriteTache` enum('Basse','Moyenne','Haute') DEFAULT 'Moyenne',
  `dateDebut` date DEFAULT NULL,
  `dateFin` date DEFAULT NULL,
  `heuresEstimees` decimal(5,2) DEFAULT '0.00',
  PRIMARY KEY (`idTache`),
  KEY `fk_tache_etat` (`idEtat`),
  KEY `idx_tache_proj` (`idProjet`),
  KEY `idx_tache_parent` (`idParentTache`),
  KEY `idTacheParent` (`idTacheParent`),
  CONSTRAINT `fk_tache_etat` FOREIGN KEY (`idEtat`) REFERENCES `etat` (`idEtat`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_tache_parent` FOREIGN KEY (`idParentTache`) REFERENCES `tache` (`idTache`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_tache_projet` FOREIGN KEY (`idProjet`) REFERENCES `projet` (`idProjet`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `tache_ibfk_1` FOREIGN KEY (`idTacheParent`) REFERENCES `tache` (`idTache`) ON DELETE CASCADE,
  CONSTRAINT `tache_ibfk_2` FOREIGN KEY (`idTacheParent`) REFERENCES `tache` (`idTache`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=51 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tache`
--

LOCK TABLES `tache` WRITE;
/*!40000 ALTER TABLE `tache` DISABLE KEYS */;
INSERT INTO `tache` (`idTache`, `idProjet`, `nomTache`, `descriptionTache`, `dateDebutTache`, `dateFinTache`, `heuresAllouees`, `idEtat`, `idParentTache`, `idTacheParent`, `titreTache`, `statutTache`, `prioriteTache`, `dateDebut`, `dateFin`, `heuresEstimees`) VALUES (26,11,'premier test','verifier les dates','2025-12-08','2025-12-19',0.00,1,NULL,NULL,'premier test','En cours','Basse',NULL,NULL,2.00),(27,11,'deuxieme test d\'ajout de tache','ajouter une deuxieme tache fictive','2025-12-09','2026-01-02',0.00,1,NULL,NULL,'deuxieme test d\'ajout de tache','À faire','Moyenne',NULL,NULL,4.00),(28,11,'test d\'ajout de sous tache','premiere sous tache','2025-12-09','2025-12-17',0.00,1,NULL,26,'test d\'ajout de sous tache','En cours','Haute',NULL,NULL,2.00),(29,11,'test d\'ajout de sous  sous tache','premiere sous sous tache','2025-12-10','2025-12-13',0.00,1,NULL,28,'test d\'ajout de sous  sous tache','En cours','Haute',NULL,NULL,2.00),(30,11,'test d\'ajout de sous  sous sous tache','premiere sous sous sous tache','2025-12-10','2025-12-12',0.00,1,NULL,29,'test d\'ajout de sous  sous sous tache','En révision','Moyenne',NULL,NULL,3.00),(31,11,'troisieme tache de yasmine','','2025-12-09','2025-12-27',0.00,1,NULL,NULL,'troisieme tache de yasmine','Terminée','Haute',NULL,NULL,6.00),(32,11,'sous tache de la troisieme tache ','','2025-12-08','2026-01-03',0.00,1,NULL,31,'sous tache de la troisieme tache ','Terminée','Moyenne',NULL,NULL,6.00),(33,11,'test de la barre de progression','','2025-12-09','2026-01-02',0.00,1,NULL,NULL,'test de la barre de progression','Terminée','Moyenne',NULL,NULL,3.00),(34,11,'test de la barre de progression1','','2025-12-09','2026-01-02',0.00,1,NULL,33,'test de la barre de progression1','Terminée','Moyenne',NULL,NULL,2.00),(35,11,'test de la barre de progression2','','2025-12-09','2025-12-31',0.00,1,NULL,34,'test de la barre de progression2','Terminée','Moyenne',NULL,NULL,1.00),(36,11,'test de la barre de progression4','','2025-12-09','2025-12-25',0.00,1,NULL,35,'test de la barre de progression4','Terminée','Haute',NULL,NULL,2.00),(37,11,'test654','','2025-12-08','2026-01-04',0.00,1,NULL,NULL,'test654','Terminée','Moyenne',NULL,NULL,8.00),(38,11,'faire un test','','2025-12-09','2025-12-31',0.00,1,NULL,37,'faire un test','Terminée','Moyenne',NULL,NULL,2.00),(43,15,'iyhiuq','fuQO','2025-12-10','2026-01-04',0.00,1,NULL,NULL,'iyhiuq','Terminée','Moyenne',NULL,NULL,4.00),(44,15,'HGFGVHKBI','YTGIUOHJOI','2025-12-10','2026-01-01',0.00,1,NULL,43,'HGFGVHKBI','Terminée','Haute',NULL,NULL,2.00),(46,11,'ngrok','','2025-12-09','2025-12-18',0.00,1,NULL,26,'ngrok','Terminée','Basse',NULL,NULL,4.00),(47,11,'tester ngrok','','2025-12-09','2025-12-14',0.00,1,NULL,46,'tester ngrok','Terminée','Moyenne',NULL,NULL,2.00),(48,19,'faire un test','pas grand chose','2025-12-03','2025-12-05',0.00,1,NULL,NULL,'faire un test','Terminée','Haute',NULL,NULL,3.00),(49,19,'jkkkkkkkk','','2025-12-04','2025-12-04',0.00,1,NULL,48,'jkkkkkkkk','Terminée','Moyenne',NULL,NULL,2.00),(50,15,'maquette projet','','2025-12-18','2026-01-03',0.00,1,NULL,NULL,'maquette projet','À faire','Moyenne',NULL,NULL,3.00);
/*!40000 ALTER TABLE `tache` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `template_projet`
--

DROP TABLE IF EXISTS `template_projet`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `template_projet` (
  `idTemplateProjet` int NOT NULL AUTO_INCREMENT,
  `nomTemplate` varchar(160) NOT NULL,
  `descriptionTemplate` text,
  `heuresTemplate` decimal(10,2) DEFAULT '0.00',
  `coutsTemplate` decimal(12,2) DEFAULT '0.00',
  PRIMARY KEY (`idTemplateProjet`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `template_projet`
--

LOCK TABLES `template_projet` WRITE;
/*!40000 ALTER TABLE `template_projet` DISABLE KEYS */;
INSERT INTO `template_projet` (`idTemplateProjet`, `nomTemplate`, `descriptionTemplate`, `heuresTemplate`, `coutsTemplate`) VALUES (1,'Template Agile','Backlog + Sprint + Revue',120.00,0.00),(2,'Template Agile','Backlog + Sprint + Revue',120.00,0.00);
/*!40000 ALTER TABLE `template_projet` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `template_tache`
--

DROP TABLE IF EXISTS `template_tache`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `template_tache` (
  `idTemplateTache` int NOT NULL AUTO_INCREMENT,
  `idTemplateProjet` int NOT NULL,
  `nomTemplateTache` varchar(160) NOT NULL,
  `descriptionTemplateTache` text,
  `heuresTemplateTache` decimal(10,2) DEFAULT '0.00',
  `idParentTemplateTache` int DEFAULT NULL,
  PRIMARY KEY (`idTemplateTache`),
  KEY `fk_tt_tpl` (`idTemplateProjet`),
  KEY `fk_tt_parent` (`idParentTemplateTache`),
  CONSTRAINT `fk_tt_parent` FOREIGN KEY (`idParentTemplateTache`) REFERENCES `template_tache` (`idTemplateTache`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_tt_tpl` FOREIGN KEY (`idTemplateProjet`) REFERENCES `template_projet` (`idTemplateProjet`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `template_tache`
--

LOCK TABLES `template_tache` WRITE;
/*!40000 ALTER TABLE `template_tache` DISABLE KEYS */;
/*!40000 ALTER TABLE `template_tache` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Temporary view structure for view `v_temps_par_tache`
--

DROP TABLE IF EXISTS `v_temps_par_tache`;
/*!50001 DROP VIEW IF EXISTS `v_temps_par_tache`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `v_temps_par_tache` AS SELECT 
 1 AS `idTache`,
 1 AS `nomTache`,
 1 AS `idProjet`,
 1 AS `total_heures`,
 1 AS `commentaires`*/;
SET character_set_client = @saved_cs_client;

--
-- Dumping events for database 'project_time_gestion'
--

--
-- Dumping routines for database 'project_time_gestion'
--

--
-- Current Database: `project_time_gestion`
--

USE `project_time_gestion`;

--
-- Final view structure for view `v_temps_par_tache`
--

/*!50001 DROP VIEW IF EXISTS `v_temps_par_tache`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = cp850 */;
/*!50001 SET character_set_results     = cp850 */;
/*!50001 SET collation_connection      = cp850_general_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_temps_par_tache` AS select `t`.`idTache` AS `idTache`,`t`.`nomTache` AS `nomTache`,`t`.`idProjet` AS `idProjet`,sum(`st`.`heures`) AS `total_heures`,group_concat(`st`.`commentaires` separator '; ') AS `commentaires` from (`tache` `t` left join `saisie_temps` `st` on((`t`.`idTache` = `st`.`idTache`))) group by `t`.`idTache`,`t`.`nomTache`,`t`.`idProjet` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-12-14  4:06:27
