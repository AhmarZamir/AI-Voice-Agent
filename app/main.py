import logging
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, Query, status
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import Base, engine, get_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("voice-patient-agent")

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Voice Patient Registration API",
    version="1.0.0",
    description="Backend API for a voice-based patient registration agent with Pakistani phone number support.",
)


@app.get("/")
def root():
    return {"message": "AI Voice Patient Registration API is running"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/patients", response_model=schemas.PatientResponse, status_code=status.HTTP_201_CREATED)
def create_patient(patient: schemas.PatientCreate, db: Session = Depends(get_db)):
    existing = (
        db.query(models.Patient)
        .filter(
            models.Patient.phone_number == patient.phone_number,
            models.Patient.deleted.is_(False),
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "message": "A patient with this phone number already exists.",
                "patient_id": existing.patient_id,
                "patient_name": f"{existing.first_name} {existing.last_name}",
            },
        )

    logger.info("Creating patient registration for phone ending in %s", patient.phone_number[-4:])
    return crud.create_patient(db, patient)


@app.get("/patients", response_model=list[schemas.PatientResponse])
def get_patients(
    last_name: Optional[str] = Query(default=None),
    phone_number: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
):
    try:
        return crud.list_patients(db, last_name=last_name, phone_number=phone_number)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.get("/patients/{patient_id}", response_model=schemas.PatientResponse)
def get_patient(patient_id: str, db: Session = Depends(get_db)):
    patient = crud.get_patient(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


@app.put("/patients/{patient_id}", response_model=schemas.PatientResponse)
def update_patient(
    patient_id: str,
    changes: schemas.PatientUpdate,
    db: Session = Depends(get_db),
):
    patient = crud.get_patient(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return crud.update_patient(db, patient, changes)


@app.delete("/patients/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_patient(patient_id: str, db: Session = Depends(get_db)):
    patient = crud.get_patient(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    crud.soft_delete_patient(db, patient)
    return None
