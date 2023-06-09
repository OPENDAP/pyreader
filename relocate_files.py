
import xml.dom.minidom as minidom
import regex as re
import os
import time
import shutil


class Info:
    def __init__(self, daac, date):
        self.DAAC = daac
        self.date = date
        self.path = ''


def get_xml_list():
    dir_path = "./xml"
    xmls = []
    for path in os.listdir(dir_path):
        # check if current path is a file
        if os.path.isfile(os.path.join(dir_path, path)):
            if re.match(".*\.xml", path) and not re.search("unittest.*\.xml", path):
                xmls.append(path)

    return xmls


def parse_file(name):
    match = re.search("(.*)-(\d{2})\.\d{2}\.(\d{4})", name)
    if match:
        daac = match.group(1).strip()
        month = match.group(2).strip()
        year = match.group(3).strip()
        # print("DAAC: '" + daac + "' | month/year : '" + month + "/" + year + "'")
        date = month + "_" + year
        info = Info(daac, date)
    return info


def check_dirs(info):
    www_dir = "/var/www/html/pyreader-tests/"
    daac_dir = os.path.join(www_dir, info.DAAC)
    month_dir = os.path.join(daac_dir, info.date)

    if not os.path.exists(daac_dir):
        os.mkdir(daac_dir)

    if not os.path.exists(month_dir):
        os.mkdir(month_dir)

    info.path = month_dir


def move_file(name, info):
    old_dir = "./xml"
    shutil.move(os.path.join(old_dir, name), os.path.join(info.path, name))


def driver():
    xmls = get_xml_list()
    for file in xmls:
        info = parse_file(file)
        print(info.DAAC + " | " + info.date)
        check_dirs(info)
        move_file(file, info)


def main():
    # main for testing script
    driver()


if __name__ == "__main__":
    main()