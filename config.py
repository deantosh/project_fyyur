import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Database parameters
DATABASE_NAME = "fyyur"
username = "postgres"
password = "root"
url = "localhost:5432"

# Create a database connection
SQLALCHEMY_DATABASE_URI = "postgresql://{}:{}@{}/{}".format(
    username,
    password,
    url,
    DATABASE_NAME
)

# Reduce significant overhead
SQLALCHEMY_TRACK_MODIFICATIONS = False