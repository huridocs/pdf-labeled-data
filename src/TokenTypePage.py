from pydantic import BaseModel
from src.TokenTypeLabel import TokenTypeLabel


class TokenTypePage(BaseModel):
    number: int
    labels: list[TokenTypeLabel]
