import os
import sys
from collections import defaultdict
from os import listdir
from os.path import join, isdir
from pathlib import Path

from pdf_token_type_labels.TokenTypeLabel import TokenTypeLabel
from pdf_token_type_labels.TokenTypeLabels import TokenTypeLabels
from pdf_token_type_labels.TokenTypePage import TokenTypePage

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


def import_structure():
    for dataset_type_name, xml_name in loop_token_type_pdfs():
        os.makedirs(
            join(
                LABELED_DATA_DESTINATION,
                "paragraph_extraction",
                dataset_type_name,
                xml_name,
            )
        )


def loop_token_type_pdfs():
    for dataset_type_name in listdir(join(LABELED_DATA_DESTINATION, "token_type")):
        dataset_path = join(LABELED_DATA_DESTINATION, "token_type", dataset_type_name)

        if not isdir(dataset_path):
            continue

        for xml_name in sorted(listdir(dataset_path)):
            yield dataset_type_name, xml_name


def create_labels():
    for dataset_type_name, xml_name in loop_token_type_pdfs():
        xml_labels_to_json_labels(dataset_type_name, xml_name)


def xml_labels_to_json_labels(dataset_type_name: str, xml_name: str):
    file: str = open(
        join(LABELED_XML_DESTINATION, get_folder_name(xml_name), XML_NAME)
    ).read()
    file_bytes: bytes = file.encode("utf-8")
    root: ElementBase = etree.fromstring(file_bytes)

    token_type_labels = TokenTypeLabels()

    for page_element in root.findall(".//page"):
        text_elements_by_paragraphs: dict[
            str : list[ElementBase]
        ] = get_text_elements_by_segment(page_element)
        page_labels: list[TokenTypeLabel] = [
            TokenTypeLabel.from_text_elements(text_elements)
            for text_elements in text_elements_by_paragraphs.values()
        ]
        token_type_labels.pages.append(
            TokenTypePage(number=page_element.attrib["number"], labels=page_labels)
        )

    labels_path: str = join(
        LABELED_DATA_DESTINATION,
        "paragraph_extraction",
        dataset_type_name,
        get_folder_name(xml_name),
        LABELS_FILE_NAME,
    )
    Path(labels_path).write_text(token_type_labels.model_dump_json(indent=4))


def get_text_elements_by_segment(page_element) -> dict[str : list[ElementBase]]:
    text_elements_by_paragraphs: dict[str : list[ElementBase]] = defaultdict(list)
    for text_element in page_element.findall(".//text"):
        key = page_element.attrib["number"] + "_" + text_element.attrib["segment_no"]
        text_elements_by_paragraphs[key].append(text_element)

    return text_elements_by_paragraphs


if __name__ == "__main__":
    # import_structure()
    create_labels()
