from pydantic import BaseModel, Field
from typing import Optional


class EspecialidadInput(BaseModel):
    """ "name": "Cardiología",
    "description": "Prevención y tratamiento de enfermedades del corazón.",
    "taxonomy": [
        "cardiólogo",
        "corazón",
        "presión",
        "infarto",
        "electrocardiograma",
        "hipertensión",
    ],"""

    nombre: str = Field(
        ..., description="Nombre de la especialidad", min_length=1, max_length=100
    )
    descripcion: Optional[str] = Field(
        None, description="Descripción de la especialidad", min_length=0, max_length=500
    )
    codigo: str = Field(
        ..., description="Código único de la especialidad", min_length=1, max_length=50
    )
    taxonomia: Optional[list[str]] = Field(
        None,
        description="Lista de términos relacionados con la especialidad",
        min_items=0,
    )


class EspecialidadOutput(BaseModel):
    """Modelo de salida para la especialidad"""

    id: str = Field(..., description="ID único de la especialidad")
    nombre: str = Field(
        ..., description="Nombre de la especialidad", min_length=1, max_length=100
    )
    codigo: str = Field(
        ..., description="Código único de la especialidad", min_length=1, max_length=50
    )
    descripcion: Optional[str] = Field(
        None, description="Descripción de la especialidad", min_length=0, max_length=500
    )
    taxonomia: Optional[list[str]] = Field(
        None,
        description="Lista de términos relacionados con la especialidad",
        min_items=0,
    )
