#! /bin/python

from sys import argv
import subprocess
import json
import requests
from time import sleep
import os
import threading
import random

packages = argv[1:]
sourcePath = os.path.dirname(__file__) + "/src/"

def check(url):
    resp = requests.get("https://api.github.com/repos/" + url)
    return json.loads(resp.text)

def multithread(function, list_of_arg_lists):
    # for args in list_of_arg_lists:
    #   function(*args)
    # return
    threads = []
    for args in list_of_arg_lists:
        thread = threading.Thread(None, function, None, args)
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()

def install(url):
    if os.path.isfile(sourcePath + url + ".lock"):
        while os.path.isfile(sourcePath + url + ".lock"):
            sleep(0.1)
        return

    with open(sourcePath + url + ".lock", "w") as f:
        f.write(" ")

    resp = {"name": url} # check(url)

    if "message" in resp and resp['message'] == "Not Found":
        print("Repo " + "https://github.com/" + url + " not found")
        return

    print("Installing " + resp['name'] + "...")

    try:
        if(os.path.isdir(sourcePath + resp['name'])):
            subprocess.check_call(["git", "pull", "origin", "master"], cwd=sourcePath + resp['name'], stdout=subprocess.DEVNULL)
        else:
            subprocess.check_call(["git", "clone", "--quiet", "--recursive", "https://github.com/PetrolStation/" + url, sourcePath + resp['name']], stdout=subprocess.DEVNULL)
    except:
        while os.path.isfile(sourcePath + url + ".lock"):
            sleep(0.1)
    os.remove(sourcePath + url + ".lock")



if packages[0] == "*":
    print("Skipping installation (using packages from src/)")
    exit()


sleep(random.randint(0, 1000) / 1000)

multithread(install, [[package] for package in packages])
