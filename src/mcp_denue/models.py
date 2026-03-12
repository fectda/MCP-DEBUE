from typing import Optional, List, Any, Dict
from pydantic import BaseModel, Field


# DENUE raw API models (for parsing HTTP responses)
class DenueEstablishmentRaw(BaseModel):
    CLEE: Optional[str] = None
    Id: str
    Nombre: str
    Razon_social: Optional[str] = None
    Clase_actividad: str
    Estrato: str
    Tipo_vialidad: str
    Calle: str
    Num_Exterior: Optional[str] = None
    Num_Interior: Optional[str] = None
    Colonia: Optional[str] = None
    CP: Optional[str] = None
    Ubicacion: str
    Telefono: Optional[str] = None
    Correo_e: Optional[str] = None
    Sitio_internet: Optional[str] = None
    Tipo: str
    Latitud: str
    Longitud: str
    CentroComercial: Optional[str] = None
    TipoCentroComercial: Optional[str] = None
    NumLocal: Optional[str] = None


# Internal Models (Output of MCP tools)
class Establishment(BaseModel):
    clee: Optional[str] = None
    id: str
    name: str
    legal_name: Optional[str] = None
    activity_class: str
    size_class: str
    street_type: str
    street_name: str
    ext_number: Optional[str] = None
    int_number: Optional[str] = None
    neighborhood: Optional[str] = None
    postal_code: Optional[str] = None
    location: str
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    unit_type: str
    latitude: float
    longitude: float
    shopping_center: Optional[str] = None
    shopping_center_type: Optional[str] = None
    unit_number: Optional[str] = None

    @classmethod
    def from_raw(cls, raw: DenueEstablishmentRaw) -> "Establishment":
        try:
            lat = float(raw.Latitud)
        except ValueError:
            lat = 0.0

        try:
            lon = float(raw.Longitud)
        except ValueError:
            lon = 0.0

        return cls(
            clee=raw.CLEE,
            id=raw.Id,
            name=raw.Nombre,
            legal_name=raw.Razon_social if raw.Razon_social else None,
            activity_class=raw.Clase_actividad,
            size_class=raw.Estrato,
            street_type=raw.Tipo_vialidad,
            street_name=raw.Calle,
            ext_number=raw.Num_Exterior if raw.Num_Exterior else None,
            int_number=raw.Num_Interior if raw.Num_Interior else None,
            neighborhood=raw.Colonia if raw.Colonia else None,
            postal_code=raw.CP if raw.CP else None,
            location=raw.Ubicacion,
            phone=raw.Telefono if raw.Telefono else None,
            email=raw.Correo_e if raw.Correo_e else None,
            website=raw.Sitio_internet if raw.Sitio_internet else None,
            unit_type=raw.Tipo,
            latitude=lat,
            longitude=lon,
            shopping_center=raw.CentroComercial if raw.CentroComercial else None,
            shopping_center_type=(
                raw.TipoCentroComercial if raw.TipoCentroComercial else None
            ),
            unit_number=raw.NumLocal if raw.NumLocal else None,
        )


class EstablishmentDetail(Establishment):
    # Depending on the Ficha API, it might return more fields.
    # The PRD states we should mirror Ficha's fields as much as possible.
    # For now, we will inherit Establishment and accept any extra fields.
    extra_details: Dict[str, Any] = Field(default_factory=dict)


class CountResponse(BaseModel):
    activity_id: str
    area_code: str
    total_establishments: int


class SearchResponse(BaseModel):
    results: List[Establishment]
    truncated: bool = False
