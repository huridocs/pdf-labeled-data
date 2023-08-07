from lxml.etree import ElementBase
from pydantic import BaseModel

from api.app.Token import Token


class Page(BaseModel):
    width: int
    height: int
    index: int
    tokens: list[Token]

    @staticmethod
    def from_tree(xml_page: ElementBase):
        index = int(xml_page.attrib["number"]) - 1
        tokens = [Token.from_tree(xml_token) for xml_token in xml_page.findall(".//text")]
        width = int(xml_page.attrib["width"])
        height = int(xml_page.attrib["height"])
        return Page(width=width, height=height, index=index, tokens=tokens)
