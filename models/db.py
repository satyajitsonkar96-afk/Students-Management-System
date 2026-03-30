import mysql.connector           # Import the MySQL Connector library to interact with MySQL databases
from config import Config        # Import the Config class from the local config module to access database settings

def get_db_connection():         # Define a function that returns a new database connection object
    return mysql.connector.connect(**Config.DB_CONFIG)   # Create and return a MySQL connection using the DB_CONFIG dictionary unpacked as keyword arguments