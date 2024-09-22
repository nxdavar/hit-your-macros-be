# external imports:
from sqlalchemy import (
    Column,
    String,
    Float,
)

# internal imports:
from db.models.base import Base


class ZipcodeGeolocation(Base):
    __tablename__ = "zipcode_geolocation"
    zipcode = Column(String(10), primary_key=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
