#!/usr/bin/env python

# Upload files named on ARGV as Slack emoji.
# https://github.com/smashwilson/slack-emojinator

import os
import re
import sys
import requests

from bs4 import BeautifulSoup

team_name = os.getenv('SLACK_TEAM')
cookie = os.getenv('SLACK_COOKIE')

url = "https://{}.slack.com/customize/emoji".format(team_name)
headers = {
    'Cookie': cookie,
}

def main():
    filename = sys.argv[1]
    emoji_name = sys.argv[2]
    print("Processing {}.".format(filename))

    upload_emoji(emoji_name, filename)
    print("{} upload complete.".format(filename))

def upload_emoji(emoji_name, filename):
    # Fetch the form first, to generate a crumb.
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    crumb = soup.find("input", attrs={"name": "crumb"})["value"]

    data = {
        'add': 1,
        'crumb': crumb,
        'name': emoji_name,
        'mode': 'data',
    }
    files = {'img': open(filename, 'rb')}
    r = requests.post(url, headers=headers, data=data, files=files, allow_redirects=False)
    r.raise_for_status()
    # Slack returns 200 OK even if upload fails, so check for status of 'alert_error' info box
    if 'alert_error' in r.content:
        soup = BeautifulSoup(r.text, "html.parser")
        crumb = soup.find("p", attrs={"class": "alert_error"})
        raise Exception("Error with uploading %s: %s" % (emoji_name, crumb.text))

if __name__ == '__main__':
    main()
