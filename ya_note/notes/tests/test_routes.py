from notes.tests.fixtures import BaseFixtures


class TestRoutes(BaseFixtures):
    """Класс проверки маршрутов."""

    def test_pages_availability(self):
        """Проверка доступа к главной странице и страницам аутентификации."""
        for name, url in self.urls_for_not_logged_user.items():
            with self.subTest(name=name):
                response = self.client.get(url)
                self.assertEqual(response.status_code, self.STATUS_200)

    def test_availability_to_note_list_add_success_add_for_auth_user(self):
        """Доступность к списку, добавлению, успешному добавлению."""
        for name, url in self.urls_for_logged_user.items():
            with self.subTest(name=name):
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, self.STATUS_200)

    def test_availability_to_note_detail_edit_and_delete_for_author(self):
        """Проверка доступа к просмотру/редактированию заметки"""
        users_statuses = (
            (self.author_client, self.STATUS_200),
            (self.not_author_client, self.STATUS_404),
        )
        for item in users_statuses:
            user, status = item
            for name, url in self.urls_for_edit_note.items():
                with self.subTest(name=name):
                    response = user.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_not_auth_user(self):
        """Проверка редиректа для не аутентифицированного пользователя."""
        for name, url in self.urls_for_redirect.items():
            with self.subTest(name=name):
                redirect_url = (f'{self.urls_for_not_logged_user["login"]}?'
                                f'next={url}')
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
