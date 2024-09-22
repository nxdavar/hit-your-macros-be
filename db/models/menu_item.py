# external imports:
from sqlalchemy import (
    Column,
    String,
    Float,
    Boolean,
    DECIMAL,
    ForeignKey,
)
from sqlalchemy.dialects.postgresql import UUID
import uuid


# internal imports:
from db.models.base import Base


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
    grams_total_fat = Column(Float)
    grams_saturated_fat = Column(Float)
    grams_trans_fat = Column(Float)
    grams_monounsat_fat = Column(Float)
    grams_polyunsat_fat = Column(Float)
    mg_cholesterol = Column(Float)
    mg_sodium = Column(Float)
    mg_calcium = Column(Float)
    mg_potassium = Column(Float)
    mg_iron = Column(Float)
    mcg_vitamin_a = Column(Float)
    mg_vitamin_c = Column(Float)
    serving_size_oz = Column(Float)
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
