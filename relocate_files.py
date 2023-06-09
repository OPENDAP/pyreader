
import xml.dom.minidom as minidom
import regex as re
import os
import time


class Info:
    def __init__(self, daac, date):
        self.DAAC = daac
        self.date = date


def get_xml_list():
    dir_path = "./xml"
    xmls = []
    for path in os.listdir(dir_path):
        # check if current path is a file
        if os.path.isfile(os.path.join(dir_path, path)):
            if re.match(".*\.xml", path) and not re.search("unittest.*\.xml", path):
                xmls.append(path)
    # print(xmls)
    print(xmls[0])
    return xmls


def parse_file(name):
    match = re.search("(.*)-(\d{2})\.\d{2}\.(\d{4})", name)
    if match:
        daac = match.group(1).strip()
        month = match.group(2).strip()
        year = match.group(3).strip()
        print("DAAC: '" + daac + "' | month/year : '" + month + "/" + year + "'")
        date = month + "_" + year
        info = Info(daac, date)
    return info


def driver():
    xmls = get_xml_list()
    info = parse_file(xmls[0])
    print(info.DAAC + " | " + info.date)


def main():
    # main for testing script
    driver()


if __name__ == "__main__":
    main()