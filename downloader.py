#! /usr/bin/env python3

"""
Sækir dagskrárskjöl RÚV og geymir
"""

import requests
import github3
import datetime
import os

GITHUB_USER = "pallih"
GITHUB_REPO = "ruvdagskra"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")


CHANNELS = ["ruv", "ruv2", "ruvhd", "ras1", "ras2"]
FILETYPE = "xml"
BASEURL = "http://muninn.ruv.is/files/{}/{}/{}-{}-{}/"
DATA_FOLDER = "data"


def save_file_and_commit(channel, year, month, day, file_extension, content):
    gh = github3.login(token=GITHUB_TOKEN)
    repo = gh.repository(GITHUB_USER, GITHUB_REPO)
    folder_path = os.path.join(DATA_FOLDER, year, month, day)
    os.makedirs(folder_path, exist_ok=True)
    filename = "{}-{}-{}-{}{}".format(channel, year, month, day, file_extension)
    filepath = os.path.join(folder_path, filename)
    with open(filepath, "w") as f:
        f.write(content)
    message = "Added: {}".format(filename)
    commit = repo.create_file(filepath, message, content.encode('utf-8'))


def download_and_save(missing_files):
    saved = []
    for missing_file in missing_files:
        filename, file_extension = os.path.splitext(missing_file)
        channel, year, month, day = filename.split("-")
        r = requests.get(BASEURL.format(file_extension.replace(".", ""), channel, year, month, day))

        if r.status_code is not 404:
            save_file_and_commit(channel, year, month, day, file_extension, r.text)
            saved.append(missing_file)
    return saved


def find_missing_files():
    base = datetime.date.today()
    date_list = [base - datetime.timedelta(days=x) for x in range(0, 91)]
    expected = []
    for date in date_list:
        for channel in CHANNELS:
            expected.append("{}-{}-{}-{}.{}".format(channel, date.year, '{:02d}'.format(date.month), '{:02d}'.format(date.day), FILETYPE))
    os.makedirs(DATA_FOLDER, exist_ok=True)
    already_exists = []
    for dirpath, dirnames, filenames in os.walk(DATA_FOLDER):
        for filename in [f for f in filenames if f.endswith(".xml")]:
            already_exists.append(filename)
    missing = [item for item in expected if item not in already_exists]
    return missing


if __name__ == '__main__':
    missing_files = find_missing_files()
    if len(missing_files) is not 0:
        saved = download_and_save(missing_files)
        if len(saved) is not 0:
            message = "Added: {}".format(", ".join(saved))
            