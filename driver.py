import get_s3_files
import xml.dom.minidom as minidom
import regex as re
import subprocess


doc_template = """<?xml version="1.0" encoding="UTF-8"?>
    <bes:request xmlns:bes="http://xml.opendap.org/ns/bes/1.0#" reqID="[http-nio-8080-exec-6:40:s3_request][bes_client:/-0]">
      <bes:setContext name="bes_timeout">0</bes:setContext>
      <bes:setContext name="dap_explicit_containers">no</bes:setContext>
      <bes:setContext name="errors">xml</bes:setContext>
      <bes:setContext name="max_response_size">0</bes:setContext>
      <bes:setContainer name="S3_1" space="s3">
        URL_TEMPLATE
      </bes:setContainer>
      <bes:define name="d1" space="default">
        <bes:container name="S3_1" />
      </bes:define>
      <bes:get type="dap" definition="d1" />
    </bes:request>
"""


def read_prefix_config():
    # Using readlines()
    file1 = open('prefixs.txt', 'r')
    raw_prefixes = file1.readlines()
    prefixes = []
    count = 0

    # Strips the newline character
    for prefix in raw_prefixes:
        count += 1
        prefixes.append(prefix.strip())
        # print("Line {}: {}".format(count, prefix.strip()))

    return prefixes


def create_bescmd(url, filename):
    bescmd = doc_template.replace("URL_TEMPLATE", url)
    root = minidom.parseString(bescmd)
    # print(root.toprettyxml())
    xml_str = root.toprettyxml(indent="\t", encoding="UTF-8")
    save_path_file = "./bescmds/"+filename+".bescmd"
    with open(save_path_file, "w+b") as f:
        f.write(xml_str)
    return save_path_file


def main():
    import argparse  # for parsing arguments
    prefixes = read_prefix_config()
    for prefix in prefixes:
        s3_list = get_s3_files.get_file_list(prefix)
        print("--" + prefix + "--")
        print(s3_list)
        for s3_url in s3_list:
            pattern = "https:.*\/(.*\.h5)"
            match = re.search(pattern, s3_url)
            filename = match.group(1)
            bescmd_filename = create_bescmd(s3_url, filename)
            datafile = open("results/" + filename + ".dap", "w+")
            logfile = open("results/" + filename + ".log", "w+")
            result = subprocess.run(["besstandalone", " -c bes.conf", f" -i {bescmd_filename}"],
                                    stdout=datafile, stderr=logfile)
            if result.returncode != 0:
                print(f"Error running besstandalone {result.args}")
        print("----------")


if __name__ == "__main__":
    main()