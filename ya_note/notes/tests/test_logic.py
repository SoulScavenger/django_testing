from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note
from notes.tests.fixtures import BaseFixtures


class TestLogic(BaseFixtures):
    """Класс проверки логики."""

    CREATE_NEW_NOTE = {
        'title': 'Новая заметка',
        'text': 'Текст новой заметки',
        'slug': slugify('Новая заметка')
    }

    def test_anonymous_user_cant_create_note(self):
        """Не аутентифицированный пользователь не может создать заметку."""
        before_notes_count = Note.objects.count()
        self.client.post(
            self.urls_for_logged_user['add'], data=self.CREATE_NEW_NOTE
        )
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
            self.urls_for_logged_user['add'], data=self.CREATE_NEW_NOTE
        )
        self.assertRedirects(response, self.urls_for_logged_user['success'])

        after_notes_count = Note.objects.count()
        self.assertLess(before_notes_count, after_notes_count)

        new_note = Note.objects.get()
        self.assertEqual(new_note.author, self.author)
        self.assertEqual(new_note.title, self.CREATE_NEW_NOTE['title'])
        self.assertEqual(new_note.text, self.CREATE_NEW_NOTE['text'])
        self.assertEqual(new_note.slug, self.CREATE_NEW_NOTE['slug'])

    def test_not_unique_slug(self):
        """Проверка slug на уникальность."""
        before_notes_count = Note.objects.count()
        self.CREATE_NEW_NOTE['slug'] = self.note.slug
        response = self.author_client.post(
            self.urls_for_logged_user['add'], data=self.CREATE_NEW_NOTE)
        after_notes_count = Note.objects.count()
        self.assertEqual(before_notes_count, after_notes_count)
        self.assertFormError(response,
                             'form',
                             'slug',
                             errors=(self.CREATE_NEW_NOTE['slug'] + WARNING)
                             )

    def test_auto_slug(self):
        """Автоматическое заполнение slug."""
        Note.objects.all().delete()
        self.author_client.post(
            self.urls_for_logged_user['add'], data=self.CREATE_NEW_NOTE
        )
        new_note = Note.objects.get()
        self.assertEqual(new_note.slug, slugify(self.CREATE_NEW_NOTE['title']))

    def test_edit_note(self):
        """Проверка - редактирования заметки автором."""
        self.author_client.post(
            self.urls_for_edit_note['edit'], data=self.CREATE_NEW_NOTE
        )

        edited_note = Note.objects.get(id=self.note.id)
        self.assertEqual(edited_note.author, self.author)
        self.assertNotEqual(edited_note.title, self.note.title)
        self.assertNotEqual(edited_note.text, self.note.text)
        self.assertNotEqual(edited_note.slug, self.note.slug)

    def test_delete_note(self):
        """Проверка - удаления заметки автором."""
        before_notes_count = Note.objects.count()
        self.author_client.post(
            self.urls_for_edit_note['delete'], data=self.CREATE_NEW_NOTE
        )

        after_notes_count = Note.objects.count()
        self.assertEqual(after_notes_count, before_notes_count - 1)

    def test_not_author_cant_edit_note(self):
        """Проверка - не автор не может удалить заметку."""
        response = self.not_author_client.post(self.urls_for_edit_note['edit'])
        self.assertEqual(response.status_code, self.STATUS_404)

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
        self.assertEqual(response.status_code, self.STATUS_404)
        after_notes_count = Note.objects.count()
        self.assertEqual(before_notes_count, after_notes_count)
