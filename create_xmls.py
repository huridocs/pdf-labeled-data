import subprocess
from os import listdir
from os.path import join, exists

from config import LABELED_XML_DESTINATION, XML_NAME, PDF_NAME


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
        xmls_count += 1
        print()

    print(f"Done. Created {xmls_count} XMLs")


if __name__ == "__main__":
    create_xmls()
