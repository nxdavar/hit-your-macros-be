# external imports:
import uuid

from sqlalchemy import Boolean, Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID

# internal imports:
from db.models.base import Base


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
