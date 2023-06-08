
import get_s3_files
import xml.dom.minidom as minidom
import regex as re
import subprocess
import os
import time
import configparser

verbose: bool = False
version = 1
bes_conf = ''
s3_url = ''
docker: bool = False


class TestResult:
    def __init__(self, status, code):
        self.status = status
        self.code = code
        self.message = 'NA'
        self.data_payload = 'NA'
        self.log_payload = 'NA'
        self.datafile_name = 'NA'
        self.logfile_name = 'NA'


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


def load_config(bes_run):
    parser = configparser.RawConfigParser()
    configfilepath = r'config.txt'
    parser.read(configfilepath)

    if bes_run == 1:
        build_path = parser.get("besstandalone", "path_build")
        deps_path = parser.get("besstandalone", "path_deps")
        print("     config : " + build_path) if verbose else ''
        print("     config : " + deps_path) if verbose else ''
        os.environ["PATH"] += os.pathsep + os.pathsep.join([build_path])
        os.environ["PATH"] += os.pathsep + os.pathsep.join([deps_path])
        # print("PATH : " + os.environ["PATH"])

    global bes_conf
    bes_conf = parser.get("besconf", "path")
    print("     bes.conf path: " + bes_conf) if verbose else ''

    global s3_url
    s3_url = parser.get("s3url", "url")
    print("     s3 url: " + s3_url) if verbose else ''


def check_besstandalone():
    success = 0
    try:
        run_result = subprocess.run(["besstandalone", "--version"])
        if run_result.returncode != 0:
            print(f"    /!\\ Error running besstandalone : {run_result.args}") if verbose else ''
            success = 1
    except Exception as e:
        print("    /!\\ besstandalone unreachable, load config.txt") if verbose else ''
        success = 1
    return success


def read_prefix_config():
    # Using readlines()
    file1 = open('prefixs.txt', 'r')
    raw_prefixes = file1.readlines()
    file1.close()
    prefixes = []
    count = 0

    # Strips the newline character
    for prefix in raw_prefixes:
        count += 1
        prefixes.append(prefix.strip())
        # print("Line {}: {}".format(count, prefix.strip()))

    return prefixes


def create_bescmd(url, filename, prefix):
    bescmd = doc_template.replace("URL_TEMPLATE", url)
    root = minidom.parseString(bescmd)
    # print(root.toprettyxml())
    xml_str = root.toprettyxml(indent="\t", encoding="UTF-8")
    save_path_file = "./bescmds/" + prefix + "-" + filename + ".bescmd"
    # print(xml_str)
    with open(save_path_file, "w+b") as f:
        f.write(xml_str)
    f.close()
    return save_path_file


def check_data_file(tr):
    pattern = "Message:(.*)"
    with open(tr.datafile_name, "r", encoding='ISO-8859-1') as evalfile:
        for line in evalfile:
            match = re.search(pattern, line)
            if match:
                tr.status = "fail"
                tr.code = 500
                msg = match.group(1).strip()
                tr.message = msg
                # print(msg)
                subpattern = "HTTP status of (\d{3}) which means (.*)"
                submatch = re.search(subpattern, msg)
                if submatch:
                    tr.code = submatch.group(1)
                    tr.message = submatch.group(2)
                    tr.data_payload = msg
                break
    # print("\n")
    evalfile.close()
    return tr


def check_log_file(tr):
    if os.stat(tr.logfile_name).st_size == 0:
        return tr
    else:
        logs = ""
        with open(tr.logfile_name, "r") as logfile:
            for line in logfile:
                logs += line
        logfile.close()
        if len(logs) != 0:
            tr.log_payload = logs
            # print("logs : " + tr.log_payload)
        return tr


def call_s3_reader(filename, bescmd_filename, prefix):
    tr = TestResult("pass", 200)

    datafile_name = "results/" + prefix + "-" + filename + ".dap"
    tr.datafile_name = datafile_name

    logfile_name = "results/" + prefix + "-" + filename + ".log"
    tr.logfile_name = logfile_name

    datafile = open(datafile_name, "w+")
    logfile = open(logfile_name, "w+")
    if docker:
        try:
            user = os.getenv('CMAC_ID')
            password = os.environ.get('CMAC_ACCESS_KEY')
            region = os.getenv('CMAC_REGION')
            url = os.getenv('CMAC_URL')
            run_result = subprocess.run(["docker", "exec",
                                         "--env", f"CMAC_URL={url}",
                                         "--env", f"CMAC_REGION={region}",
                                         "--env", f"CMAC_ACCESS_KEY={password}",
                                         "--env", f"CMAC_ID={user}",
                                         "besd", "besstandalone",
                                         f"--config={bes_conf}",
                                         f"--inputfile={bescmd_filename}"],
                                        stdout=datafile, stderr=logfile)
            if run_result.returncode != 0:
                print(f"    /!\\ Error running docker : {run_result.args}")
                tr.status = "error"
                tr.code = 500
                tr.message = str(run_result)
        except Exception as e:
            print(f"    /!\\ Error running docker : {e}")
            tr.status = "error"
            tr.code = 666
            tr.message = str(e)
    else:
        try:
            run_result = subprocess.run(["besstandalone", f"--config={bes_conf}", f"--inputfile={bescmd_filename}"],
                                        stdout=datafile, stderr=logfile)
            if run_result.returncode != 0:
                print(f"    /!\\ Error running besstandalone : {run_result.args}")
                tr.status = "error"
                tr.code = 500
                tr.message = str(run_result)
        except Exception as e:
            print(f"    /!\\ Error running besstandalone : {e}")
            tr.status = "error"
            tr.code = 666
            tr.message = str(e)

    logfile.close()
    datafile.close()

    return tr


