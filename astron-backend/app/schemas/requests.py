from pydantic import BaseModel, Field


class SkySearchRequest(BaseModel):
    ra: float = Field(
        ge=0, lt=360, allow_inf_nan=False,
        description="Right Ascension in degrees",
    )
    dec: float = Field(
        ge=-90, le=90, allow_inf_nan=False,
        description="Declination in degrees",
    )
    radius: float = Field(
        gt=0, le=180, allow_inf_nan=False,
        description="Search radius in degrees",
    )


class FitsDownloadRequest(BaseModel):
    obs_id: str = Field(
        min_length=1, max_length=128,
        description="SPHEREx observation identifier",
    )
    access_url: str = Field(
        min_length=1, max_length=2048,
        description="IRSA FITS product download URL",
    )


class FitsInspectRequest(BaseModel):
    obs_id: str = Field(
        min_length=1, max_length=128,
        description="SPHEREx observation identifier",
    )


class SpectralInfoRequest(BaseModel):
    obs_id: str = Field(
        min_length=1, max_length=128,
        description="SPHEREx observation identifier",
    )
    x: float = Field(
        gt=0, allow_inf_nan=False,
        description="FITS pixel coordinate along X (1-based)",
    )
    y: float = Field(
        gt=0, allow_inf_nan=False,
        description="FITS pixel coordinate along Y (1-based)",
    )


class PixelInfoRequest(BaseModel):
    obs_id: str = Field(
        min_length=1, max_length=128,
        description="SPHEREx observation identifier",
    )
    x: float = Field(
        gt=0, allow_inf_nan=False,
        description="FITS pixel coordinate along X (1-based)",
    )
    y: float = Field(
        gt=0, allow_inf_nan=False,
        description="FITS pixel coordinate along Y (1-based)",
    )
