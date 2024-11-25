from sqlalchemy import Column, Integer, String, Date, DateTime, Boolean, ForeignKey
from db.database import Base
from sqlalchemy.orm import relationship
from datetime import datetime
import datetime

from db.db_models import User

class RefreshToken(Base):
    __tablename__ = "refresh_token"
    id = Column(Integer, primary_key=True, index=True)
    employment_id = Column(Integer, ForeignKey(User.id))
    access_token = Column(String(450), nullable=False)
    refresh_token = Column(String(450), nullable=False)
    status = Column(Boolean)
    created_date = Column(DateTime, default=datetime.datetime.now)

