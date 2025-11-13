# Importation du module mysql.connector pour se connecter à une base MySQL
import mysql.connector

# Fonction pour obtenir une connexion à la base de données
# Cette fonction retourne un objet de connexion utilisable par le backend
def get_db_connection():
    conn = mysql.connector.connect(
        host='localhost',           # Adresse du serveur MySQL
        user='root',                # Nom d'utilisateur MySQL
        password='uqac2022',        # Mot de passe MySQL (à adapter selon la configuration)
        database='project_time_gestion' # Nom de la base de données utilisée
    )
    return conn                    # Retourne l'objet de connexion
