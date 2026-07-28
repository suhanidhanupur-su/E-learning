from io import BytesIO

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from PIL import Image


class HomePageTests(TestCase):
    def test_homepage_renders(self):
        response = self.client.get('/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Erudition')
        self.assertContains(response, 'Courses')


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
