import json
import os
import shutil
import sys
from os import listdir
from os.path import join, isdir, exists
from pathlib import Path

from pdf_features.Rectangle import Rectangle
from pdf_token_type_labels.ParagraphType import ParagraphType
from pdf_token_type_labels.TokenTypeLabel import TokenTypeLabel
from pdf_token_type_labels.TokenTypeLabels import TokenTypeLabels
from pdf_token_type_labels.TokenTypePage import TokenTypePage

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


from config import (
    LABELED_XML_DESTINATION,
    PROJECT_PATH,
    PDF_NAME,
    LABELED_DATA_DESTINATION,
    LABELS_FILE_NAME,
)


PARAGRAPH_SELECTOR_SOURCE = join(PROJECT_PATH, "segment_selector", "labeled_data")


def get_folder_name(xml_name: str):
    return xml_name.replace(".xml", "")


def loop_pdfs():
    for dataset_type_name in listdir(PARAGRAPH_SELECTOR_SOURCE):
        for pdf_name in sorted(listdir(join(PARAGRAPH_SELECTOR_SOURCE, dataset_type_name))):
            if not isdir(join(PARAGRAPH_SELECTOR_SOURCE, dataset_type_name, pdf_name)):
                continue

            if pdf_name == "status":
                continue

            yield dataset_type_name, pdf_name


def import_pdfs():
    pdfs_imported = 0
    pdfs_exists = 0
    for dataset_type_name, pdf_name in loop_pdfs():
        pdf_old_path = join(PARAGRAPH_SELECTOR_SOURCE, dataset_type_name, pdf_name, pdf_name + ".pdf")
        pdf_new_path = join(LABELED_XML_DESTINATION, pdf_name, PDF_NAME)

        if not exists(pdf_new_path):
            pdfs_imported += 1
            os.makedirs(Path(pdf_new_path).parent, exist_ok=True)
            shutil.copyfile(pdf_old_path, pdf_new_path)
        else:
            print("exixts", pdf_name)
            pdfs_exists += 1

    print("pdfs_imported", pdfs_imported)
    print("pdfs_exists", pdfs_exists)


def create_labels():
    for dataset_type_name, pdf_name in loop_pdfs():
        old_json_labels_to_json_labels(dataset_type_name, pdf_name)


def old_json_labels_to_json_labels(dataset_type_name: str, pdf_name: str):
    json_path = join(PARAGRAPH_SELECTOR_SOURCE, dataset_type_name, pdf_name, "development_user@example.com_annotations.json")
    annotations = json.loads(Path(json_path).read_text())

    labels_path, labels_per_page = get_labels_per_page(annotations, dataset_type_name, pdf_name)

    os.makedirs(labels_path.parent.parent, exist_ok=True)
    os.makedirs(labels_path.parent, exist_ok=True)

    pages = [TokenTypePage(number=page_number, labels=labels) for page_number, labels in labels_per_page.items()]
    token_type_labels = TokenTypeLabels(pages=pages)
    labels_path.write_text(token_type_labels.model_dump_json(indent=4))
    print("creating labels for", dataset_type_name, pdf_name)


def get_labels_per_page(annotations, dataset_type_name, pdf_name):
    labels_per_page = dict()
    for annotation in annotations["annotations"]:
        annotation_type_name = annotation["label"]["text"].lower()
        if annotation_type_name != dataset_type_name:
            continue

        bounding_box = Rectangle(
            left=int(annotation["bounds"]["left"]),
            top=int(annotation["bounds"]["top"]),
            right=int(annotation["bounds"]["right"]),
            bottom=int(annotation["bounds"]["bottom"]),
        )

        label = TokenTypeLabel(
            top=bounding_box.top,
            left=bounding_box.left,
            width=bounding_box.width,
            height=bounding_box.height,
            token_type=ParagraphType.PARAGRAPH,
        )
        page = int(annotation["page"]) + 1

        labels_per_page.setdefault(page, []).append(label)
    labels_path: Path = Path(
        join(
            LABELED_DATA_DESTINATION,
            "paragraph_selector",
            dataset_type_name,
            pdf_name,
            LABELS_FILE_NAME,
        )
    )
    return labels_path, labels_per_page


if __name__ == "__main__":
    create_labels()
    # import_pdfs()
