from pydantic import BaseModel, Field
from typing import List, Literal

class DiseaseTheory(BaseModel):
    """Information about disease"""
    disease_name: str = Field(
        description="Name of the disease",
        examples=["cancer", "melanoma", "medulloblastoma"]
    )
    affected_body_parts: Literal["Leg", "Arm", "Skin"] = Field(
        description="Where does the disease Occur, what body parts are affected?"
    )
    symptoms: str = Field(
        description="Main symptoms of the disease",
        examples=["pain, swelling, fatigue"]
    )
    risk_factors: str = Field(
        description="Factors that increase risk of disease",
        examples=["smoking, UV exposure, genetic predisposition"]
    )
    disease_type: str = Field(
        description="The type/category of the disease",
        examples=["cancer", "genetic", "infectious"]
    )
    progression_stage: str = Field(
        description="Different stages or progression levels of the disease",
        examples=["early stage, advanced, metastatic"]
    )
    treatment_approaches: str = Field(
        description="Known treatment methods for the disease",
        examples=["surgery, chemotherapy, immunotherapy"]
    )
    prognosis: str = Field(
        description="Expected outcome or survival rate of the disease",
        examples=["good, moderate, poor"]
    )
