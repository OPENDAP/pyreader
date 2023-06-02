import unittest
import filecmp
import time
import regex as re
import driver


class DriverTests(unittest.TestCase):

    def test_load_config(self):
        driver.load_config(1)
        self.assertEqual(driver.bes_conf, "./bes.conf")
        self.assertEqual(driver.s3_url, "https://s3-module-test-bucket.s3.us-west-2.amazonaws.com/")

    def test_read_prefix_config(self):
        prefixes = driver.read_prefix_config()
        self.assertEqual(len(prefixes), 3)
        self.assertEqual(prefixes[0], "test_folder")

    def test_create_bescmd(self):
        bescmd_path = driver.create_bescmd("https://test_url/", "test_file", "unittest")
        # print(bescmd_path)
        baseline_path = "./bescmds/baseline.bescmd"
        result = filecmp.cmp(bescmd_path, baseline_path, shallow=False)
        # print(result)
        self.assertEqual(True, result)

    def test_check_data_files(self):
        tr = driver.TestResult("pass", 200)
        tr.datafile_name = "./results/baseline.dap"
        tr = driver.check_data_file(tr)
        self.assertEqual(tr.status, "fail")
        self.assertEqual(tr.code, '404')
        self.assertEqual(tr.message, "Not Found: The underlying data source or server could not be found.")

    def test_check_log_file(self):
        tr = driver.TestResult("fail", 500)
        tr.logfile_name = "./results/baseline.log"
        tr = driver.check_log_file(tr)
        self.assertEqual(tr.log_payload, "this is the baseline.log text")

    def test_call_s3_reader(self):
        driver.load_config(1)
        tr = driver.call_s3_reader("s3_test", "./bescmds/s3_test.bescmd", "unittest")
        s3_baseline = "./results/s3_baseline.dap"
        result = filecmp.cmp(tr.datafile_name, s3_baseline, shallow=False)
        self.assertEqual(result, True)

    def test_write_xml_doc(self):
        results = {"https:unittest/test_entry_1.h5": driver.TestResult("pass", 200),
                   "https:unittest/test_entry_2.h5": driver.TestResult("fail", 500)}
        driver.write_xml_document("unittest", "1", results)
        save_path_file = "xml/unittest" + time.strftime("-%m.%d.%Y-") + "1.xml"

        xml_file = open(save_path_file, "r")
        xml_string = xml_file.read()
        xml_file.close()
        xml_string = re.sub('date=".*"', 'date="date"', xml_string)

        xml_file = open(save_path_file, "w")
        xml_file.write(xml_string)
        xml_file.close()

        result = filecmp.cmp(save_path_file, "xml/baseline.xml", shallow=False)
        self.assertEqual(result, True)


if __name__ == '__main__':
    unittest.main()
