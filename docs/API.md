# Documentation de l'API

Base URL : `http://127.0.0.1:5000/api`

## Authentification

### POST /register
Créer un nouveau compte utilisateur.

**Body (JSON) :**
```json
{
  "nomEmploye": "Dupont",
  "courrielEmploye": "jean.dupont@exemple.com",
  "motDePasse": "password123",
  "role": "Employe"
}
```

**Champs :**
- `nomEmploye` : Nom de l'employé (requis)
- `courrielEmploye` : Adresse email (requis, unique)
- `motDePasse` : Mot de passe (requis)
- `role` : Rôle de l'utilisateur (optionnel, défaut: "Employe")
  - Valeurs possibles : "Admin", "Gestionnaire", "Employe"

**Réponse (201) :**
```json
{
  "message": "Utilisateur inscrit avec succès"
}
```

**Notes :**
- Le département est défini par défaut à 1
- Le hash du mot de passe est automatique

### POST /login
Authentifier un utilisateur.

**Body (JSON) :**
```json
{
  "courrielEmploye": "test@gmail.com",
  "motDePasse": "123"
}
```

**Réponse (200) :**

**Erreurs :**
- 400 : Données manquantes
- 401 : Identifiants invalides

## Projets

### GET /projets
Récupérer la liste de tous les projets.

**Réponse (200) :**
```json
[
  {
    "idProjet": 1,
    "nomProjet": "Projet Démo",
    "dateDebut": "2025-12-01",
    "dateFin": "2026-01-30",
    "statutProjet": "En cours",
    "progressionProjet": 62.5,
    "idClient": 1,
    "idEmploye": 2
  }
]
```

**Notes :**
- Détection automatique des projets "En retard" avant renvoi
- Champ `progressionProjet` calculé dynamiquement


### GET /projets/:id
Récupérer les détails d'un projet spécifique.

**Paramètres URL :**
- `id` : ID du projet


**Erreurs :**
- 404 : Projet non trouvé

### POST /projets
Créer un nouveau projet.

**Body (JSON) - Champs de base :**
```json
{
  "nomProjet": "Nouveau Projet",
  "dateDebut": "2025-12-10",
  "dateFin": "2026-03-15",
  "statutProjet": "À faire",
  "idClient": 1,
  "idEmploye": 2
}
```

**Champs requis :**
- `nomProjet` : Nom du projet
- `dateDebut` : Date de début
- `idEmploye` : ID du gestionnaire responsable

**Champs optionnels :**
- `dateFin` : Date de fin prévue
- `statutProjet` : Statut (défaut: "À faire")
- `descriptionProjet` : Description
- `heuresBudget` : Budget en heures (défaut: 0)
- `coutsProjet` : Coûts (défaut: 0)
- `idClient` : ID du client
- `idTemplateProjet` : ID du template utilisé

**Réponse (201) :**
```json
{
  "message": "Projet ajouté avec succès",
  "idProjet": 7
}
```

**Erreurs :**
- 400 : Données manquantes
- 500 : Erreur serveur

### PUT /projets/:id
Mettre à jour un projet existant.

**Paramètres URL :**
- `id` : ID du projet



**Réponse (200) :**
```json
{
  "message": "Projet mis à jour avec succès"
}
```

**Notes :**
- Recalcul automatique de la progression après mise à jour

**Erreurs :**
- 404 : Projet non trouvé

### DELETE /projets/:id
Supprimer un projet et toutes ses données associées.

**Paramètres URL :**
- `id` : ID du projet

**Réponse (200) :**
```json
{
  "message": "Projet supprimé avec succès"
}
```

**Notes :**
- Suppression en cascade : toutes les tâches, affectations, heures sont supprimées
- Opération irréversible

**Erreurs :**
- 404 : Projet non trouvé

### GET /projets/:idProjet/membres
Récupérer les membres assignés à un projet.

**Paramètres URL :**
- `idProjet` : ID du projet

