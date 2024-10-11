# external imports:
import os
from urllib.parse import parse_qs, urlencode, urlparse

from dotenv import load_dotenv
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

# internal imports:
from db.models.restaurant import Restaurant

load_dotenv()

# Parse the DATABASE_URL
url = urlparse(os.getenv("DATABASE_URL", ""))
query = dict(parse_qs(url.query)) if url.query else {}

# Construct a new connection string
connection_string = f"postgresql://{url.username or ''}:{url.password or ''}@{url.hostname or ''}:{url.port or ''}/"
if url.path:
    connection_string += url.path[1:]

# Add SSL mode if not present
if "sslmode" not in query:
    query["sslmode"] = ["require"]

if query:
    connection_string += f"?{urlencode(query, doseq=True)}"

# Create the engine with the correct parameters
engine = create_engine(
    connection_string, pool_pre_ping=True, pool_size=10, max_overflow=20
)

# Create a sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


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
