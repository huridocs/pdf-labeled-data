import os
import subprocess
from os import listdir
from os.path import join, exists

from lxml import etree
from lxml.etree import ElementBase, XMLSyntaxError

from config import LABELED_XML_DESTINATION, XML_NAME, PDF_NAME


def contains_text(xml_path: str):
    try:
        file_content = open(xml_path).read()
        file_bytes = file_content.encode("utf-8")
        root: ElementBase = etree.fromstring(file_bytes)
        text_elements: list[ElementBase] = root.findall(".//text")
    except (FileNotFoundError, UnicodeDecodeError, XMLSyntaxError):
        return False
    return len(text_elements) > 0


def create_xmls():
    print("Creating missing XML from PDFs")
    xmls_count = 0
    for pdf_name in listdir(LABELED_XML_DESTINATION):
        pdf_path = join(LABELED_XML_DESTINATION, pdf_name, PDF_NAME)
        xml_path = join(LABELED_XML_DESTINATION, pdf_name, XML_NAME)

        if not exists(pdf_path):
            print("error", pdf_path)
            continue

        if exists(xml_path):
            continue

        print(pdf_name)
        print(pdf_path)
        print(xml_path)
        subprocess.run(["pdftohtml", "-i", "-xml", "-zoom", "1.0", pdf_path, xml_path])
        if not contains_text(xml_path):
            subprocess.run(["pdftohtml", "-i", "-hidden", "-xml", "-zoom", "1.0", pdf_path, xml_path])

        xmls_count += 1
        print()

    print(f"Done. Created {xmls_count} XMLs")


def remove_xmls():
    for pdf_name in listdir(LABELED_XML_DESTINATION):
        xml_path = join(LABELED_XML_DESTINATION, pdf_name, XML_NAME)
        print("removing", xml_path)
        if exists(xml_path):
            os.remove(xml_path)


if __name__ == "__main__":
    create_xmls()
