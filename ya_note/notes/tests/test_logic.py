from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from pytils.translit import slugify

from notes.tests.fixtures import BaseFixtures
from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


class TestLogic(BaseFixtures, TestCase):
    """Класс проверки логики."""

    @classmethod
    def setUpTestData(cls):
        """Создание фикстур."""
        super().setUpTestData()
        cls.form_data = {
            'title': 'Новая заметка',
            'text': 'Текст новой заметки',
            'slug': slugify('Новая заметка')}

    def test_anonymous_user_cant_create_note(self):
        """Не аутентифицированный пользователь не может создать заметку."""
        before_notes_count = Note.objects.count()
        self.client.post(self.urls_for_logged_user['add'], data=self.form_data)
        redirect_url = (f'{self.urls_for_not_logged_user["login"]}?next='
                        f'{self.urls_for_logged_user["add"]}')
        response = self.client.get(self.urls_for_logged_user['add'])
        self.assertRedirects(response, redirect_url)

        after_notes_count = Note.objects.count()
        self.assertEqual(before_notes_count, after_notes_count)

    def test_user_can_create_note(self):
        """Аутентифицированный пользователь может создать заметку."""
        Note.objects.all().delete()

        before_notes_count = Note.objects.count()
        response = self.author_client.post(
            self.urls_for_logged_user['add'], data=self.form_data
        )
        self.assertRedirects(response, self.urls_for_logged_user['success'])

        after_notes_count = Note.objects.count()
        self.assertLess(before_notes_count, after_notes_count)

        new_note = Note.objects.get()
        self.assertEqual(new_note.author, self.author)
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])

    def test_not_unique_slug(self):
        """Проверка slug на уникальность."""
        before_notes_count = Note.objects.count()
        self.form_data['slug'] = self.note.slug
        response = self.author_client.post(
            self.urls_for_logged_user['add'], data=self.form_data)
        after_notes_count = Note.objects.count()
        self.assertEqual(before_notes_count, after_notes_count)
        self.assertFormError(response,
                             'form',
                             'slug',
                             errors=(self.form_data['slug'] + WARNING)
                             )

    def test_auto_slug(self):
        """Автоматическое заполнение slug."""
        Note.objects.all().delete()
        self.author_client.post(
            self.urls_for_logged_user['add'], data=self.form_data
        )
        new_note = Note.objects.get()
        self.assertEqual(new_note.slug, slugify(self.form_data['title']))

    def test_edit_note(self):
        """Проверка - редактирования заметки автором."""
        self.author_client.post(
            self.urls_for_edit_note['edit'], data=self.form_data
        )

        edited_note = Note.objects.get(id=self.note.id)
        self.assertEqual(edited_note.author, self.author)
        self.assertNotEqual(edited_note.title, self.note.title)
        self.assertNotEqual(edited_note.text, self.note.text)
        self.assertNotEqual(edited_note.slug, self.note.slug)

    def test_delete_note(self):
        """Проверка - удаления заметки автором."""
        self.author_client.post(
            self.urls_for_edit_note['delete'], data=self.form_data
        )

        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_not_author_cant_edit_note(self):
        """Проверка - не автор не может удалить заметку."""
        response = self.not_author_client.post(self.urls_for_edit_note['edit'])
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

        edited_note = Note.objects.get(id=self.note.id)
        self.assertNotEqual(edited_note.author, self.not_author)
        self.assertEqual(edited_note.title, self.note.title)
        self.assertEqual(edited_note.text, self.note.text)
        self.assertEqual(edited_note.slug, self.note.slug)

    def test_not_author_cant_delete_note(self):
        """Проверка - не автор не может удалить заметку."""
        before_notes_count = Note.objects.count()
        response = self.not_author_client.post(
            self.urls_for_edit_note['delete']
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        after_notes_count = Note.objects.count()
        self.assertEqual(before_notes_count, after_notes_count)
