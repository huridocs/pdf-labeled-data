import json
import os
import shutil
import sys
from collections import defaultdict
from os import listdir
from os.path import join, isdir, exists
from pathlib import Path

from pdf_features.Rectangle import Rectangle
from pdf_token_type_labels.TokenTypeLabel import TokenTypeLabel
from pdf_token_type_labels.TokenTypeLabels import TokenTypeLabels
from pdf_token_type_labels.TokenTypePage import TokenTypePage
from pdf_token_type_labels.TableOfContentType import TableOfContentType

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from lxml.etree import ElementBase

from config import (
    LABELS_FILE_NAME,
    LABELED_XML_DESTINATION,
    LABELED_DATA_DESTINATION,
    LABELED_TOC_DATA_SOURCE,
    PDF_NAME,
)

TOC_TYPES = {
    0: TableOfContentType.INDENTATION_0,
    1: TableOfContentType.INDENTATION_1,
    2: TableOfContentType.INDENTATION_2,
    3: TableOfContentType.INDENTATION_3,
    4: TableOfContentType.INDENTATION_3,
    5: TableOfContentType.INDENTATION_3,
}


def import_structure():
    for (
        pdf_path,
        json_path,
        folder_path,
        folder_name,
    ) in loop_table_of_content_folders():
        xml_destination_folder_path = join(LABELED_XML_DESTINATION, folder_name)

        if not exists(xml_destination_folder_path):
            os.makedirs(xml_destination_folder_path)
            shutil.copyfile(pdf_path, join(xml_destination_folder_path, PDF_NAME))

        os.makedirs(
            join(
                LABELED_DATA_DESTINATION, "table_of_content", "dataset_1", folder_name
            ),
            exist_ok=True,
        )


def loop_table_of_content_folders():
    for folder_name in listdir(LABELED_TOC_DATA_SOURCE):
        folder_path = join(LABELED_TOC_DATA_SOURCE, folder_name)

        if not isdir(folder_path):
            continue

        pdf_path = join(folder_path, f"{folder_name}.pdf")
        if not exists(pdf_path):
            continue

        json_path = join(folder_path, "toc.json")
        if not exists(json_path):
            continue

        yield pdf_path, Path(json_path), folder_path, folder_name


def create_labels():
    for (
        pdf_path,
        json_path,
        folder_path,
        folder_name,
    ) in loop_table_of_content_folders():
        tocs = json.loads(json_path.read_text())
        labels_per_page = defaultdict(list)
        for toc in tocs:
            rectangles = list()
            page = 0
            for selection_rectangle in toc["selectionRectangles"]:
                rectangles.append(
                    Rectangle.from_width_height(
                        left=int(selection_rectangle["left"] * 0.75),
                        top=int(selection_rectangle["top"] * 0.75),
                        width=int(selection_rectangle["width"] * 0.75),
                        height=int(selection_rectangle["height"] * 0.75),
                    )
                )
                page = selection_rectangle["page"]

            bounding_box = Rectangle.merge_rectangles(rectangles)
            indentation = toc["indentation"]

            label = TokenTypeLabel(
                top=bounding_box.top,
                left=bounding_box.left,
                width=bounding_box.width,
                height=bounding_box.height,
                token_type=TOC_TYPES[indentation],
            )
            labels_per_page[page].append(label)

        labels_path: str = join(
            LABELED_DATA_DESTINATION,
            "table_of_content",
            "dataset_1",
            folder_name,
            LABELS_FILE_NAME,
        )
        pages = [
            TokenTypePage(number=page_number, labels=labels)
            for page_number, labels in labels_per_page.items()
        ]
        token_type_labels = TokenTypeLabels(pages=pages)
        Path(labels_path).write_text(token_type_labels.model_dump_json(indent=4))


def get_text_elements_by_segment(page_element) -> dict[str : list[ElementBase]]:
    text_elements_by_paragraphs: dict[str : list[ElementBase]] = defaultdict(list)
    for text_element in page_element.findall(".//text"):
        key = page_element.attrib["number"] + "_" + text_element.attrib["segment_no"]
        text_elements_by_paragraphs[key].append(text_element)

    return text_elements_by_paragraphs


if __name__ == "__main__":
    import_structure()
    create_labels()
