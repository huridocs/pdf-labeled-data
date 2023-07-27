from pydantic import BaseModel

from src.TokenTypePage import TokenTypePage


class TokenTypeLabels(BaseModel):
    pages: list[TokenTypePage] = list()
