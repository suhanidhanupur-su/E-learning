from io import BytesIO

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from PIL import Image

from .models import Category, Course, Enrollment, Enquiry, TeamMember


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


class CourseEnrollmentTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Technology', slug='technology')
        self.course = Course.objects.create(
            category=self.category,
            title='Python for Beginners',
            slug='python-for-beginners',
            short_description='A practical introduction to Python.',
            description='A comprehensive course for first-time learners.',
            instructor_name='Ada Lovelace',
            duration='4 weeks',
            price=49.00,
            is_active=True,
        )
        self.user = get_user_model().objects.create_user(
            username='courseuser',
            email='course@example.com',
            password='strong-password-123',
        )

    def test_course_detail_page_renders(self):
        response = self.client.get('/courses/python-for-beginners/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Python for Beginners')
        self.assertContains(response, 'Ada Lovelace')

    def test_enrollment_requires_login(self):
        response = self.client.get('/enroll/python-for-beginners/')

        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_authenticated_user_can_enroll(self):
        self.client.login(username='courseuser', password='strong-password-123')

        response = self.client.get('/enroll/python-for-beginners/')

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/enrollment-success/')
        self.assertTrue(Enrollment.objects.filter(user=self.user, course=self.course).exists())


class GetInTouchTests(TestCase):
    def test_enquiry_submission_saves_and_returns_success(self):
        response = self.client.post('/enquiries/', {
            'name': 'Asha Rao',
            'phone': '9876543210',
            'email': 'asha@example.com',
            'message': 'I would like to learn more about your programs.'
        }, content_type='application/json')

        self.assertEqual(response.status_code, 200)
        self.assertTrue(Enquiry.objects.filter(email='asha@example.com').exists())

    def test_enquiry_submission_returns_validation_errors(self):
        response = self.client.post('/enquiries/', {
            'name': '',
            'phone': '',
            'email': 'not-an-email',
            'message': ''
        }, content_type='application/json')

        self.assertEqual(response.status_code, 400)
        self.assertIn('errors', response.json())


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
