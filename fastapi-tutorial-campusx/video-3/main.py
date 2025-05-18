from fastapi import FastAPI, Path, HTTPException, Query
from pydantic import BaseModel
from enum import Enum
import json

app = FastAPI()

def load_data():
    with open("patients.json", "r") as f:
        data = json.load(f)
    return data

def save_data(data):
    with open("patients.json", "w") as f:
        json.dump(data, f, indent=4)

@app.get("/")
def hello():
    return {"message": "Patient Management System API"}

@app.get("/about")
def about():
    return {"message": "This is a simple API for managing patient data."}

@app.get("/view")
def view(sort_by: str = Query(None, description="Sort on the basis of height, weight or bmi", example="height"), order: str = Query("asc", description="Order of sorting", example="asc")):
    valid_fields = ["height", "weight", "bmi"]

    if sort_by not in valid_fields:
        raise HTTPException(status_code=400, detail="Invalid field, select from {valid_fields}")
    if order not in ["asc", "desc"]:
        raise HTTPException(status_code=400, detail="Invalid order, select from either asc or desc")
    
    data = load_data()

    sort_order = True if order == "desc" else False
    sorted_data = sorted(data.values(), key=lambda x: x.get(sort_by, 0), reverse=sort_order)

    return sorted_data

@app.get("/patient/{patient_id}")
def get_patient(patient_id: str = Path(..., description="The ID of the patient", example="P001")):
    data = load_data()
    if patient_id in data:
        return data[patient_id]
    raise HTTPException(status_code=404, detail="Patient not found")

class genderEnum(str, Enum):
    male = "male"
    female = "female"

class verdictEnum(str, Enum):
    obese = "obese"
    overweight = "overweight"
    underweight = "underweight"
    normal = "normal"
class PatientModel(BaseModel):
    name: str
    city: str
    age: int
    gender: genderEnum
    height: float
    weight: float
    bmi: float
    verdict: verdictEnum

@app.post("/add")
def add_patient(patient: PatientModel):
    data = load_data()
    if data:
        last_id = max(int(k[1:]) for k in data.keys())
    else:
        last_id = 0
    new_id = f"P{last_id + 1:03}"

    data[new_id] = patient.model_dump()

    save_data(data)

    return {"message": "Patient added successfully", "patient_id": new_id}

@app.delete("/delete/{patient_id}")
def delete_patient(patient_id: str):
    data = load_data()
    if patient_id not in data:
        raise HTTPException(status_code = 404, detail = "Patient not Fount")
    
    del data[patient_id]
    save_data(data)

    return{"message": f"Patient {patient_id} deleted successfully"}