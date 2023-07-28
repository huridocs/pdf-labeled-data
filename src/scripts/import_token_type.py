import os
import shutil
import sys
from os import listdir
from os.path import join
from pathlib import Path

from src.api.app.TokenTypeLabel import TokenTypeLabel
from src.api.app.TokenTypeLabels import TokenTypeLabels
from src.api.app.TokenTypePage import TokenTypePage

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from lxml import etree
from lxml.etree import ElementBase

from config import ROOT_PATH, XML_NAME, LABELS_FILE_NAME, PROJECT_PATH






def get_folder_name(xml_name: str):
    return xml_name.replace('.xml', '')


def import_xml():
    for dataset_type_name, xml_name in loop_xmls():
        xml_old_path = join(LABELED_DATA_SOURCE, dataset_type_name, xml_name)
        xml_new_path = join(LABELED_XML_DESTINATION, get_folder_name(xml_name), XML_NAME)

        os.makedirs(Path(xml_new_path).parent, exist_ok=True)
        shutil.copyfile(xml_old_path, xml_new_path)


def loop_xmls():
    for dataset_type_name in listdir(LABELED_DATA_SOURCE):
        for xml_name in sorted(listdir(join(LABELED_DATA_SOURCE, dataset_type_name))):
            yield dataset_type_name, xml_name


def create_labels():
    for dataset_type_name, xml_name in loop_xmls():
        inside_labels_to_json_labels(dataset_type_name, xml_name)


def inside_labels_to_json_labels(dataset_type_name: str, xml_name: str):
    file: str = open(join(LABELED_XML_DESTINATION, get_folder_name(xml_name), XML_NAME)).read()
    file_bytes: bytes = file.encode('utf-8')
    root: ElementBase = etree.fromstring(file_bytes)

    token_type_labels = TokenTypeLabels()

    for page_element in root.findall('.//page'):
        page_labels: list[TokenTypeLabel] = list()
        for text_element in page_element.findall('.//text'):
            label = TokenTypeLabel.from_text_element(text_element)
            page_labels.append(label)

        token_type_labels.pages.append(TokenTypePage(number=page_element.attrib["number"], labels=page_labels))

    labels_path: str = join(LABELED_DATA_DESTINATION, dataset_type_name, get_folder_name(xml_name), LABELS_FILE_NAME)
    Path(labels_path).write_text(token_type_labels.model_dump_json(indent=4))


if __name__ == '__main__':
    # import_xml()
    create_labels()