**Réponse (200) :**
```json
[
  {
    "idEmploye": 1,
    "nomEmploye": "Admin",
    "prenomEmploye": "Alpha",
    "courrielEmploye": "alpha.admin@exemple.com"
  },
  {
    "idEmploye": 2,
    "nomEmploye": "Gestion",
    "prenomEmploye": "Beta",
    "courrielEmploye": "beta.gestion@exemple.com"
  }
]
```

### POST /projets/:idProjet/membres
Assigner des membres à un projet.

**Paramètres URL :**
- `idProjet` : ID du projet

**Body (JSON) :**
```json
{
  "membres": [1, 2, 3]
}
```

**Réponse (200) :**
```json
{
  "message": "Membres assignés avec succès"
}
```

**Notes :**
- Remplace complètement la liste des membres existants

## Tâches

### GET /taches/:idProjet
Récupérer toutes les tâches d'un projet (structure hiérarchique incluse).

**Paramètres URL :**
- `idProjet` : ID du projet

**Réponse (200) :**
```json
[
  {
    "idTache": 1,
    "idProjet": 1,
    "idTacheParent": null,
    "titreTache": "Tâche principale",
    "descriptionTache": "Description",
    "statutTache": "En cours",
    "prioriteTache": "Haute",
    "dateDebutTache": "2025-12-01",
    "dateFinTache": "2025-12-15",
    "heuresEstimees": 40,
    "progressionTache": 50.0
  },
  {
    "idTache": 2,
    "idProjet": 1,
    "idTacheParent": 1,
    "titreTache": "Sous-tâche",
    "descriptionTache": "Description",
    "statutTache": "Terminée",
    "prioriteTache": "Moyenne",
    "dateDebutTache": "2025-12-01",
    "dateFinTache": "2025-12-10",
    "heuresEstimees": 20,
    "progressionTache": 100.0
  }
]
```

**Notes :**
- Détection automatique des tâches "En retard" avant renvoi
- Calcul récursif de la progression pour chaque tâche
- La hiérarchie est représentée par `idTacheParent`

### POST /taches
Créer une nouvelle tâche ou sous-tâche.

**Body (JSON) :**
```json
{
  "idProjet": 1,
  "idTacheParent": null,
  "titreTache": "Nouvelle tâche",
  "descriptionTache": "Description détaillée",
  "statutTache": "À faire",
  "prioriteTache": "Moyenne",
  "dateDebutTache": "2025-12-10",
  "dateFinTache": "2025-12-20",
  "heuresEstimees": 15,
  "membres": [2, 3]
}
```

**Réponse (201) :**
```json
{
  "message": "Tâche créée avec succès",
  "idTache": 10
}
```

**Notes :**
- `idTacheParent` : null pour une tâche principale, ID pour une sous-tâche
- `membres` (optionnel) : Liste des IDs d'employés à assigner
- Validation automatique des dates par rapport au projet et à la tâche parent
- Mise à jour automatique du statut et progression du projet

**Erreurs :**
- 400 : Dates invalides ou hors limites du projet/parent

### PUT /taches/:idTache
Mettre à jour une tâche existante.

**Paramètres URL :**
- `idTache` : ID de la tâche

**Body (JSON) :**
```json
{
  "titreTache": "Tâche modifiée",
  "descriptionTache": "Nouvelle description",
  "statutTache": "En cours",
  "prioriteTache": "Haute",
  "dateDebutTache": "2025-12-10",
  "dateFinTache": "2025-12-22",
  "heuresEstimees": 20
}
```

**Réponse (200) :**
```json
{
  "message": "Tâche mise à jour avec succès"
}
```

**Notes :**
- Validation automatique des dates
- Recalcul récursif de la progression (tâche, parents, projet)
- Mise à jour automatique du statut des tâches parentes

**Erreurs :**
- 404 : Tâche non trouvée
- 400 : Dates invalides

### DELETE /taches/:idTache
Supprimer une tâche et toutes ses sous-tâches (récursif).

**Paramètres URL :**
- `idTache` : ID de la tâche

