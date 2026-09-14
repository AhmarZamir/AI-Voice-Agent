import uuid
from sqlalchemy import Boolean, Column, Date, DateTime, String
from sqlalchemy.sql import func

from .database import Base


class Patient(Base):
    __tablename__ = "patients"

    patient_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    sex = Column(String(30), nullable=False)
    phone_number = Column(String(13), nullable=False, index=True)
    email = Column(String(255), nullable=True)
    address_line_1 = Column(String(255), nullable=False)
    address_line_2 = Column(String(255), nullable=True)
    city = Column(String(100), nullable=False)
    state = Column(String(50), nullable=False)
    zip_code = Column(String(20), nullable=False)
    insurance_provider = Column(String(150), nullable=True)
    insurance_member_id = Column(String(100), nullable=True)
    preferred_language = Column(String(50), default="English")
    emergency_contact_name = Column(String(100), nullable=True)
    emergency_contact_phone = Column(String(13), nullable=True)
    deleted = Column(Boolean, default=False, nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
