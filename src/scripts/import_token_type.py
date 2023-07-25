import os
import shutil
from os import listdir
from os.path import join
from pathlib import Path

from lxml import etree
from lxml.etree import ElementBase

from config import ROOT_PATH, XML_NAME, LABELS_FILE_NAME, PROJECT_PATH

from src.Page import Page
from src.TokenTypeLabel import TokenTypeLabel
from src.TokenTypeLabels import TokenTypeLabels

LABELED_DATA_SOURCE = join(PROJECT_PATH, 'ml_pdf_editor', 'labeled_xmls_poppler')
LABELED_DATA_DESTINATION = join(ROOT_PATH, 'labeled_data', 'token_type')


def get_folder_name(xml_name: str):
    return xml_name.replace('.xml', '')


def import_xml():
    for dataset_type_name, xml_folder_path, xml_name in loop_xmls():
        xml_old_path = join(LABELED_DATA_SOURCE, dataset_type_name, xml_name)
        xml_new_path = join(xml_folder_path, XML_NAME)

        os.makedirs(Path(xml_new_path).parent, exist_ok=True)
        shutil.copyfile(xml_old_path, xml_new_path)


def loop_xmls():
    for dataset_type_name in listdir(LABELED_DATA_SOURCE):
        for xml_name in sorted(listdir(join(LABELED_DATA_SOURCE, dataset_type_name))):
            xml_folder_name = get_folder_name(xml_name)
            yield dataset_type_name, join(LABELED_DATA_DESTINATION, dataset_type_name, xml_folder_name), xml_name


def create_labels():
    for dataset_type_name, xml_folder_path, xml_name in loop_xmls():
        inside_labels_to_json_labels(xml_folder_path)


def inside_labels_to_json_labels(xml_folder_path: str):
    file: str = open(join(xml_folder_path, XML_NAME)).read()
    file_bytes: bytes = file.encode('utf-8')
    root: ElementBase = etree.fromstring(file_bytes)

    token_type_labels = TokenTypeLabels()

    for page_element in root.findall('.//page'):
        page_labels: list[TokenTypeLabel] = list()
        for text_element in page_element.findall('.//text'):
            label = TokenTypeLabel.from_text_element(text_element)
            page_labels.append(label)

        token_type_labels.pages.append(Page(number=page_element.attrib["number"], labels=page_labels))

    Path(join(xml_folder_path, LABELS_FILE_NAME)).write_text(token_type_labels.model_dump_json(indent=4))


if __name__ == '__main__':
    create_labels()
