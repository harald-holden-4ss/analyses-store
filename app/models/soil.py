from pydantic import BaseModel, Field
from uuid import UUID


class soil_data(BaseModel, extra="forbid"):
    id: UUID | None = None
    name: str = Field(min_length=1)
    
