from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
import dotenv

dotenv.load_dotenv()

# Load environment variables
DATABASE_USER = os.getenv("TRADING_POSTGRES_USER")
DATABASE_PASSWORD = os.getenv("TRADING_POSTGRES_PASSWORD")
DATABASE_HOST = os.getenv("TRADING_POSTGRES_HOST")
DATABASE_PORT = os.getenv("TRADING_POSTGRES_PORT")
DATABASE_DB = os.getenv("TRADING_POSTGRES_DB")

# # DEV
# DATABASE_HOST = 'localhost'
# DATABASE_PORT = '5434'

DATABASE_URL = f"postgresql+psycopg2://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_DB}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)