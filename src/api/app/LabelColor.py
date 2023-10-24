from pydantic import BaseModel


class LabelColor(BaseModel):
    text: str
    color: str
