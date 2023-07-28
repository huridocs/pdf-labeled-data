from typing import List

from lxml import etree
from lxml.etree import ElementBase
from pydantic import BaseModel

from app.Page import Page


class Pages(BaseModel):
    pages: List[Page]

    @staticmethod
    def from_etree(file_path: str):
        file: str = open(file_path).read()
        file_bytes: bytes = file.encode("utf-8")
        root: ElementBase = etree.fromstring(file_bytes)
        pages: List[Page] = [Page.from_tree(tree_page) for tree_page in root.findall(".//page")]
        return Pages(pages=pages)
