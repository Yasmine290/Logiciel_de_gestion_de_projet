import mysql.connector
import os
from mysql.connector import pooling
from typing import Optional


class DatabaseConnection:
    _instance = None
    _connection_pool = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._connection_pool is None:
            self._initialize_pool()
    
    def _initialize_pool(self):
        """Initialise le pool de connexions"""
        try:
            self._connection_pool = pooling.MySQLConnectionPool(
                pool_name="mypool",
                pool_size=10,
                pool_reset_session=True,
                host=os.getenv('DB_HOST', 'localhost'),
                database=os.getenv('DB_NAME', 'gestion_projet'),
                user=os.getenv('DB_USER', 'root'),
                password=os.getenv('DB_PASSWORD', ''),
                port=int(os.getenv('DB_PORT', 3306)),
                autocommit=False
            )
            print("Pool de connexions MySQL créé avec succès")
        except mysql.connector.Error as err:
            print(f"Erreur lors de la création du pool: {err}")
            raise
    
    def get_connection(self):
        """Obtient une connexion du pool"""
        try:
            return self._connection_pool.get_connection()
        except mysql.connector.Error as err:
            print(f"Erreur lors de l'obtention d'une connexion: {err}")
            raise
    
    def close_all(self):
        """Ferme toutes les connexions du pool"""
        if self._connection_pool:
            self._connection_pool._remove_connections()
            print("Toutes les connexions fermées")
