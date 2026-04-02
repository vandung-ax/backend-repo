from pydantic import BaseModel

class CoVanInfoResponse(BaseModel):
    Id_CoVan: int
    TenCoVan: str
    MaKhoa: str
    TenKhoa: str
    
    class Config:
        from_attributes = True