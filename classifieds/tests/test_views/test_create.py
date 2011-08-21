from django.test import TestCase
from django.core.urlresolvers import reverse


class TestAdEditor(TestCase):
    fixtures = ['users', 'categories', 'ads']

    def test_page_loads(self):
        self.client.login(username='user', password='user')
        response = self.client.get(reverse('classifieds_create_ad_create'))
        self.assertEqual(response.status_code, 200)
