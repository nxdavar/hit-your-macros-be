from db.models.base import Base
from db.utils.db_session import get_db_port, get_engine


# Create tables in the database
def create_tables():
    engine = get_engine()
    print("this is the port: ", get_db_port())
    try:
        Base.metadata.create_all(engine)
        print("Tables created successfully!")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    print("this is the port: ", get_db_port())
    create_tables()
