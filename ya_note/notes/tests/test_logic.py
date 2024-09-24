from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


class TestLogic(TestCase):
    """Класс проверки логики."""

    @classmethod
    def setUpTestData(cls):
        """Создание фикстур."""
        cls.author = User.objects.create(username='Maksim')
        cls.not_author = User.objects.create(username='User')
        cls.note = Note.objects.create(title='Заметка',
                                       text='Текст заметки',
                                       author=cls.author
                                       )
        cls.add_url = reverse('notes:add')
        cls.login_url = reverse('users:login')
        cls.success_url = reverse('notes:success')
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug, ))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug, ))
        cls.author_client = Client()
        cls.not_author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.not_author_client.force_login(cls.not_author)
        cls.form_data = {
            'title': 'Новая заметка',
            'text': 'Текст новой заметки',
            'slug': slugify('Новая заметка')}

    def test_anonymous_user_cant_create_note(self):
        """Не аутентифицированный пользователь не может создать заметку."""
        self.client.post(self.add_url, data=self.form_data)
        redirect_url = f'{self.login_url}?next={self.add_url}'
        response = self.client.get(self.add_url)
        self.assertRedirects(response, redirect_url)

        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_user_can_create_note(self):
        """Аутентифицированный пользователь может создать заметку."""
        response = self.author_client.post(self.add_url, data=self.form_data)
        self.assertRedirects(response, self.success_url)

        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 2)

        new_note = Note.objects.last()
        self.assertEqual(new_note.author, self.author)
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])

    def test_not_unique_slug(self):
        """Проверка slug на уникальность."""
        self.form_data['slug'] = self.note.slug
        response = self.author_client.post(self.add_url, data=self.form_data)
        self.assertFormError(response,
                             'form',
                             'slug',
                             errors=(self.form_data['slug'] + WARNING)
                             )

    def test_auto_slug(self):
        """Автоматическое заполнение slug."""
        self.author_client.post(self.add_url, data=self.form_data)
        new_note = Note.objects.last()
        self.assertEqual(new_note.slug, slugify(self.form_data['title']))

    def test_edit_note(self):
        """Проверка - редактирования заметки автором."""
        self.author_client.post(self.edit_url, data=self.form_data)

        edited_note = Note.objects.last()
        self.assertEqual(edited_note.author, self.author)
        self.assertEqual(edited_note.title, self.form_data['title'])
        self.assertEqual(edited_note.text, self.form_data['text'])
        self.assertEqual(edited_note.slug, self.form_data['slug'])

    def test_delete_note(self):
        """Проверка - удаления заметки автором."""
        self.author_client.post(self.delete_url, data=self.form_data)

        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_not_author_cant_edit_note(self):
        """Проверка - не автор не может удалить заметку."""
        response = self.not_author_client.post(self.edit_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

        edited_note = Note.objects.last()
        self.assertNotEqual(edited_note.author, self.not_author)
        self.assertNotEqual(edited_note.title, self.form_data['title'])
        self.assertNotEqual(edited_note.text, self.form_data['text'])
        self.assertNotEqual(edited_note.slug, self.form_data['slug'])

    def test_not_author_cant_delete_note(self):
        """Проверка - не автор не может удалить заметку."""
        response = self.not_author_client.post(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
