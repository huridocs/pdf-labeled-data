from pydantic import BaseModel


class Label(BaseModel):
    text: str
    color: str