**Réponse (200) :**
```json
{
  "message": "Tâche supprimée avec succès"
}
```

**Notes :**
- Suppression récursive de TOUTES les sous-tâches (tous niveaux)
- Suppression automatique : affectations, dépendances, saisies de temps
- Mise à jour automatique du statut et progression du projet

**Erreurs :**
- 404 : Tâche non trouvée

### GET /taches/:idTache/membres
Récupérer les membres assignés à une tâche.

**Paramètres URL :**
- `idTache` : ID de la tâche

**Réponse (200) :**
```json
[
  {
    "idEmploye": 2,
    "nomEmploye": "Gestion",
    "prenomEmploye": "Beta",
    "courrielEmploye": "beta.gestion@exemple.com",
    "tauxHoraire": 75.00,
    "roleSurLaTache": "Responsable"
  }
]
```

### POST /taches/:idTache/membres
Assigner des membres à une tâche.

**Paramètres URL :**
- `idTache` : ID de la tâche

**Body (JSON) :**
```json
{
  "membres": [2, 3]
}
```

**Réponse (200) :**
```json
{
  "message": "Membres assignés avec succès"
}
```

**Notes :**
- Remplace complètement la liste des membres existants

### GET /taches/:idTache/progression
Récupérer la progression détaillée d'une tâche (incluant sous-tâches).

**Paramètres URL :**
- `idTache` : ID de la tâche

**Réponse (200) :**
```json
{
  "idTache": 1,
  "titreTache": "Tâche principale",
  "progressionTache": 62.5,
  "heuresEstimees": 40,
  "heuresTravaillees": 25,
  "statutTache": "En cours"
}
```

### GET /projets/:idProjet/progression
Récupérer la progression globale d'un projet.

**Paramètres URL :**
- `idProjet` : ID du projet

**Réponse (200) :**
```json
{
  "idProjet": 1,
  "nomProjet": "Projet Démo",
  "progressionProjet": 62.5,
  "totalTaches": 16,
  "tachesTerminees": 9,
  "tachesEnCours": 6,
  "heuresBudget": 200,
  "heuresTravaillees": 125
}
```

### POST /projets/:idProjet/recalculer
Forcer le recalcul de la progression et des statuts d'un projet.

**Paramètres URL :**
- `idProjet` : ID du projet

**Réponse (200) :**
```json
{
  "message": "Progression recalculée avec succès",
  "progressionProjet": 62.5
}
```

**Notes :**
- Recalcule récursivement toutes les tâches et sous-tâches
- Met à jour tous les statuts selon la logique métier

## Employés

### GET /employes
Récupérer la liste de tous les employés.

**Réponse (200) :**
```json
[
  {
    "idEmploye": 1,
    "nomEmploye": "Admin",
    "prenomEmploye": "Alpha",
    "courrielEmploye": "alpha.admin@exemple.com",
    "telephoneEmploye": "000-000-0000",
    "idRole": 1,
    "nomRole": "Admin",
    "idDepartement": 1,
    "nomDepartement": "Informatique"
  }
]
```

### DELETE /employes/:idEmploye
Supprimer un employé.

**Paramètres URL :**
- `idEmploye` : ID de l'employé

**Réponse (200) :**
```json
{
  "message": "Employé supprimé avec succès"
}
```

**Permissions :**
- Administrateurs uniquement (idRole = 1)
- Les gestionnaires ne peuvent pas supprimer d'employés

**Erreurs :**
- 403 : Permission refusée
- 404 : Employé non trouvé

### GET /employes/:idEmploye/projets
Récupérer les projets assignés à un employé.

**Paramètres URL :**
- `idEmploye` : ID de l'employé

**Réponse (200) :**
```json
[
  {
    "idProjet": 1,
    "nomProjet": "Projet Démo",
    "dateDebut": "2025-12-01",
    "dateFin": "2026-01-30",
    "statutProjet": "En cours",
    "progressionProjet": 62.5
  }
]
```

### GET /employes/:idEmploye/taches
Récupérer les tâches assignées à un employé.

