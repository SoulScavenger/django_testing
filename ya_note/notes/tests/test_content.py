from django.contrib.auth import get_user_model
from django.test import TestCase

from notes.forms import NoteForm
from notes.tests.fixtures import BaseFixtures

User = get_user_model()


class TestNotesPage(BaseFixtures, TestCase):
    """Класс проверки содержимого страницы заметок."""

    def test_note_in_author_notes_list(self):
        """Проверка, что созданная заметка в списке заметок."""
        response = self.author_client.get(self.urls_for_logged_user['list'])
        object_list = response.context['object_list']
        self.assertIn(self.note, object_list)

    def test_note_not_in_another_user_notes_list(self):
        """Проверка, что созданная заметка не в чужом списке."""
        response = self.not_author_client.get(
            self.urls_for_logged_user['list']
        )
        notes = response.context['object_list']
        self.assertNotIn(self.note, notes)


class TestDetailNotePage(BaseFixtures, TestCase):
    """Класс проверки детальной страницы заметки."""

    def test_authorized_client_has_form(self):
        """Проверка наличия формы в методе add/edit."""
        for name, url in self.urls_for_check_form.items():
            with self.subTest(name=name):
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
