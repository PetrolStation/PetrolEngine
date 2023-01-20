#! /bin/python

from sys import argv
import subprocess
import json
import requests

packages = argv[1:]

def check(url):
    resp = requests.get("https://api.github.com/repos/" + url)
    return json.loads(resp.text)

def install(url):
    url = "PetrolStation/" + url

    resp = check(url)

    if "message" in resp and resp['message'] == "Not Found":
        print("Repo " + "https://github.com/" + url + " not found")
        return

    print("Installing " + resp['name'] + "...")

    subprocess.check_output(["git", "clone", "--recursive", "https://github.com/" + url, "src/" + resp['name']])


if packages[0] == "*":
    print("Skipping installation (using packages from src/)")
    exit()

for package in packages:
    install(package)