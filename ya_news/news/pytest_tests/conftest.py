from datetime import timedelta
from django.urls import reverse
from django.utils import timezone
from django.conf import settings
import pytest

from django.test.client import Client

from news.models import News, Comment
from news.forms import BAD_WORDS


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
def news_id_for_args(news):
    return (news.id, )


@pytest.fixture
def comment(news, author):
    comment = Comment.objects.create(
        text='Какой-то текст',
        author=author,
        news=news
    )
    return comment


@pytest.fixture
def comment_id_for_args(comment):
    return (comment.id, )


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
    all_comments = [
        Comment(
            text='Комментарий {index}',
            created=today - timedelta(days=index),
            author=author,
            news=news,
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE)
    ]
    Comment.objects.bulk_create(all_comments)
    return (news.id, )


@pytest.fixture
def url_for_detail_news(news):
    return reverse('news:detail', args=(news.id, ))


@pytest.fixture
def url_and_object_for_edit_comment(comment):
    return (comment, reverse('news:edit', args=(comment.id, )))


@pytest.fixture
def url_for_delete_comment(comment):
    return reverse('news:delete', args=(comment.id, ))


@pytest.fixture(scope='session')
def form_for_create_comment():
    return {'text': 'Новый комментарий'}


@pytest.fixture(scope='session')
def form_for_edit_comment():
    return {'text': 'Отредактированный комментарий'}


@pytest.fixture(scope='session')
def form_for_create_comment_with_bad_words():
    return {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}


@pytest.fixture(scope='session')
def url_home():
    return reverse('news:home')


@pytest.fixture
def url_to_comments(url_for_detail_news):
    return url_for_detail_news + '#comments'
