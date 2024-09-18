from sqlalchemy import (
    create_engine,
    Column,
    String,
    Float,
    Boolean,
    Time,
    JSON,
    DECIMAL,
    ForeignKey,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import uuid
import os
from dotenv import load_dotenv

load_dotenv()

# Database connection settings
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

# Define the base class
Base = declarative_base()


# Define the Restaurant model
class Restaurant(Base):
    __tablename__ = "restaurant"
    restaurant_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    address = Column(String(255))
    zipcode = Column(String(10))
    latitude = Column(Float)
    longitude = Column(Float)
    cuisine = Column(String(100))
    open_hours = Column(JSON)
    breakfast_start_time = Column(Time)
    breakfast_end_time = Column(Time)
    customizable = Column(Boolean, default=False)
    open_now = Column(Boolean)
    created_at = Column(String, default="CURRENT_TIMESTAMP")
    updated_at = Column(String, default="CURRENT_TIMESTAMP")


# Define the MenuItem model
class MenuItem(Base):
    __tablename__ = "menu_item"
    menu_item_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    restaurant_id = Column(
        UUID(as_uuid=True),
        ForeignKey("restaurant.restaurant_id", ondelete="CASCADE"),
        nullable=False,
    )
    name = Column(String(255), nullable=False)
    description = Column(String)
    price = Column(DECIMAL(10, 2))
    kcal = Column(Float, nullable=False)
    kcal_from_fat = Column(Float)
    grams_protein = Column(Float)
    grams_carbs = Column(Float)
    grams_dietary_fiber = Column(Float)
    grams_total_sugar = Column(Float)
    grams_added_sugar = Column(Float)
    grams_fat = Column(Float)
    grams_saturated_fat = Column(Float)
    grams_trans_fat = Column(Float)
    grams_monounsat_fat = Column(Float)
    grams_polyunsat_fat = Column(Float)
    mg_cholesterol = Column(Float)
    mg_sodium = Column(Float)
    ingredients = Column(String)
    allergens = Column(String)
    is_breakfast = Column(Boolean)
    is_dessert = Column(Boolean)
    is_side_condiment = Column(Boolean)
    is_add_on = Column(Boolean)
    is_vegetarian = Column(Boolean)
    contains_caffeine = Column(Boolean)
    contains_alcohol = Column(Boolean)
    contains_seafood = Column(Boolean)
    is_kids_meal = Column(Boolean)
    is_beverage = Column(Boolean)
    is_dairy_free = Column(Boolean)
    is_pescatarian = Column(Boolean)
    is_vegan = Column(Boolean)
    is_gluten_free = Column(Boolean)
    is_keto = Column(Boolean)
    created_at = Column(String, default="CURRENT_TIMESTAMP")
    updated_at = Column(String, default="CURRENT_TIMESTAMP")


# Define the MenuItemFilter model
class MenuItemFilter(Base):
    __tablename__ = "menu_item_filter"
    filter_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    menu_item_id = Column(
        UUID(as_uuid=True),
        ForeignKey("menu_item.menu_item_id", ondelete="CASCADE"),
        nullable=False,
    )
    filter_name = Column(String(100), nullable=False)
    filter_value = Column(Boolean, nullable=False)


# Define the ZipcodeGeolocation model
class ZipcodeGeolocation(Base):
    __tablename__ = "zipcode_geolocation"
    zipcode = Column(String(10), primary_key=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)


# Database URL
DATABASE_URL = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# Create an engine
engine = create_engine(DATABASE_URL)

# Create a session
Session = sessionmaker(bind=engine)
session = Session()


# Create tables in the database
def create_tables():
    print("this is the port: ", DB_PORT)
    try:
        Base.metadata.create_all(engine)
        print("Tables created successfully!")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    print("this is the port: ", DB_PORT)
    create_tables()
