from typing import Union

from lxml.etree import ElementBase
from pydantic import BaseModel

from api.app.ParagraphType import ParagraphType
from api.app.TokenType import TokenType


class TokenTypeLabel(BaseModel):
    top: int
    left: int
    width: int
    height: int
    token_type: Union[TokenType, ParagraphType]

    @staticmethod
    def from_text_element(text_element: ElementBase):
        return TokenTypeLabel(
            top=text_element.attrib["top"],
            left=text_element.attrib["left"],
            width=text_element.attrib["width"],
            height=text_element.attrib["height"],
            token_type=TokenType.from_text(text_element.attrib["tag_type"]),
        )

    @staticmethod
    def from_text_elements(text_elements: list[ElementBase]):
        top = min([int(x.attrib["top"]) for x in text_elements])
        left = min([int(x.attrib["left"]) for x in text_elements])
        bottom = max([int(x.attrib["top"]) + int(x.attrib["height"]) for x in text_elements])
        right = max([int(x.attrib["left"]) + int(x.attrib["width"]) for x in text_elements])

        return TokenTypeLabel(
            top=top, left=left, width=int(right - left), height=int(bottom - top), token_type=ParagraphType.PARAGRAPH
        )
