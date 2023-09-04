from os.path import join

from lxml import etree
from lxml.etree import ElementBase


def import_toc_from_xml():
    file: str = open(
        "/home/gabo/projects/information_extraction/table_of_content/labeled_documents_manual/5a4d294c79f3f44b101e2816/20210129-135247283927_ouv52ak2aitxzsluccmbihpvi_spa.xml"
    ).read()
    file_bytes: bytes = file.encode("utf-8")
    root: ElementBase = etree.fromstring(file_bytes)

    alto = root.find(".//alto")
    print("aye")
    print(alto)


if __name__ == "__main__":
    import_toc_from_xml()
