from bs4 import BeautifulSoup as bs
import requests
from itertools import groupby
from operator import attrgetter
from article import Article

import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

KEY_SLACK_TOKEN = os.environ.get('KEY_SLACK_TOKEN')
KEY_CHANNEL_ID = os.environ.get('KEY_CHANNEL_ID')

groupTitle = ''
articles = []

response = requests.get("https://androidweekly.net/")
html = bs(response.text, "html.parser")
date = html.find('a', {'href':'/issues/issue-584'}).get_text().strip()
items = html.find_all('div', {'class':'text-container galileo-ap-content-editor'})

for item in items:
    if (item.find('a') == None):
        title = item.span.get_text().strip()
        if (title != 'Sponsored'):
            groupTitle = title
        continue
    
    article = Article(
        group = groupTitle,
        title = item.a.get_text().replace('\n', '').strip(),
        desc = item.find_all('div')[-1].get_text().strip(),
        url = item.find('a', href=True)['href']
    )
    articles.append(article)

grouped = {group: list(items) for group, items in groupby(articles, attrgetter('group'))}
message = '금주 Android Weekly {} 입니다!\n\n'.format(date)

for group, items in grouped.items():
    message += '[ {} ]\n'.format(group)
    for index, item in enumerate(items):
        message += '{}. {}\n - 내용 : {}\n - 링크 : {}\n\n'.format(index + 1, item.title, item.desc, item.url)
    message += '\n\n'
  

# Send Data
client = WebClient(token=KEY_SLACK_TOKEN)
try:
    response = client.chat_postMessage(
        channel=KEY_CHANNEL_ID,
        text=message
    )
except SlackApiError as e:
    # You will get a SlackApiError if "ok" is False
    assert e.response["error"]    # str like 'invalid_auth', 'channel_not_found'