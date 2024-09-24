from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    ('name', 'args'),
    (
        ('news:home', None),
        ('news:detail', pytest.lazy_fixture('news_id_for_args')),
        ('users:login', None),
        ('users:logout', None),
        ('users:signup', None),
    )
)
def test_home_availability_for_anonymous_user(name, client, args):
    """Проверка доступа к страницам для анонимного пользователя."""
    url = reverse(name, args=args)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    ('name', 'args'),
    (
        ('news:edit', pytest.lazy_fixture('comment_id_for_args')),
        ('news:delete', pytest.lazy_fixture('comment_id_for_args')),
    )
)
def test_redirects(name, client, args):
    """Проверка редиректа для анонима."""
    login_url = reverse('users:login')
    url = reverse(name, args=args)
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)


@pytest.mark.parametrize(
    ('parametrized_client', 'comment_id', 'expected_status'),
    (
        (
            pytest.lazy_fixture('not_author_client'),
            pytest.lazy_fixture('comment_id_for_args'),
            HTTPStatus.NOT_FOUND),
        (
            pytest.lazy_fixture('author_client'),
            pytest.lazy_fixture('comment_id_for_args'),
            HTTPStatus.OK
        )
    ),
)
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete', ),
)
def test_pages_availability_for_different_users(
        name, parametrized_client, comment_id, expected_status
):
    """Проверка доступа к редактированию комментария."""
    url = reverse(name, args=(comment_id))
    response = parametrized_client.get(url)
    assert response.status_code == expected_status