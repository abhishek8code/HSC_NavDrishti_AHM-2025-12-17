from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

MYSQL_USER = os.getenv('MYSQL_USER', 'root')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'password')
MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
MYSQL_DB = os.getenv('MYSQL_DB', 'navdrishti')

# Allow overriding full DATABASE_URL via env var for flexibility
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
	DATABASE_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}"

# Try to create engine for MySQL; if connection/auth fails, fall back to SQLite for local dev
def _create_engine_with_fallback():
	try:
		engine = create_engine(DATABASE_URL, echo=True)
		# Test connection
		with engine.connect() as conn:
			pass
		return engine
	except Exception as e:
		# Fallback to SQLite file for local development
		fallback_url = os.getenv('SQLALCHEMY_SQLITE_URL', 'sqlite:///./dev_navdrishti.db')
		print(f"WARNING: Could not connect to primary DB ({e}). Falling back to SQLite at {fallback_url}")
		engine = create_engine(fallback_url, echo=True)
		return engine

engine = _create_engine_with_fallback()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
