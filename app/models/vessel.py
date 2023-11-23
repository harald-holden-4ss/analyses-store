from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID


class vessel(BaseModel, extra="forbid"):
    id: UUID | None = None
    name: str = Field(min_length=1)
    imo: int = Field(gt=0)
    year_built: Optional[int] = Field(None, gt=0)
