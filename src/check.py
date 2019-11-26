import sys
import requests
import urllib.request
import time
from bs4 import BeautifulSoup
from enum import Enum

class Status(Enum):
    SUPPORTED = 1
    NOT_SUPPORTED = 0
    UNKNOWN = -1

    def desc(self):
        display_dict = {
            self.SUPPORTED: "True",
            self.NOT_SUPPORTED: "False",
            self.UNKNOWN: "Unknown"
        }
        return display_dict[self]

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
                if bit[2] != "Implementation":
                    supported.add(bit[2])
        except IndexError:
            pass
    return supported

def check_dependency(python_version, dependency, version=None):
    # When version is not specified the url automatically points to the 
    # newest version of the package
    print(f"CHECKING DEPENDENCY: {dependency}")
    response = get_and_process_response(get_url(dependency, version))
    if response is None:
        return Status.UNKNOWN, None
    else:
        soup = BeautifulSoup(response.text, "html.parser")
        python_bits = get_python_bits_from_soup(soup)
        supported_versions = get_supported_versions_from_python_bits(python_bits)
        if python_version in supported_versions:
            return Status.SUPPORTED, None
        else:
            return Status.NOT_SUPPORTED, supported_versions
         
def print_results(unknown, incompatible):    
    print("\n\n\n")
    print("################################")
    print("\n\n\n")

    if unknown:
        print(f"Could not get information on:")
        for key, value in unknown.items():
            print(f"{item}   Newest supported: {value}")

    if incompatible:
        print("\n\n\n")
        print("INCOMPATIBLE")
        for key, value in incompatible.items():
            print(f"{key}  Supported versions:{value['supported_versions']}   Newest version supported: {value['newest_supported']}")

    print("\n\n\n")
    print("################################")
    print("\n\n\n")


def check(python_version, filepath):
    unknown = {}
    incompatible = {}

    dependencies = get_dependencies_from_file(filepath)

    for dependency, version in dependencies:
        status, supported_versions = check_dependency(python_version, dependency, version)
        if status is not Status.SUPPORTED:
            # Check if the newest version is compatible 
            status_newest, _ = check_dependency(python_version, dependency)
            if status is Status.UNKNOWN:
                unknown[dependency] = {newest_supported: status_newest.desc()}
            else:
                incompatible[dependency] = {"supported_versions": supported_versions, "newest_supported": status_newest.desc()}
        time.sleep(0.5)

    return unknown, incompatible

if __name__=="__main__":
    python_version = sys.argv[1]
    filepath = sys.argv[2]
    unknown, incompatible = check(python_version, filepath)
    print_results(unknown, incompatible)
