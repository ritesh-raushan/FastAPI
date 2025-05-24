from fastapi import FastAPI, Path, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, computed_field
from typing import Annotated, Literal, Optional
import json

app = FastAPI()

def load_data():
    with open("patients.json", "r") as f:
        data = json.load(f)
    return data

def save_data(data):
    with open("patients.json", "w") as f:
        json.dump(data, f)

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

class Patient(BaseModel):
    id: Annotated[str, Field(..., description="ID of the patient", examples=["P001"])]
    name: Annotated[str, Field(..., description="Name of the patient")]
    city: Annotated[str, Field(..., description="City where the patient is living")]
    age: Annotated[int, Field(..., ge=0, lt=120,description="Age of the patient in years")]
    gender: Annotated[Literal['male', 'female', 'others'], Field(..., description="Gender of the patient")]
    height: Annotated[float, Field(..., gt=0, description="Height of the patient in meters")]
    weight: Annotated[float, Field(..., gt=0, description="Weight of the patient in kgs")]

    @computed_field
    @property
    def bmi(self) -> float:
        bmi = round(self.weight / (self.height ** 2), 2)
        return bmi
    
    @computed_field
    @property
    def verdict(self) -> str:
        if self.bmi < 18.5:
            return 'Underweight'
        elif self.bmi < 25:
            return 'Normal'
        elif self.bmi < 30:
            return 'Overweight'
        else:
            return 'Obese'

@app.post("/add")
def add_patient(patient: Patient):

    # Load Existing Data
    data = load_data()

    # Check if patient already Exists
    if patient.id in data:
        raise HTTPException(status_code=400, detail="Patient Already Exist")
    
    # Add new patient to the Database
    data[patient.id] = patient.model_dump(exclude=['id'])
    
    # Save Data into the json File
    save_data(data)

    return JSONResponse(status_code=201, content={"message":"Patient created Successfully"})

class PatientUpdate(BaseModel):
    name : Annotated[Optional[str], Field(default=None)]
    city : Annotated[Optional[str], Field(default=None)]
    age : Annotated[Optional[int], Field(default=None, gt=0)]
    gender : Annotated[Optional[Literal['male', 'female', 'others']], Field(default=None)]
    height : Annotated[Optional[float], Field(default=None, gt=0)]
    weight : Annotated[Optional[float], Field(default=None, gt=0)]

@app.put('/edit/{patient_id}')
def update_patient(patient_id: str, patient_update: PatientUpdate):

    data = load_data()

    if patient_id not in data:
        raise HTTPException(status_code=404, detail="Patient not Found")
    
    existing_patient_info = data[patient_id]

    updated_patient_info = patient_update.model_dump(exclude_unset=True)

    for key, value in updated_patient_info.items():
        existing_patient_info[key] = value

    # existing_patient_info -> pydantic object -> updated bmi + verdict
    existing_patient_info['id'] = patient_id
    patient_pydantic_obj = Patient(**existing_patient_info)
    # pydantic object -> dict
    patient_pydantic_obj.model_dump(exclude='id')

    # add this dict to data
    data[patient_id] = existing_patient_info

    # save data
    save_data(data)

    return JSONResponse(status_code=200, content={'message':"Patient Updated"})

@app.delete("/delete/{patient_id}")
def delete_patient(patient_id: str):

    data = load_data()

    if patient_id not in data:
        raise HTTPException(status_code = 404, detail = "Patient not Fount")
    
    del data[patient_id]
    
    save_data(data)

    return JSONResponse(status_code=200, content={'message':"Patient deleted successfully"})