**Paramètres URL :**
- `idEmploye` : ID de l'employé

**Réponse (200) :**
```json
[
  {
    "idTache": 2,
    "titreTache": "Développement",
    "descriptionTache": "Implémentation",
    "statutTache": "En cours",
    "prioriteTache": "Haute",
    "dateDebutTache": "2025-12-07",
    "dateFinTache": "2025-12-18",
    "heuresEstimees": 120,
    "idProjet": 1,
    "nomProjet": "Projet Démo"
  }
]
```

## Temps de travail

### GET /temps
Récupérer toutes les saisies de temps.

**Paramètres query (optionnels) :**
- `idEmploye` : Filtrer par employé
- `idTache` : Filtrer par tâche
- `dateDebut` : Date de début (YYYY-MM-DD)
- `dateFin` : Date de fin (YYYY-MM-DD)

**Exemple :**
```
GET /temps?idEmploye=3&dateDebut=2025-12-01&dateFin=2025-12-31
```

**Réponse (200) :**
```json
[
  {
    "idSaisie": 1,
    "idEmploye": 3,
    "nomEmploye": "Employe",
    "prenomEmploye": "Gamma",
    "idTache": 2,
    "titreTache": "Développement",
    "idProjet": 1,
    "nomProjet": "Projet Démo",
    "dateTravail": "2025-12-02",
    "heures": 3.5,
    "commentaires": "Setup projet"
  }
]
```

### POST /temps
Saisir des heures de travail.

**Body (JSON) :**
```json
{
  "idEmploye": 3,
  "idTache": 2,
  "dateTravail": "2025-12-04",
  "heures": 6.5,
  "commentaires": "Développement API"
}
```

**Réponse (201) :**
```json
{
  "message": "Temps saisi avec succès",
  "idSaisie": 15
}
```

**Notes :**
- Les heures doivent être > 0
- La date ne peut pas être dans le futur

**Erreurs :**
- 400 : Données manquantes ou invalides
- 404 : Tâche ou employé non trouvé

## Pages frontend

Les routes suivantes renvoient les pages HTML de l'application :

- GET `/` : Redirection vers /login
- GET `/login` : Page de connexion
- GET `/projects` : Liste des projets
- GET `/time` : Saisie des temps
- GET `/gantt` : Diagramme de Gantt
- GET `/users` : Gestion des utilisateurs (Admin)
- GET `/project_details` : Détails d'un projet
- GET `/assets/<path>` : Fichiers statiques (CSS, JS, images)

## Codes de statut HTTP

- **200** : Succès (GET, PUT, DELETE)
- **201** : Créé avec succès (POST)
- **400** : Requête invalide (données manquantes ou incorrectes)
- **401** : Non authentifié
- **403** : Permission refusée
- **404** : Ressource non trouvée
- **409** : Conflit (ex: email déjà utilisé)
- **500** : Erreur serveur interne

## Fonctionnalités automatiques

### Détection des retards
Avant chaque requête GET sur les projets/tâches :
- Vérification automatique des dates d'échéance
- Mise à jour du statut "En retard" si nécessaire

### Calcul de progression
La progression est calculée automatiquement :
- Formule pondérée : `Σ(progression × heures) / Σ(heures)`
- Prise en compte de toutes les sous-tâches (récursif)
- Maximum entre progression par heures et par statut

### Mise à jour hiérarchique
Lors de la modification d'une tâche :
- Recalcul de la progression de toutes les tâches parentes
- Mise à jour du statut des tâches parentes
- Mise à jour du statut et progression du projet

### Validation des dates
Validation automatique lors de la création/modification :
- dateDebut <= dateFin
- Dates des sous-tâches dans l'intervalle du parent
- Dates des tâches dans l'intervalle du projet

## Notes techniques

- Format des dates : `YYYY-MM-DD` (ISO 8601)
- Format des nombres décimaux : JSON standard (ex: 62.5)
- Encodage : UTF-8
- Content-Type : `application/json`
- CORS : Activé pour le développement local
