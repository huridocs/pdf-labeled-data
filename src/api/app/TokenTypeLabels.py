from pydantic import BaseModel

from api.app.TokenTypePage import TokenTypePage


class TokenTypeLabels(BaseModel):
    pages: list[TokenTypePage] = list()
