import os                     # Import the os module to interact with environment variables

class Config:                 # Define a configuration class to hold app settings
    SECRET_KEY = "supersecret123"   # Set a static secret key for session signing and security (hardcoded for dev)

    DB_CONFIG = {             # Define a dictionary containing database connection parameters
        "host": os.getenv("DB_HOST"),        # Get database host from environment variable DB_HOST
        "user": os.getenv("DB_USER"),        # Get database username from environment variable DB_USER
        "password": os.getenv("DB_PASSWORD"),# Get database password from environment variable DB_PASSWORD
        "database": os.getenv("DB_NAME"),    # Get database name from environment variable DB_NAME
        "port": 3306                         # Set fixed MySQL default port (3306)
    }