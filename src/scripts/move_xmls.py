import os
import shutil
from os import listdir
from os.path import join, exists

from config import ROOT_PATH

destination_path = join(ROOT_PATH, "pdfs")


def move_xmls():
    source_path = join(ROOT_PATH, "labeled_data", "token_type")

    for dataset in listdir(source_path):
        label_path = join(source_path, dataset)

        if not os.path.isdir(label_path):
            continue

        for pdf_name in listdir(label_path):
            pdf_path = join(destination_path, pdf_name)
            xml_source_path = join(source_path, dataset, pdf_name, "etree.xml")

            if not exists(xml_source_path) or exists(pdf_path):
                continue

            os.mkdir(pdf_path)
            shutil.move(xml_source_path, pdf_path)


def move_pdfs():
    for pdf_name in listdir(join(destination_path, "pdfs")):
        destination_folder_name = pdf_name.replace(".pdf", "")
        destination_pdf_path = join(destination_path, destination_folder_name)

        if exists(destination_pdf_path):
            shutil.copy(join(destination_path, "pdfs", pdf_name), join(destination_pdf_path, "document.pdf"))


if __name__ == "__main__":
    move_pdfs()
