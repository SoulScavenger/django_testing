from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class BaseFixtures(TestCase):
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
            'home': reverse('notes:home', None),
            'login': reverse('users:login', None),
            'logout': reverse('users:logout', None),
            'signup': reverse('users:signup', None),
        }
        cls.urls_for_logged_user = {
            'list': reverse('notes:list', None),
            'add': reverse('notes:add', None),
            'success': reverse('notes:success', None)
        }

        cls.urls_for_edit_note = {
            'detail': reverse('notes:detail', args=(cls.note.slug, )),
            'edit': reverse('notes:edit', args=(cls.note.slug, )),
            'delete': reverse('notes:delete', args=(cls.note.slug, ))
        }

        cls.urls_for_redirect = {}
        cls.urls_for_redirect.update(cls.urls_for_logged_user)
        cls.urls_for_redirect.update(cls.urls_for_edit_note)

        cls.urls_for_check_form = {
            'add': reverse('notes:add', None),
            'edit': reverse('notes:edit', args=(cls.note.slug, )),
        }
