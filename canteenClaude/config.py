import os
from dotenv import load_dotenv
 
load_dotenv()
 
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
 
 
class Config:
    #   SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-secret-key"
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or (
        "sqlite:///" + os.path.join(BASE_DIR, "instance","club33.db")
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
 
 
class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = False  # Set True to log SQL statements
 
 
class ProductionConfig(Config):
    DEBUG = False
 
 
class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
 
 
config_map = {
    "development": DevelopmentConfig,
    "production":  ProductionConfig,
    "testing":     TestingConfig,
    "default":     DevelopmentConfig,
}
 