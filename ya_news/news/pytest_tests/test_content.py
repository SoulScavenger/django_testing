import pytest
from django.conf import settings

from news.forms import CommentForm

pytestmark = pytest.mark.django_db


@pytest.mark.usefixtures('many_news')
def test_news_count(client, url_home_news):
    """Проверка количества новостей на странице."""
    response = client.get(url_home_news)
    object_list = response.context['object_list']
    news_count = object_list.count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.usefixtures('many_news')
def test_news_order(client, url_home_news):
    """Проверка сортировки новостей."""
    response = client.get(url_home_news)
    all_dates = [news.date for news in response.context['object_list']]
    sorted_dates = sorted(all_dates, reverse=True)
    assert sorted_dates == all_dates


@pytest.mark.usefixtures('many_comments')
def test_comments_order(client, url_detail_news):
    """Проверка сортировки комментариев."""
    response = client.get(url_detail_news)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert sorted_timestamps == all_timestamps


def test_anonymous_client_has_no_form(client, url_detail_news):
    """Проверка форма не доступна для анонима."""
    response = client.get(url_detail_news)
    assert 'form' not in response.context


def test_logged_user_has_form(author_client, url_detail_news):
    """Проверка форма доступна для аутентифицированного пользователя."""
    response = author_client.get(url_detail_news)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
