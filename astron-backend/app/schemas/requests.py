from pydantic import BaseModel, Field

class SkySearchRequest(BaseModel):
    ra: float = Field(
        ge=0,
        lt=360,
        description="Right Ascension in degrees",
    )

    dec : float = Field(
        ge=-90,
        le=90,
        description="Declination in degrees",
    )

    radius: float = Field(
        gt=0,
        le=180,
        description="Search radius in degrees",
    )