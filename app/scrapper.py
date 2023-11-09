from datetime import datetime
from typing import Any

import requests
from bs4 import BeautifulSoup as Soup
from pytz import timezone, UTC

URL = 'https://www.reuters.com'
TIMEZONE = 'Africa/Kampala'


def pages(page: str) -> dict[Any]:
    request = requests.get(f'{URL}/{page}')
    html = Soup(request.content, 'html.parser')
    # buttons with attr data test id = TextButton
    buttons = html.find_all('button', {'data-testid': 'TextButton'})
    data = []

    for (index, button) in enumerate(buttons):
        row = {'id': index + 1, 'name': None, 'description': None, 'query': None}
        if button.has_attr('data-id'):
            (_, category) = button['data-id'].strip('/').split('/')
            row['name'] = category
            row['description'] = button.text
            row['query'] = f'?page={page}&category={category}'
            data.append(row)
    return {'total': len(data), 'page': page, 'items': data}


def feeds(page: str, category: str) -> dict[Any]:
    req = requests.get(f'{URL}/{page}/{category}')
    html = Soup(req.content, 'html.parser')
    # get all divs with data-testid="MediaStoryCard"
    cards = html.find_all('li', id=True)
    data = []
    for (index, card) in enumerate(cards):
        row = {'id': card['id'], 'category': None, 'title': None, 'link': None, 'image': None, 'datetime': None}
        # get image url
        image = card.find('img')
        row['image'] = image['src'] if image else None
        # get heading and a link
        h3 = card.find('h3', {'data-testid': 'Heading'})
        if h3:
            row['title'] = h3.text
            a = h3.find('a', {'data-testid': 'Link'})
            row['link'] = a['href']
        label = card.find('span', {'data-testid': 'Label'})
        if label:
            row['category'] = label.text.replace('category', '')
            if '·' in row['category']:
                row['category'] = row['category'].split('·')[0].strip()
        if row['title']:
            data.append(row)
        time = card.find('time', {'data-testid': 'Label'})
        if time:
            row['datetime'] = time['datetime']
            date = datetime.strptime(row['datetime'], "%Y-%m-%dT%H:%M:%SZ")
            date_utc = date.replace(tzinfo=UTC)
            row['datetime_utc'] = date_utc.astimezone(timezone(TIMEZONE))
            row['datetime'] = date
    return {
        'total': len(data), 'source': URL, 'page': page,
        'category': category, 'items': data
    }
