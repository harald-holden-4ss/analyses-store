from pydantic import BaseModel, Field
from uuid import uuid4, UUID
from typing import List, Literal


class json_patch_modify(BaseModel, extra="forbid"):
    op: str
    path: str
    value: str | float
