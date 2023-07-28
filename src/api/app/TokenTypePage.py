from typing import List

from pydantic import BaseModel
from app.TokenTypeLabel import TokenTypeLabel


class TokenTypePage(BaseModel):
    number: int
    labels: List[TokenTypeLabel]
