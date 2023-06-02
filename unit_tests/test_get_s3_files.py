import unittest

import get_s3_files


class GetS3Files(unittest.TestCase):

    def test_get_file_list(self):
        s3_files = get_s3_files.get_file_list("test_folder",
                                              "https://s3-module-test-bucket.s3.us-west-2.amazonaws.com/")
        self.assertEqual(len(s3_files), 4)
        self.assertEqual(s3_files[0],
                         "https://s3-module-test-bucket.s3.us-west-2.amazonaws.com/test_folder/chunked_fourD.h5")

    def test_get_empty_prefix(self):
        s3_files = get_s3_files.get_file_list("empty_folder",
                                              "https://s3-module-test-bucket.s3.us-west-2.amazonaws.com/")
        self.assertEqual(len(s3_files), 0)


if __name__ == '__main__':
    unittest.main()
