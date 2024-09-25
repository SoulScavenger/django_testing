from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    ('url', 'parametrized_client', 'status'),
    (
        (
            pytest.lazy_fixture('url_home_news'),
            pytest.lazy_fixture('client'),
            HTTPStatus.OK
        ),
        (
            pytest.lazy_fixture('url_detail_news'),
            pytest.lazy_fixture('client'),
            HTTPStatus.OK
        ),
        (
            pytest.lazy_fixture('url_users_login'),
            pytest.lazy_fixture('client'),
            HTTPStatus.OK
        ),
        (
            pytest.lazy_fixture('url_users_logout'),
            pytest.lazy_fixture('client'),
            HTTPStatus.OK
        ),
        (
            pytest.lazy_fixture('url_users_signup'),
            pytest.lazy_fixture('client'),
            HTTPStatus.OK),
        (
            pytest.lazy_fixture('url_edit_comment'),
            pytest.lazy_fixture('not_author_client'),
            HTTPStatus.NOT_FOUND
        ),
        (
            pytest.lazy_fixture('url_delete_comment'),
            pytest.lazy_fixture('not_author_client'),
            HTTPStatus.NOT_FOUND
        ),
        (
            pytest.lazy_fixture('url_edit_comment'),
            pytest.lazy_fixture('author_client'),
            HTTPStatus.OK
        ),
        (
            pytest.lazy_fixture('url_delete_comment'),
            pytest.lazy_fixture('author_client'),
            HTTPStatus.OK
        ),
    )
)
def test_page_availability(url, parametrized_client, status):
    """Проверка доступности страниц."""
    response = parametrized_client.get(url)
    assert response.status_code == status


@pytest.mark.parametrize(
    'url_login',
    (
        pytest.lazy_fixture('url_users_login'),
    )
)
@pytest.mark.parametrize(
    'url',
    (
        pytest.lazy_fixture('url_edit_comment'),
        pytest.lazy_fixture('url_delete_comment'),
    )
)
def test_redirects(client, url_login, url):
    """Проверка редиректа для анонима."""
    expected_url = f'{url_login}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
