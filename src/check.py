import sys
import requests
import urllib.request
import time
from bs4 import BeautifulSoup

def get_python_versions_from_response(response):
    pass

def get_and_process_response(url):
    response = requests.get(url)
    if response.status_code != 200:
        return None
    return response

def process_line(line):
    if line[0]=="#" or line[0]=="-":
        return None
    else:
        line = line.strip().split()
        if line:
            return line[0].split("==")
    return None


def get_dependencies_from_file(file):
    dependencies = []
    with open(file, "r") as f:
        for line in f:
            dep = process_line(line)
            if dep:
                dependencies.append((dep[0], dep[1]))
    return dependencies

def get_url(dependency, version=None):
    if version: 
        return f"https://pypi.org/project/{dependency}/{version}"
    return f"https://pypi.org/project/{dependency}/"

def get_python_bits_from_soup(soup):
    a_tags_in_sidebar = soup.select(".sidebar-section a")
    text_strings = [a.get_text() for a in a_tags_in_sidebar]
    python_bits = [text_string for text_string in text_strings if "Python" in text_string]
    return python_bits

def get_supported_versions_from_python_bits(python_bits):
    supported = set()
    for bit in python_bits:
        bit = bit.strip().split()
        try:
            if bit[1] == "::":
                supported.add(bit[2])
        except IndexError:
            pass
    return supported

def check(python_version, filepath):
    unknown = []
    incompatible = {}
    supported = []
    dependencies = get_dependencies_from_file(filepath)
    for dependency, version in dependencies:
        print(f"CHECKING DEPENDENCY: {dependency}")
        response = get_and_process_response(get_url(dependency, version))
        if response is None:
            unknown.append(dependency)
        else:
            soup = BeautifulSoup(response.text, "html.parser")
            python_bits = get_python_bits_from_soup(soup)
            supported_versions = get_supported_versions_from_python_bits(python_bits)
            if python_version in supported_versions:
                supported.append(dependency)
            else:
                new_version_response = get_and_process_response(get_url(dependency))
                if new_version_response is None:
                    newest_supported = "unknown"
                    newest_supported_versions = None
                else:
                    soup = BeautifulSoup(new_version_response.text, "html.parser")
                    python_bits = get_python_bits_from_soup(soup)
                    newest_supported_versions = get_supported_versions_from_python_bits(python_bits)
                    newest_supported = python_version in newest_supported_versions
                incompatible[dependency] = {"supported_versions": supported_versions, "newest_supported": newest_supported}
        time.sleep(0.5)

    print("\n\n\n")
    print("################################")
    print("\n\n\n")
    print(f"Could not get information on:")
    for item in unknown:
        print(item)

    print("\n\n\n")
    print("INCOMPATIBLE")
    for key, value in incompatible.items():
        print(f"{key}  {value}")

    print("\n\n\n")
    print("################################")
    print("\n\n\n")

if __name__=="__main__":
    python_version = sys.argv[1]
    filepath = sys.argv[2]
    check(python_version, filepath)
