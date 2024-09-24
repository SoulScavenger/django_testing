from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestNotesPage(TestCase):
    """Класс проверки содержимого страницы заметок."""

    USER_NOTES_URL = reverse('notes:list')

    @classmethod
    def setUpTestData(cls):
        """Создание фикстур."""
        cls.author = User.objects.create(username='Автор')
        cls.not_author = User.objects.create(username='Не автор')
        cls.note = Note.objects.create(title='Заметка',
                                       text='Просто текст',
                                       author=cls.author)

    def test_note_in_author_notes_list(self):
        """Проверка, что созданная заметка в списке заметок."""
        self.client.force_login(self.author)
        response = self.client.get(self.USER_NOTES_URL)
        object_list = response.context['object_list']
        self.assertIn(self.note, object_list)

    def test_note_not_in_another_user_notes_list(self):
        """Проверка, что созданная заметка не в чужом списке."""
        self.client.force_login(self.not_author)
        response = self.client.get(self.USER_NOTES_URL)
        object_list = response.context['object_list']
        self.assertNotIn(self.note, object_list)


class TestDetailNotePage(TestCase):
    """Класс проверки детальной страницы заметки."""

    @classmethod
    def setUpTestData(cls):
        """Создание фикстур."""
        cls.author = User.objects.create(username='Автор')
        cls.not_author = User.objects.create(username='Не автор')
        cls.note = Note.objects.create(title='Заметка',
                                       text='Просто текст',
                                       author=cls.author)

    def test_authorized_client_has_form(self):
        """Проверка наличия формы в методе add/edit."""
        self.client.force_login(self.author)
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug, )),
        )
        for item in urls:
            name, args = item
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertIsInstance(response.context['form'], NoteForm)
