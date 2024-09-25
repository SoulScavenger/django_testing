from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects
from pytest_lazyfixture import lazy_fixture as lf

pytestmark = pytest.mark.django_db

STATUS_CODE_200 = HTTPStatus.OK
STATUS_CODE_404 = HTTPStatus.NOT_FOUND


@pytest.mark.parametrize(
    ('url', 'parametrized_client', 'status'),
    (
        (
            lf('url_home_news'),
            lf('client'),
            STATUS_CODE_200
        ),
        (
            lf('url_detail_news'),
            lf('client'),
            STATUS_CODE_200
        ),
        (
            lf('url_users_login'),
            lf('client'),
            STATUS_CODE_200
        ),
        (
            lf('url_users_logout'),
            lf('client'),
            STATUS_CODE_200
        ),
        (
            lf('url_users_signup'),
            lf('client'),
            STATUS_CODE_200
        ),
        (
            lf('url_edit_comment'),
            lf('not_author_client'),
            STATUS_CODE_404
        ),
        (
            lf('url_delete_comment'),
            lf('not_author_client'),
            STATUS_CODE_404
        ),
        (
            lf('url_edit_comment'),
            lf('author_client'),
            STATUS_CODE_200
        ),
        (
            lf('url_delete_comment'),
            lf('author_client'),
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
        lf('url_edit_comment'),
        lf('url_delete_comment'),
    )
)
def test_redirects(client, url_users_login, url):
    """Проверка редиректа для анонима."""
    expected_url = f'{url_users_login}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