def print_out_test_result(tr):
    print("     Status : " + tr.status)
    print("     Code : " + str(tr.code))
    print("     Message : " + tr.message)
    print("     data_payload : " + tr.data_payload)
    print("     log payload : " + tr.log_payload)


def write_xml_document(prefix, ver, results):
    # make the response document
    root = minidom.Document()

    xsl_element = root.createProcessingInstruction("xml-stylesheet",
                                                   "type='text/xsl' href='pyreader_details.xsl'")
    root.appendChild(xsl_element)

    prov = root.createElement('DACC')
    prov.setAttribute('name', prefix)
    prov.setAttribute('date', time.asctime())
    root.appendChild(prov)

    for key in results.keys():
        url = key
        pattern = "https:.*\/(.*\.h5)"
        match = re.search(pattern, url)
        filename = match.group(1)

        # XML element for the collection
        collection = root.createElement('File')
        collection.setAttribute('name', filename)
        collection.setAttribute('url', url)
        prov.appendChild(collection)

        # Add XML for all the tests we ran
        test_result = results[key]

        test = create_attribute(root, test_result)
        collection.appendChild(test)

        if test_result.data_payload != "NA":
            test = root.createElement('Info')
            test.setAttribute('message', test_result.data_payload)
            collection.appendChild(test)

        if test_result.log_payload != "NA":
            test = root.createElement('Logs')
            test.setAttribute('message', test_result.log_payload)
            collection.appendChild(test)

    # Save the XML
    xml_str = root.toprettyxml(indent="\t")
    save_path_file = "xml/" + prefix + time.strftime("-%m.%d.%Y-") + ver + ".xml"
    with open(save_path_file, "w") as f:
        f.write(xml_str)
    f.close()


def create_attribute(root, result):
    test = root.createElement('Result')
    test.setAttribute('status', result.status)
    test.setAttribute('code', str(result.code))
    test.setAttribute('message', result.message)
    return test


def main():
    import argparse  # for parsing arguments
    parser = argparse.ArgumentParser(description="Query S3 bucket for a list of *.h5 files, create *.bescmd files,"
                                                 " call besstandalone with the *.bescmd, save the response to a file,"
                                                 " finally check the response file and save results to xml file")
    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true", default=False)
    parser.add_argument("-V", "--version", help="version number for output files", default="1")
    parser.add_argument("-D", "--docker", help="use 'docker exec besd ...' command", default=False)
    args = parser.parse_args()

    global verbose
    verbose = args.verbose
    global version
    version = args.version
    global docker
    docker = args.docker

    bes_run = check_besstandalone()
    load_config(bes_run)

    global s3_url
    url = s3_url

    prefixes = read_prefix_config()
    for prefix in prefixes:
        if prefix[0] == '#':
            continue

        prefix_list = {}
        print("\n|-|-|-|-|-|-|-|-|-|- " + prefix + " -|-|-|-|-|-|-|-|-|-|\n") if verbose else ''
        print("calling 'get_s3_files.get_file_list(...)'") if verbose else ''
        s3_list = get_s3_files.get_file_list(prefix, url)
        print("     # of files found: " + str(len(s3_list))) if verbose else ''

        if len(s3_list) == 0:
            tr = TestResult("pass", 200)
            tr.log_payload = "No files found in \"" + prefix + "\" S3 bucket."
            prefix_list["https:foo/Empty Bucket.h5"] = tr

        for s3_url in s3_list:
            pattern = "https:.*\/(.*\.h5)"
            match = re.search(pattern, s3_url)
            filename = match.group(1)

            print("|---------- filename: " + filename + " ----------|") if verbose else print('.', end="", flush=True)
            print("calling 'create_bescmd(...)'") if verbose else ''
            bescmd_filename = create_bescmd(s3_url, filename, prefix)
            print("     bescmd file: " + bescmd_filename) if verbose else ''

            print("calling 'call_s3_reader(...)'") if verbose else ''
            tr = call_s3_reader(filename, bescmd_filename, prefix)
            if verbose:
                print_out_test_result(tr)

            print("calling 'check_data_file(...)'") if verbose else ''
            if tr.status == 'pass':
                tr = check_data_file(tr)
            if verbose:
                print_out_test_result(tr)

            print("calling 'check_log_file(...)'") if verbose else ''
            tr = check_log_file(tr)
            if verbose:
                print_out_test_result(tr)

            prefix_list[s3_url] = tr

            print("|____________________ end ____________________|\n") if verbose else ''
        write_xml_document(prefix, str(version), prefix_list)
        print("\n|-|-|-|-|-|-|-|-|-|-|-|-|-|- end -|-|-|-|-|-|-|-|-|-|-|-|-|-|\n") if verbose \
            else print('|', end="", flush=True)


if __name__ == "__main__":
    main()
