import pytest
from pytest_django.asserts import assertRedirects
from pytest_lazyfixture import lazy_fixture as ls

from news.pytest_tests.conftest import STATUS_CODE_200, STATUS_CODE_404

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    ('url', 'parametrized_client', 'status'),
    (
        (
            ls('url_home_news'),
            ls('client'),
            STATUS_CODE_200
        ),
        (
            ls('url_detail_news'),
            ls('client'),
            STATUS_CODE_200
        ),
        (
            ls('url_users_login'),
            ls('client'),
            STATUS_CODE_200
        ),
        (
            ls('url_users_logout'),
            ls('client'),
            STATUS_CODE_200
        ),
        (
            ls('url_users_signup'),
            ls('client'),
            STATUS_CODE_200
        ),
        (
            ls('url_edit_comment'),
            ls('not_author_client'),
            STATUS_CODE_404
        ),
        (
            ls('url_delete_comment'),
            ls('not_author_client'),
            STATUS_CODE_404
        ),
        (
            ls('url_edit_comment'),
            ls('author_client'),
            STATUS_CODE_200
        ),
        (
            ls('url_delete_comment'),
            ls('author_client'),
            STATUS_CODE_200
        ),
    )
)
def test_page_availability(url, parametrized_client, status):
    """Проверка доступности страниц."""
    response = parametrized_client.get(url)
    assert response.status_code == status


@pytest.mark.parametrize(
    'url',
    (
        ls('url_edit_comment'),
        ls('url_delete_comment'),
    )
)
def test_redirects(client, url_users_login, url):
    """Проверка редиректа для анонима."""
    expected_url = f'{url_users_login}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
