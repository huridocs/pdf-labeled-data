from lxml.etree import ElementBase
from pydantic import BaseModel

from src.TokenType import TokenType


class TokenTypeLabel(BaseModel):
    top: int
    left: int
    width: int
    height: int
    tag_type: TokenType

    @staticmethod
    def from_text_element(text_element: ElementBase):
        return TokenTypeLabel(top=text_element.attrib["top"],
                              left=text_element.attrib["left"],
                              width=text_element.attrib["width"],
                              height=text_element.attrib["height"],
                              tag_type=TokenType.from_text(text_element.attrib["tag_type"]))
