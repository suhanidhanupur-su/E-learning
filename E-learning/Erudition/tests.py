from django.test import TestCase


class HomePageTests(TestCase):
    def test_homepage_renders(self):
        response = self.client.get('/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Erudition')
        self.assertContains(response, 'Courses')
