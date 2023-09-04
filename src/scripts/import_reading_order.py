import os
import sys
from os.path import join, exists
from pathlib import Path

from pdf_token_type_labels.TokenTypeLabel import TokenTypeLabel
from pdf_token_type_labels.TokenTypeLabels import TokenTypeLabels
from pdf_token_type_labels.TokenTypePage import TokenTypePage

from scripts.import_token_type import loop_xmls

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from lxml import etree
from lxml.etree import ElementBase

from config import (
    XML_NAME,
    LABELS_FILE_NAME,
    LABELED_XML_DESTINATION,
    LABELED_DATA_DESTINATION,
)


def get_folder_name(xml_name: str):
    return xml_name.replace(".xml", "")


def create_labels():
    for dataset_type_name, xml_name in loop_xmls():
        inside_labels_to_json_labels(dataset_type_name, xml_name)


def inside_labels_to_json_labels(dataset_type_name: str, xml_name: str):
    file: str = open(
        join(LABELED_XML_DESTINATION, get_folder_name(xml_name), XML_NAME)
    ).read()
    file_bytes: bytes = file.encode("utf-8")
    root: ElementBase = etree.fromstring(file_bytes)

    token_type_labels = TokenTypeLabels()

    for page_element in root.findall(".//page"):
        page_labels: list[TokenTypeLabel] = list()
        for text_element in page_element.findall(".//text"):
            label = get_reading_order_label(text_element)
            page_labels.append(label)

        token_type_labels.pages.append(
            TokenTypePage(number=page_element.attrib["number"], labels=page_labels)
        )

    labels_path: Path = Path(
        join(
            LABELED_DATA_DESTINATION,
            "reading_order",
            dataset_type_name,
            get_folder_name(xml_name),
            LABELS_FILE_NAME,
        )
    )

    if not exists(labels_path.parent):
        os.makedirs(labels_path.parent)

    labels_path.write_text(token_type_labels.model_dump_json(indent=4))


def get_reading_order_label(text_element: ElementBase):
    return TokenTypeLabel(
        top=text_element.attrib["top"],
        left=text_element.attrib["left"],
        width=text_element.attrib["width"],
        height=text_element.attrib["height"],
        token_type=int(text_element.attrib["reading_order_no"]),
    )


if __name__ == "__main__":
    create_labels()
