
import requests
import os
from aws_requests_auth.aws_auth import AWSRequestsAuth
import xml.dom.minidom as minidom
import regex as re


def build_creds():
    user = os.getenv('CMAC_ID')
    password = os.environ.get('CMAC_ACCESS_KEY')
    region = os.getenv('CMAC_REGION')

    auth = AWSRequestsAuth(aws_access_key=user,
                           aws_secret_access_key=password,
                           aws_host='s3-module-test-bucket.s3.us-west-2.amazonaws.com',
                           aws_region=region,
                           aws_service='s3')

    return auth


def get_file_list(prefix, s3_url):
    # s3_url = "https://s3-module-test-bucket.s3.us-west-2.amazonaws.com/"
    # resp = requests.get(s3_url, auth=auth, params=param)
    auth = build_creds()
    if prefix != '':
        param = {'prefix': prefix}
        resp = requests.get(s3_url, auth=auth, params=param)
    else:
        resp = requests.get(s3_url, auth=auth)

    # print(resp.status_code)
    # print(resp.text)
    # print("---------")

    dom1 = minidom.parseString(resp.text)
    keys = dom1.getElementsByTagName("Key")
    url_list = []
    for element in keys:
        e = element.firstChild.nodeValue
        # print(e)
        r = re.compile('.*\.h5$')
        if r.match(e):
            full_url = s3_url + e
            # print(full_url)
            url_list.append(full_url)
    # print("---------")

    return url_list


def main():
    import argparse  # for parsing arguments
    s3_list = get_file_list("test_folder")
    print(s3_list)
    # get_file_list("")


if __name__ == "__main__":
    main()
