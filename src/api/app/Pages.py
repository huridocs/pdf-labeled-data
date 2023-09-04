from lxml import etree
from lxml.etree import ElementBase
from pydantic import BaseModel

from api.app.Page import Page


class Pages(BaseModel):
    pages: list[Page]

    @staticmethod
    def from_etree(file_path: str):
        file: str = open(file_path).read()
        file_bytes: bytes = file.encode("utf-8")

        parser = etree.XMLParser(recover=True, encoding="utf-8")
        root: ElementBase = etree.fromstring(file_bytes, parser=parser)

        pages: list[Page] = [
            Page.from_tree(tree_page) for tree_page in root.findall(".//page")
        ]
        return Pages(pages=pages)
