#  Gestionnaire de Projets et Temps

Application web de gestion de projets avec suivi du temps, diagramme de Gantt et gestion d'équipes.

##  Installation

### Prérequis
- Python 3.8+
- MySQL 8.0+
- Navigateur (Chrome, Firefox, Edge)

### Installation rapide

1. **Installer les dépendances Python**
```bash
python -m pip install -r requirements.txt
```

2. **Importer la base de données complète**

**MÉTHODE 1 : Ligne de commande (simple et rapide)**
```bash
mysql -u root -p < database/export_complet.sql
```

**MÉTHODE 2 : phpMyAdmin** (si problème avec la méthode 1)
```
1. Ouvrir phpMyAdmin dans votre navigateur
2. Cliquer sur "Importer" en haut
3. Sélectionner le fichier database/export_complet.sql
4. Cliquer sur "Exécuter"
```

**MÉTHODE 3 : MySQL Workbench**
```
1. Ouvrir MySQL Workbench
2. Connectez-vous à votre serveur MySQL
3. Server → Data Import
4. Sélectionner "Import from Self-Contained File"
5. Choisir database/export_complet.sql
6. Cliquer sur "Start Import"
```

> **Note importante** : Le fichier `export_complet.sql` contient la structure complète de la base de données ET toutes les données de démonstration (employés, projets, tâches, temps saisis). Il créera automatiquement la base `project_time_gestion`.

3. **Configurer la connexion à la base de données**

Éditer le fichier `backend/db.py` et ajuster le mot de passe MySQL :
```python
def get_db_connection():
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='VOTRE_MOT_DE_PASSE',  # ← Modifier ici
        database='project_time_gestion'
    )
    return conn
```

4. **Démarrer le serveur**
```bash
cd backend
python app.py
```

Le serveur démarre sur `http://127.0.0.1:5000`

5. **Accéder à l'application**
```
http://127.0.0.1:5000/login
```

##  Structure du projet

```
gestionnaire_projet_temps/
├── backend/          # API Flask
├── Frontend/         # Interface utilisateur
├── database/         # Scripts SQL
└── scripts/          # Utilitaires
```

##  Comptes disponibles

Après l'importation de la base de données, vous pouvez vous connecter avec les comptes existants.

**Note** : Les mots de passe sont hachés avec Werkzeug (Python). Si vous souhaitez créer de nouveaux utilisateurs ou réinitialiser les mots de passe, utilisez l'interface d'administration ou créez un script Python avec :
```python
from werkzeug.security import generate_password_hash
password_hash = generate_password_hash('votre_mot_de_passe')
```

Comptes actuellement dans la base de données :
- **quewel@gmail.com** - Employé  **mot de passe**:123 
- **yas@gmail.com** - Admin  **mot de passe**:123 
- **mo@gmail.com** - Employé  **mot de passe**:123 
- **sam@gmail.com** - Gestionnaire  **mot de passe**:123 
- **cath@gmail.com** - Gestionnaire  **mot de passe**:123 
- **test@gmail.com** - Admin  **mot de passe**:1234 

##  Fonctionnalités

-  Gestion de projets et tâches
-  Diagramme de Gantt interactif
-  Suivi du temps de travail
-  Calcul automatique de progression
-  Assignation d'équipes
-  Gestion des utilisateurs (Admin)
-  Statistiques en temps réel

##  Technologies

- **Backend** : Flask (Python)
- **Frontend** : HTML, CSS, JavaScript (Vanilla)
- **Base de données** : MySQL
- **Style** : CSS personnalisé + Font Awesome

##  Configuration

### Connexion à la base de données

Le fichier `backend/db.py` contient les paramètres de connexion :
```python
def get_db_connection():
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='*****',  # ← Modifier selon votre configuration
        database='project_time_gestion'
    )
    return conn
```

### Dépendances Python

Le fichier `requirements.txt` contient :
```
Flask==3.0.0
flask-cors==4.0.0
mysql-connector-python==8.2.0
Werkzeug==3.0.1
```

##  Documentation

Voir le dossier `docs/` pour plus de détails :
- **`SCHEMA_BDD.md`** : Structure complète de la base de données (19 tables)
- **`API.md`** : Documentation détaillée des endpoints REST 
- **`schema_database.png`** : Diagramme visuel de l'architecture de la base de données

##  Fichiers de base de données

- **`export_complet.sql`** : Export complet avec structure + données actuelles (**UTILISEZ CELUI-CI**)
- **`BD_projet.sql`** : Structure de base seule (sans données)
- **`setup_complet_avec_donnees.sql`** : Script avec données de démonstration fictives
- **`add_projet_employe_table.sql`** : Script de migration pour la table projet_employe



