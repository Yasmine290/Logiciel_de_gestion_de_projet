import sys
sys.path.append('backend')
from db import get_db_connection

# Vérifier si la table projet_employe existe
conn = get_db_connection()
cursor = conn.cursor()

print("\n=== VÉRIFICATION DES TABLES ===\n")

# Lister toutes les tables
cursor.execute("SHOW TABLES")
tables = cursor.fetchall()
print("Tables dans la base de données:")
for table in tables:
    print(f"  - {table[0]}")

# Vérifier spécifiquement projet_employe
cursor.execute("SHOW TABLES LIKE 'projet_employe'")
result = cursor.fetchone()

print(f"\n{'✅' if result else '❌'} Table projet_employe: {'EXISTE' if result else 'N\'EXISTE PAS'}")

# Si la table existe, afficher sa structure
if result:
    print("\nStructure de la table projet_employe:")
    cursor.execute("DESCRIBE projet_employe")
    columns = cursor.fetchall()
    for col in columns:
        print(f"  - {col[0]}: {col[1]}")
    
    # Compter les enregistrements
    cursor.execute("SELECT COUNT(*) FROM projet_employe")
    count = cursor.fetchone()[0]
    print(f"\nNombre d'assignations: {count}")

cursor.close()
conn.close()
