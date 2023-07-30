from typing import List

from pydantic import BaseModel

from api.app.TokenTypePage import TokenTypePage


class TokenTypeLabels(BaseModel):
    pages: List[TokenTypePage] = list()