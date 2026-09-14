import re
from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator

PAKISTAN_MOBILE_RE = re.compile(r"^(?:\+92|92|0)?3\d{9}$")


def normalize_pk_phone(value: str) -> str:
    digits = re.sub(r"\D", "", value)
    if digits.startswith("92"):
        digits = digits[2:]
    elif digits.startswith("0"):
        digits = digits[1:]
    if not re.fullmatch(r"3\d{9}", digits):
        raise ValueError("Enter a valid Pakistani mobile number, e.g. 03001234567 or +923001234567.")
    return f"+92{digits}"


class PatientBase(BaseModel):
    first_name: str
    last_name: str
    date_of_birth: date
    sex: str
    phone_number: str
    email: Optional[EmailStr] = None
    address_line_1: str
    address_line_2: Optional[str] = None
    city: str
    state: str
    zip_code: str
    insurance_provider: Optional[str] = None
    insurance_member_id: Optional[str] = None
    preferred_language: Optional[str] = "English"
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        value = value.strip()
        if not 1 <= len(value) <= 50:
            raise ValueError("Name must be between 1 and 50 characters.")
        if not re.fullmatch(r"[A-Za-zÀ-ÿ' -]+", value):
            raise ValueError("Name can contain letters, spaces, hyphens and apostrophes only.")
        return value

    @field_validator("date_of_birth")
    @classmethod
    def validate_dob(cls, value: date) -> date:
        if value > date.today():
            raise ValueError("Date of birth cannot be in the future.")
        return value

    @field_validator("phone_number")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        return normalize_pk_phone(value)

    @field_validator("emergency_contact_phone")
    @classmethod
    def validate_emergency_phone(cls, value: Optional[str]) -> Optional[str]:
        return normalize_pk_phone(value) if value else value


class PatientCreate(PatientBase):
    pass


class PatientUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    sex: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None
    address_line_1: Optional[str] = None
    address_line_2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    insurance_provider: Optional[str] = None
    insurance_member_id: Optional[str] = None
    preferred_language: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None

    @field_validator("phone_number", "emergency_contact_phone")
    @classmethod
    def validate_optional_phone(cls, value: Optional[str]) -> Optional[str]:
        return normalize_pk_phone(value) if value else value

    @field_validator("date_of_birth")
    @classmethod
    def validate_optional_dob(cls, value: Optional[date]) -> Optional[date]:
        if value and value > date.today():
            raise ValueError("Date of birth cannot be in the future.")
        return value


class PatientResponse(PatientBase):
    patient_id: str
    model_config = ConfigDict(from_attributes=True)
