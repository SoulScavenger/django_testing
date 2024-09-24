from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):
    """Класс проверки маршрутов."""

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Maksim')
        cls.reader = User.objects.create(username='User')
        cls.note = Note.objects.create(
            title='Заголовок', text='Текст', author=cls.author
        )

    def test_pages_availability(self):
        """Проверка доступа к главной странице и страницам аутентификации."""
        urls = (
            ('notes:home', None),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
        )
        for item in urls:
            name, args = item
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_to_note_list_add_success_add_for_auth_user(self):
        """Доступность к списку, добавлению, успешному добавлению."""
        self.client.force_login(self.author)
        urls = (
            ('notes:list', None),
            ('notes:add', None),
            ('notes:success', None)
        )
        for item in urls:
            name, args = item
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_to_note_detail_edit_and_delete_for_author(self):
        """Проверка доступа к просмотру/редактированию заметки"""
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        urls = (
            ('notes:detail', (self.note.slug, )),
            ('notes:edit', (self.note.slug, )),
            ('notes:delete', (self.note.slug, ))
        )
        for item in users_statuses:
            user, status = item
            self.client.force_login(user)
            for item in urls:
                name, args = item
                with self.subTest(name):
                    url = reverse(name, args=args)
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_not_auth_user(self):
        """Проверка редиректа для не аутентифицированного пользователя."""
        login_url = reverse('users:login')
        urls = (
            ('notes:list', None),
            ('notes:add', None),
            ('notes:success', None),
            ('notes:detail', (self.note.slug, )),
            ('notes:edit', (self.note.slug, )),
            ('notes:delete', (self.note.slug, ))
        )
        for item in urls:
            name, args = item
            with self.subTest(name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
