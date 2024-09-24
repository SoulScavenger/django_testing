from http import HTTPStatus

import pytest
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import WARNING
from news.models import Comment

pytestmark = pytest.mark.django_db


def test_anonymous_user_cant_create_comment(
        client, url_for_detail_news, form_for_create_comment
):
    """Проверка аноним не может создавать комментарии"""
    client.post(url_for_detail_news, data=form_for_create_comment)
    assert Comment.objects.count() == 0


def test_logged_user_can_create_comment(
        author_client, url_for_detail_news, form_for_create_comment):
    """Проверка пользователь может создавать комментарии."""
    author_client.post(url_for_detail_news, data=form_for_create_comment)
    assert Comment.objects.count() == 1


def test_user_cant_use_bad_words(
        author_client,
        url_for_detail_news,
        form_for_create_comment_with_bad_words
):
    """Проверка на запрет создание комментариев с бранью."""
    response = author_client.post(
        url_for_detail_news,
        data=form_for_create_comment_with_bad_words
    )
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )

    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_author_can_delete_comment(
        author_client,
        url_to_comments,
        url_for_delete_comment):
    """Автор комментария может удалить комментарий."""
    response = author_client.delete(url_for_delete_comment)
    assertRedirects(response, url_to_comments)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_user_cant_delete_comment_of_another_user(
        not_author_client,
        url_for_delete_comment
):
    """Не автор комментария не может удалить комментарий."""
    response = not_author_client.delete(url_for_delete_comment)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.count()
    assert comments_count == 1


def test_author_can_edit_comment(
        author_client,
        url_and_object_for_edit_comment,
        url_to_comments,
        form_for_edit_comment
):
    """Автор комментария может изменить комментарий."""
    comment, url = url_and_object_for_edit_comment
    response = author_client.post(url, data=form_for_edit_comment)
    assertRedirects(response, url_to_comments)
    comment.refresh_from_db()
    assert comment.text == form_for_edit_comment['text']


def test_user_cant_edit_comment_of_another_user(
        not_author_client,
        url_and_object_for_edit_comment,
        form_for_edit_comment):
    comment, url = url_and_object_for_edit_comment
    response = not_author_client.post(url, data=form_for_edit_comment)

    assert response.status_code == HTTPStatus.NOT_FOUND

    comment.refresh_from_db()

    assert comment.text != form_for_edit_comment['text']
