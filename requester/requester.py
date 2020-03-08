import mimetypes
import re
import argparse
import requests
import sys
import base64
import random
import validators
import cfscrape


class Requester:
    def __init__(self):
        self._base64data = None
        self._base64 = False
        self._init_argument_parse()
        self._validate_resource_url()
        self._validate_bypass_method()

    def download_resource(self):
        filename = "./"
        data = ""
        data_length = 0
        if self._is_bas64():
            filename = random_filename()
            content_type = self._get_base64data().get_content_type()
            if "image".lower() in content_type:
                filename = filename + "." + content_type.split("/")[1]
            data = base64.decodebytes(self._get_base64data().get_data())
            data_length = len(data)
        else:
            response = self._get_request_maker().get(self.get_resource_url())
            if response.status_code == 200:
                filename = self._get_filename_from_requests(response)
                data = response.iter_content(1024)
                data_length = len(response.content)
            else:
                print("Error: response code:" + str(response.status_code), file=sys.stderr)
                if response.status_code == 503:
                    print("503.. Maybe try a firewall bypass method [-f | --firewall-bypass] basic ")
                exit(1)
        with open(filename, 'wb') as f:
            current = 0
            print("Downloading File:" + filename)
            for block in data:
                _print_download_status(current, data_length)
                f.write(block)
                if self._is_bas64():
                    current = current + 1
                else:
                    current = current + 1024
                    if current > data_length:
                        current = data_length
                _print_download_status(current, data_length)
            f.close()
        return filename

    def _is_bas64(self):
        return self._base64

    def _get_filename_from_requests(self, response):
        extension = ""
        if "Content-Type" in response.headers.keys():
            content_type = response.headers['content-type']
            extension = mimetypes.guess_extension(content_type.partition(';')[0].strip(), strict=False)
        if "Content-Disposition" in response.headers.keys():
            return re.findall("filename=(.+)", response.headers["Content-Disposition"])[0].replace(extension, "") + extension
        else:
            return self.get_resource_url().split("/")[-1].replace(extension, "") + extension

    def _get_argument_parser(self):
        return self._arg_parser

    def _init_argument_parse(self):
        self._arg_parser = argparse.ArgumentParser(description="Downloads web resources")
        self._arg_parser.add_argument('resource', metavar='resource_url', nargs=1, default=None)
        self._arg_parser.add_argument('--firewall-bypass', '-f', metavar='bypass_method', dest='firewall_bypass', default=None)
        self._args = self._arg_parser.parse_args()
        self._resource_url = self._get_arguments().resource[0]

    def print_usage(self, io=sys.stderr):
        self._arg_parser.print_usage(io)

    def _get_request_maker(self):
        return self._request_maker

    def _get_arguments(self):
        return self._args

    def get_resource_url(self):
        return self._resource_url

    def _get_base64data(self):
        if self._is_bas64():
            return self._base64data
        return None

    def _validate_bypass_method(self):
        session = requests.Session()
        method = self._get_arguments().firewall_bypass
        if method == "basic":
            self._request_maker = cfscrape.create_scraper(sess=session)
        elif method is None:
            self._request_maker = session
        else:
            print("Error", file=sys.stderr)

    def _validate_resource_url(self):
        if " " in self._resource_url:
            self.print_usage()
            print("Error: Whitespaces are not alowed in a URL", file=sys.stderr)
            exit(1)
        if len(self._resource_url) == 0:
            print("Warning: No URL specified")
        if self.get_resource_url().lower().startswith("data"):
            self._base64 = True
            self._base64data = Base64data(self.get_resource_url().split(",", 1)[1])
            content_type = self.get_resource_url().split(":", 1)[1].split(';', 1)[0].split(',', 1)[0]
            if len(content_type) > 0:
                self._get_base64data().set_content_type(content_type)
        elif not validators.url(self.get_resource_url()):
            print("Error: Please specify a valid URI", file=sys.stderr)
            exit(1)


class Base64data:

    def __init__(self, data=None, content_type=None):
        self._content_type = content_type
        self._data = data

    def get_content_type(self):
        return self._content_type

    def get_data(self):
        return self._data

    def set_content_type(self, content_type):
        self._content_type = content_type


def _print_download_status(current, total):
    if total is None:  # no content length header
        return
    else:
        done = int(50 * current / total)
        sys.stdout.write("\r[%s%s]" % ('=' * done, ' ' * (50 - done)) + str(current) + "B/" + str(total) + "B")
        sys.stdout.flush()


def random_filename():
    return ''.join([chr(random.randint(65, 90)) for _ in range(16)])
