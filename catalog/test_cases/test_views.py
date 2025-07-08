from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User, Permission
from catalog.models import Author

class AuthorCreateViewTest(TestCase):
    def setUp(self):
        # Создаем пользователя без прав
        self.user = User.objects.create_user(username='testuser', password='12345')
        # Создаем пользователя с правом can_mark_returned
        self.user_with_permission = User.objects.create_user(username='permuser', password='12345')
        permission = Permission.objects.get(codename='can_mark_returned')
        self.user_with_permission.user_permissions.add(permission)
        self.user_with_permission.save()

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('author_create'))
        self.assertRedirects(response, '/accounts/login/?next=' + reverse('author_create'))

    def test_forbidden_if_logged_in_without_permission(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('author_create'))
        self.assertEqual(response.status_code, 403)

    def test_logged_in_with_permission_uses_correct_template(self):
        self.client.login(username='permuser', password='12345')
        response = self.client.get(reverse('author_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/author_form.html')

    def test_initial_date_of_death(self):
        self.client.login(username='permuser', password='12345')
        response = self.client.get(reverse('author_create'))
        self.assertEqual(response.status_code, 200)
        # Проверяем реальное значение в форме
        self.assertIn('11/06/2020', str(response.content))


    def test_successful_author_creation_redirects(self):
        self.client.login(username='permuser', password='12345')
        response = self.client.post(reverse('author_create'), {
            'first_name': 'John',
            'last_name': 'Doe',
            'date_of_birth': '1970-01-01',
            'date_of_death': '2020-06-11',
        })
        # После успешного создания должен быть редирект, например на список авторов
        self.assertEqual(response.status_code, 302)
        # Проверяем, что создан автор с нужным именем
        self.assertTrue(Author.objects.filter(first_name='John', last_name='Doe').exists())

# Тест для модели Author (например, в test_models.py)
class AuthorModelTest(TestCase):
    def test_get_absolute_url(self):
        author = Author.objects.create(first_name='John', last_name='Doe')
        self.assertEquals(author.get_absolute_url(), f'/catalog/author/{author.pk}/')  # Обрати внимание на слеш в конце
