import datetime

import requests
from django.db import models
from django.contrib.auth.models import User


# https://medium.com/djangotube/django-roles-groups-and-permissions-introduction-a54d1070544
# Create Groups
# Assign the set of permissions to that group
# Assign a user to groups
# Check user in the group


class SearchPhrase(models.Model):
    keyword = models.CharField('phrase', max_length=500)

    def __str__(self):
        return f'{self.keyword}'


class UserSearchPhrase(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_search_phrases')
    search_phrase = models.ForeignKey(SearchPhrase, on_delete=models.CASCADE, related_name='user_search_phrases')
    search_count = models.PositiveIntegerField('search count', default=1)

    def __str__(self):
        return f'user: {self.user}, search_phrase: {self.search_phrase}, search_count: {self.search_count}'


class Source(models.Model):
    source_id = models.CharField('source id', max_length=100, blank=True, null=True, default=None)
    source_name = models.CharField('source name', max_length=100, blank=True, null=True)

    def __str__(self):
        return f'source_id: {self.source_id}, source_name: {self.source_name}'


class News(models.Model):
    author = models.CharField('author', max_length=200, blank=True, null=True)
    title = models.CharField('title', max_length=1000, blank=True, null=True)
    description = models.TextField('description', blank=True, null=True)
    news_url = models.URLField('news url', blank=True, null=True)
    image_url = models.URLField('image url', blank=True, null=True)
    publishedAt = models.DateTimeField('published at', null=True)
    content = models.TextField('content', blank=True, null=True)
    source = models.ForeignKey(Source, on_delete=models.SET_NULL, null=True, related_name='news')
    search_phrase = models.ForeignKey(SearchPhrase, on_delete=models.SET_NULL, null=True, related_name='news')

    def __str__(self):
        return f'title: {self.title}, author: {self.author}, publishedAt: {self.publishedAt}'


def get_news_from_api(keyword, from_date=None, to_date=None, page_size=50, current_page=1):
    """
    fetch data from 3rd party api
    """
    news_data = {'keyword': keyword, 'data': [], 'status': 'error', 'message': None, 'page_size': page_size, 'total_pages': 0, 'current_page': current_page}
    total_results = 0
    try:
        url = 'https://newsapi.org/v2/everything?apiKey=0b5d798e87074381917b314f2fc1b3b8'  # b28247348af64f059a0433425517ee5f'
        url += f'&q={keyword}&sortBy=publishedAt&pageSize={page_size}&page={current_page}'
        if from_date:
            url += f'&from={from_date}'
        if to_date:
            url += f'&to={to_date}'

        response = requests.request('get', url=url)
        data = response.json()
        if data['status'] == 'ok':
            news_data.update({'data': data['articles'],  'status': data.pop('status')})
            total_results = data.pop('totalResults')
        else:
            news_data['message'] = data.pop('message')

        if page_size > 0:
            total_pages = total_results // page_size
            news_data['total_pages'] = total_pages + 1 if (total_results % page_size) > 0 else total_pages

    except Exception as e:
        print(e)
    return news_data['status'] == 'ok', news_data


def load_data_from_api(keyword, data):
    """
    save data to local database if not exists
    """
    newly_created = 0
    try:
        if keyword:
            search_phrase, f = SearchPhrase.objects.get_or_create(keyword=str(keyword).lower())

            for i in data:
                source_id = i['source']['id'].lower() if i['source']['id'] else None
                source_name = i['source']['name'].lower() if i['source']['name'] else None
                source, f = Source.objects.get_or_create(source_id=source_id, source_name=source_name)
                if source:
                    published_at = datetime.datetime.strptime(i['publishedAt'], '%Y-%m-%dT%H:%M:%SZ')
                    author = i['author'].title() if i['author'] else None
                    title = i['title'].title() if i['title'] else None
                    news = News.objects.filter(author=author, title=title, publishedAt=published_at)
                    if not news:
                        news = News.objects.create(
                            author=author,
                            title=title,
                            description=i['description'],
                            news_url=i['url'],
                            image_url=i['urlToImage'],
                            publishedAt=published_at,
                            content=i['content'],
                            source=source,
                            search_phrase=search_phrase
                        )
                        newly_created += 1
    except Exception as e:
        print(e)
    return newly_created


def save_to_local_db(keyword):
    """
    saving all keyword related data regardless of from & to date to the local db.
    """
    newly_created = 0
    f = True
    current_page = 1
    while f:
        f, data = get_news_from_api(keyword=keyword, current_page=current_page)
        current_page += 1
        newly_created += load_data_from_api(keyword=keyword, data=data['data'])
    return newly_created
