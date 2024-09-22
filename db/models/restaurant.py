# external imports:
from sqlalchemy import (
    Column,
    String,
    Float,
    Boolean,
    Time,
    JSON,
)
from sqlalchemy.dialects.postgresql import UUID
import uuid

# internal imports:
from db.models.base import Base


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
