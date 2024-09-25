from datetime import timedelta
from http import HTTPStatus

import pytest
from django.conf import settings
from django.test.client import Client
from django.urls import reverse
from django.utils import timezone

from news.models import Comment, News

STATUS_CODE_200 = HTTPStatus.OK
STATUS_CODE_404 = HTTPStatus.NOT_FOUND


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news():
    news = News.objects.create(
        title='Заголовок',
        text='Текст',
    )
    return news


@pytest.fixture
def comment(news, author):
    comment = Comment.objects.create(
        text='Какой-то текст',
        author=author,
        news=news
    )
    return comment


@pytest.fixture
def many_news():
    today = timezone.now()
    all_news = [
        News(
            title=f'Новость {index}',
            text='Просто текст',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    News.objects.bulk_create(all_news)


@pytest.fixture
def many_comments(news, author):
    today = timezone.now()
    for index in range(settings.NEWS_COUNT_ON_HOME_PAGE):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Комментарий {index}',
        )
        comment.created = today + timedelta(days=index)
        comment.save()


@pytest.fixture(scope='session')
def url_home_news():
    return reverse('news:home')


@pytest.fixture
def url_detail_news(news):
    return reverse('news:detail', args=(news.id, ))


@pytest.fixture
def url_edit_comment(comment):
    return reverse('news:edit', args=(comment.id, ))


@pytest.fixture
def url_delete_comment(comment):
    return reverse('news:delete', args=(comment.id, ))


@pytest.fixture(scope='session')
def url_users_login():
    return reverse('users:login')


@pytest.fixture(scope='session')
def url_users_logout():
    return reverse('users:logout')


@pytest.fixture(scope='session')
def url_users_signup():
    return reverse('users:signup')


@pytest.fixture
def url_to_comments(url_detail_news):
    return url_detail_news + '#comments'
