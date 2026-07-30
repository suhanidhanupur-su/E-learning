from io import BytesIO

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from PIL import Image

from .models import TeamMember


class HomePageTests(TestCase):
    def test_homepage_renders(self):
        response = self.client.get('/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Erudition')
        self.assertContains(response, 'Courses')


class LiveClassesPageTests(TestCase):
    def test_live_classes_page_renders(self):
        response = self.client.get('/live-classes/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Live Classes')


class FaviconTests(TestCase):
    def test_favicon_redirects_to_a_static_asset(self):
        response = self.client.get('/favicon.ico')

        self.assertEqual(response.status_code, 301)


class TeamMemberModelTests(TestCase):
    def test_team_member_is_created_with_expected_defaults(self):
        image = BytesIO()
        Image.new('RGB', (100, 100), color='gold').save(image, format='PNG')
        image.seek(0)
        uploaded_image = SimpleUploadedFile('trainer.png', image.getvalue(), content_type='image/png')

        team_member = TeamMember.objects.create(
            employee_image=uploaded_image,
            employee_name='Aarav Sharma',
            role='Corporate Trainer',
            description='Senior corporate trainer with a focus on leadership development.',
            display_order=2,
        )

        self.assertTrue(team_member.is_active)
        self.assertEqual(team_member.display_order, 2)
        self.assertEqual(str(team_member), 'Aarav Sharma')


class ProfileFlowTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='profileuser',
            email='profile@example.com',
            password='strong-password-123',
        )

    def test_profile_page_requires_login(self):
        response = self.client.get('/profile/')

        self.assertEqual(response.status_code, 302)

    def test_login_page_is_available(self):
        response = self.client.get('/accounts/login/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Login')

    def test_edit_profile_updates_user_details(self):
        self.client.login(username='profileuser', password='strong-password-123')

        image = BytesIO()
        Image.new('RGB', (100, 100), color='blue').save(image, format='PNG')
        image.seek(0)
        uploaded_image = SimpleUploadedFile('avatar.png', image.getvalue(), content_type='image/png')

        response = self.client.post('/edit-profile/', {
            'full_name': 'Ava Johnson',
            'email': 'ava@example.com',
            'phone_number': '07123456789',
            'profile_photo': uploaded_image,
        })

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/profile/')

        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Ava')
        self.assertEqual(self.user.last_name, 'Johnson')
        self.assertEqual(self.user.email, 'ava@example.com')

        profile = self.user.profile
        self.assertEqual(profile.full_name, 'Ava Johnson')
        self.assertEqual(profile.phone_number, '07123456789')
        self.assertTrue(profile.profile_photo)
