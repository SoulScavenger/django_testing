from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class BaseFixtures(TestCase):

    STATUS_200 = HTTPStatus.OK
    STATUS_404 = HTTPStatus.NOT_FOUND

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.not_author = User.objects.create(username='Не автор')
        cls.note = Note.objects.create(title='Заметка',
                                       text='Просто текст',
                                       author=cls.author
                                       )
        cls.author_client = Client()
        cls.not_author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.not_author_client.force_login(cls.not_author)
        cls.urls_for_not_logged_user = {
            'home': reverse('notes:home'),
            'login': reverse('users:login'),
            'logout': reverse('users:logout'),
            'signup': reverse('users:signup'),
        }
        cls.urls_for_logged_user = {
            'list': reverse('notes:list'),
            'add': reverse('notes:add'),
            'success': reverse('notes:success')
        }

        cls.urls_for_edit_note = {
            'detail': reverse('notes:detail', args=(cls.note.slug, )),
            'edit': reverse('notes:edit', args=(cls.note.slug, )),
            'delete': reverse('notes:delete', args=(cls.note.slug, ))
        }

        cls.urls_for_redirect = {
            **cls.urls_for_logged_user, **cls.urls_for_edit_note
        }

        cls.urls_for_check_form = {
            'add': reverse('notes:add'),
            'edit': reverse('notes:edit', args=(cls.note.slug, )),
        }
