from pydantic import BaseModel
from api.app.TokenTypeLabel import TokenTypeLabel


class TokenTypePage(BaseModel):
    number: int
    labels: list[TokenTypeLabel]
