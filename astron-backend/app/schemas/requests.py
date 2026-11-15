from pydantic import BaseModel, Field


class SkySearchRequest(BaseModel):
    ra: float = Field(ge=0, lt=360, allow_inf_nan=False)
    dec: float = Field(ge=-90, le=90, allow_inf_nan=False)
    radius: float = Field(gt=0, le=180, allow_inf_nan=False)


class FitsDownloadRequest(BaseModel):
    obs_id: str = Field(min_length=1, max_length=128)
    access_url: str = Field(min_length=1, max_length=2048)


class FitsInspectRequest(BaseModel):
    obs_id: str = Field(min_length=1, max_length=128)


class FitsUploadRequest(BaseModel):
    obs_id: str = Field(min_length=1, max_length=128)


class SpectralInfoRequest(BaseModel):
    obs_id: str = Field(min_length=1, max_length=128)
    x: float = Field(gt=0, allow_inf_nan=False)
    y: float = Field(gt=0, allow_inf_nan=False)


class PixelInfoRequest(BaseModel):
    obs_id: str = Field(min_length=1, max_length=128)
    x: float = Field(gt=0, allow_inf_nan=False)
    y: float = Field(gt=0, allow_inf_nan=False)
