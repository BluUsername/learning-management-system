from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token

from .models import User


class RegisterTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_register_student(self):
        response = self.client.post('/api/auth/register/', {
            'username': 'newstudent',
            'email': 'student@example.com',
            'password': 'testpass123',
            'password2': 'testpass123',
            'role': 'student',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)
        self.assertEqual(response.data['user']['role'], 'student')

    def test_register_teacher(self):
        response = self.client.post('/api/auth/register/', {
            'username': 'newteacher',
            'email': 'teacher@example.com',
            'password': 'testpass123',
            'password2': 'testpass123',
            'role': 'teacher',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['user']['role'], 'teacher')

    def test_register_password_mismatch(self):
        response = self.client.post('/api/auth/register/', {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'password2': 'wrongpass123',
            'role': 'student',
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_duplicate_username(self):
        User.objects.create_user(username='existing', email='a@example.com', password='pass1234')
        response = self.client.post('/api/auth/register/', {
            'username': 'existing',
            'email': 'b@example.com',
            'password': 'testpass123',
            'password2': 'testpass123',
            'role': 'student',
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LoginTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser', email='test@example.com',
            password='testpass123', role='student',
        )

    def test_login_valid(self):
        response = self.client.post('/api/auth/login/', {
            'username': 'testuser',
            'password': 'testpass123',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertEqual(response.data['user']['username'], 'testuser')

    def test_login_invalid(self):
        response = self.client.post('/api/auth/login/', {
            'username': 'testuser',
            'password': 'wrongpassword',
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class CurrentUserTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser', email='test@example.com',
            password='testpass123', role='student',
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

    def test_get_current_user(self):
        response = self.client.get('/api/auth/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
        self.assertEqual(response.data['role'], 'student')

    def test_unauthenticated_access(self):
        client = APIClient()
        response = client.get('/api/auth/me/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_cannot_escalate_role_via_self_update(self):
        """A student PATCHing /api/auth/me/ with role=admin must not change role."""
        response = self.client.patch('/api/auth/me/', {'role': 'admin'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.role, 'student')

    def test_user_cannot_change_username_via_self_update(self):
        """Username and email must be read-only on the self-service endpoint."""
        response = self.client.patch(
            '/api/auth/me/',
            {'username': 'hacker', 'email': 'hacker@example.com'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'test@example.com')

    def test_user_can_update_safe_profile_fields(self):
        """Safe profile fields like first_name, last_name, bio should remain editable."""
        response = self.client.patch(
            '/api/auth/me/',
            {'first_name': 'Test', 'last_name': 'User', 'bio': 'Hello world'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Test')
        self.assertEqual(self.user.last_name, 'User')
        self.assertEqual(self.user.bio, 'Hello world')


class UserManagementTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            username='admin', email='admin@example.com',
            password='testpass123', role='admin',
        )
        self.student = User.objects.create_user(
            username='student', email='student@example.com',
            password='testpass123', role='student',
        )
        self.admin_token = Token.objects.create(user=self.admin)
        self.student_token = Token.objects.create(user=self.student)

    def test_user_list_admin_only(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Paginated response: results are in response.data['results']
        results = response.data.get('results', response.data)
        self.assertEqual(len(results), 2)

    def test_user_list_student_forbidden(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.student_token.key}')
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_delete_admin_only(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        response = self.client.delete(f'/api/users/{self.student.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(id=self.student.id).exists())

    def test_user_delete_student_forbidden(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.student_token.key}')
        response = self.client.delete(f'/api/users/{self.admin.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class LogoutTests(TestCase):
    """Tests for POST /api/auth/logout/.

    Logout works by destroying the user's auth token server-side. After
    logout, the same token must no longer authenticate any request — this
    is what makes the endpoint a real security primitive rather than a
    client-only convenience.
    """

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser', email='test@example.com',
            password='testpass123', role='student',
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

    def test_logout_deletes_token_and_returns_204(self):
        """Logout must destroy the token row so reuse is impossible."""
        response = self.client.post('/api/auth/logout/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Token.objects.filter(key=self.token.key).exists())

    def test_logout_then_reuse_token_is_unauthorized(self):
        """The same token must stop working immediately after logout."""
        self.client.post('/api/auth/logout/')
        response = self.client.get('/api/auth/me/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
