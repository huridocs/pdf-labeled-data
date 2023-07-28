from lxml.etree import ElementBase
from pydantic import BaseModel


class Token(BaseModel):
    x: int
    y: int
    width: int
    height: int
    text: str

    @staticmethod
    def from_tree(xml_token: ElementBase):
        x = int(xml_token.attrib["left"])
        y = int(xml_token.attrib["top"])
        width = int(xml_token.attrib["width"])
        height = int(xml_token.attrib["height"])
        text = ''.join(xml_token.itertext()).strip()
        return Token(x=x, y=y, width=width, height=height, text=text)
