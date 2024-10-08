# external imports:
from sqlalchemy import create_engine, Table, MetaData, select, Column, Integer, String
from sqlalchemy.orm import Session, sessionmaker
from dotenv import load_dotenv
import os
from urllib.parse import urlparse, parse_qs

# internal imports:
from db.models.restaurant import Restaurant

load_dotenv()

# Parse the DATABASE_URL
url = urlparse(os.getenv("DATABASE_URL"))
query = parse_qs(url.query)

# Construct a new connection string
connection_string = f"postgresql://{url.username}:{url.password}@{url.hostname}:{url.port}/{url.path[1:]}"

# Add SSL mode if not present
if "sslmode" not in query:
    connection_string += "?sslmode=require"

# Create the engine with the correct parameters
engine = create_engine(
    connection_string, pool_pre_ping=True, pool_size=10, max_overflow=20
)

# Create a sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Use declarative base instead of reflection
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


# Define your Restaurant model (if not already defined elsewhere)
class Restaurant(Base):
    __tablename__ = "restaurant"
    restaurant_id = Column(Integer, primary_key=True)
    name = Column(String)


# The rest of your functions remain largely the same, but use SessionLocal


def get_restaurant_id_one(res_name: str):
    with SessionLocal() as session:
        result = (
            session.query(Restaurant.restaurant_id)
            .filter(Restaurant.name == res_name)
            .scalar()
        )
    return result


def add_new_restaurant(res_name: str):
    with SessionLocal() as session:
        new_restaurant = Restaurant(name=res_name)
        session.add(new_restaurant)
        session.commit()
        session.refresh(new_restaurant)
    return new_restaurant


def get_restaurant_id(res_name):
    with SessionLocal() as session:
        stmt = select(Restaurant.restaurant_id).where(Restaurant.name == res_name)
        result = session.execute(stmt).scalar()
    return result
