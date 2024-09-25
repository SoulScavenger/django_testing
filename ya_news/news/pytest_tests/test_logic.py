from http import HTTPStatus

import pytest
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

pytestmark = pytest.mark.django_db

FORM_FOR_CREATE_COMMENT = {'text': 'Новый комментарий'}
FORM_FOR_EDIT_COMMENT = {'text': 'Отредактированный комментарий'}
FORM_FOR_CREATE_COMMENT_WITH_BAD_WORDS = {
    'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'
}


def test_anonymous_user_cant_create_comment(
        client, url_detail_news
):
    """Проверка аноним не может создавать комментарии"""
    before_comment_count = Comment.objects.count()
    client.post(url_detail_news, data=FORM_FOR_CREATE_COMMENT)
    after_comment_count = Comment.objects.count()
    assert before_comment_count == after_comment_count


def test_logged_user_can_create_comment(
        author, author_client, url_detail_news):
    """Проверка пользователь может создавать комментарии."""
    before_comment_count = Comment.objects.count()
    author_client.post(url_detail_news, data=FORM_FOR_CREATE_COMMENT)
    after_comment_count = Comment.objects.count()
    comment = Comment.objects.get()
    news_id = int(url_detail_news.strip('/').split('/')[-1])

    assert before_comment_count < after_comment_count

    assert comment.news.id == news_id
    assert comment.text == FORM_FOR_CREATE_COMMENT['text']
    assert comment.author == author


def test_user_cant_use_bad_words(
        author_client,
        url_detail_news,
):
    """Проверка на запрет создание комментариев с бранью."""
    before_comment_count = Comment.objects.count()
    response = author_client.post(
        url_detail_news,
        data=FORM_FOR_CREATE_COMMENT_WITH_BAD_WORDS
    )
    after_comment_count = Comment.objects.count()
    assert before_comment_count == after_comment_count
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )


def test_author_can_delete_comment(
        author_client, url_to_comments, url_delete_comment
):
    """Автор комментария может удалить комментарий."""
    before_comment_count = Comment.objects.count()
    response = author_client.delete(url_delete_comment)
    assertRedirects(response, url_to_comments)
    after_comments_count = Comment.objects.count()
    assert before_comment_count > after_comments_count


def test_user_cant_delete_comment_of_another_user(
        not_author_client, url_delete_comment
):
    """Не автор комментария не может удалить комментарий."""
    before_comments_count = Comment.objects.count()
    response = not_author_client.delete(url_delete_comment)
    assert response.status_code == HTTPStatus.NOT_FOUND
    after_comments_count = Comment.objects.count()
    assert before_comments_count == after_comments_count


def test_author_can_edit_comment(
        author_client,
        url_and_object_for_edit_comment,
        url_to_comments,
):
    """Автор комментария может изменить комментарий."""
    comment, url = url_and_object_for_edit_comment
    response = author_client.post(url, FORM_FOR_EDIT_COMMENT)
    assertRedirects(response, url_to_comments)

    comment_from_db = Comment.objects.get(id=comment.id)

    assert comment.text != comment_from_db.text
    assert comment.author == comment_from_db.author
    assert comment.news == comment_from_db.news


def test_user_cant_edit_comment_of_another_user(
        not_author_client,
        url_and_object_for_edit_comment,
):
    comment, url = url_and_object_for_edit_comment
    response = not_author_client.post(url, data=FORM_FOR_EDIT_COMMENT)

    assert response.status_code == HTTPStatus.NOT_FOUND

    comment_from_db = Comment.objects.get(id=comment.id)

    assert comment.text == comment_from_db.text
    assert comment.author == comment_from_db.author
    assert comment.news == comment_from_db.news
