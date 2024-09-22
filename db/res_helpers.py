# external imports:
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, Table, MetaData
from dotenv import load_dotenv
import os


load_dotenv()
engine = create_engine(os.getenv("DATABASE_URL"))
metadata = MetaData()


restaurant_table = Table("restaurant", metadata, autoload_with=engine)


# Function to get restaurant_id based on restaurant name
def get_restaurant_id(res_name):
    with Session(engine) as session:
        stmt = select(restaurant_table.c.restaurant_id).where(
            restaurant_table.c.name == res_name
        )
        result = session.execute(stmt).scalar()
        return result
