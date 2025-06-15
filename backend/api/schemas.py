from pydantic import BaseModel

class HealthResponse(BaseModel):
    status: str

class ExportResponse(BaseModel):
    message: str
    records_exported: int

class ExportRequest(BaseModel):
    export_type: str
    filters: dict
