from pydantic import BaseModel

from src.Page import Page


class TokenTypeLabels(BaseModel):
    pages: list[Page] = list()
