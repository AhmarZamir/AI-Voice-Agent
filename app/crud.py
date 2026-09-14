from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from . import models, schemas


def create_patient(db: Session, patient: schemas.PatientCreate):
    db_patient = models.Patient(**patient.model_dump())
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient


def list_patients(
    db: Session,
    last_name: Optional[str] = None,
    phone_number: Optional[str] = None,
):
    query = db.query(models.Patient).filter(models.Patient.deleted.is_(False))
    if last_name:
        query = query.filter(models.Patient.last_name.ilike(last_name))
    if phone_number:
        phone_number = schemas.normalize_pk_phone(phone_number)
        query = query.filter(models.Patient.phone_number == phone_number)
    return query.all()


def get_patient(db: Session, patient_id: str):
    return (
        db.query(models.Patient)
        .filter(
            models.Patient.patient_id == patient_id,
            models.Patient.deleted.is_(False),
        )
        .first()
    )


def update_patient(db: Session, patient: models.Patient, changes: schemas.PatientUpdate):
    for field, value in changes.model_dump(exclude_unset=True).items():
        setattr(patient, field, value)
    db.commit()
    db.refresh(patient)
    return patient


def soft_delete_patient(db: Session, patient: models.Patient):
    patient.deleted = True
    patient.deleted_at = datetime.now(timezone.utc)
    db.commit()
