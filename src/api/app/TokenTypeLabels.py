from typing import List

from pydantic import BaseModel

from app.TokenTypePage import TokenTypePage


class TokenTypeLabels(BaseModel):
    pages: List[TokenTypePage] = list()