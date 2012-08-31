# vim: set fileencoding=utf-8 ft=python ff=unix nowrap tabstop=4 shiftwidth=4 softtabstop=4 smarttab shiftround expandtab :
from django.core.urlresolvers import reverse

from classifieds.tests.test_views import FancyTestCase


class TestAdBrowsing(FancyTestCase):
    fixtures = ['users', 'categories', 'ads']

    def setUp(self):
        self.client.login(username='user', password='user')

    def test_view_ad_must_be_active(self):
        response = self.get('classifieds_browse_ad_view', pk=1)
        self.assertEqual(response.status_code, 404)

    def test_cant_view_expired_ad_when_logged_out(self):
        self.client.logout()
        response = self.get('classifieds_browse_ad_view', pk=2)
        self.assertEqual(response.status_code, 404)

    def test_cant_view_expiered_ad_of_another_user(self):
        self.client.logout()
        self.client.login(username='other_user', password='user')
        response = self.get('classifieds_browse_ad_view', pk=2)
        self.assertEqual(response.status_code, 404)

    def test_can_view_own_expired_ad(self):
        response = self.get('classifieds_browse_ad_view', pk=2)
        self.assertEqual(response.status_code, 200)

    def test_unauthed_user_can_view_active_ad(self):
        self.client.logout()
        response = self.get('classifieds_browse_ad_view', pk=18)
        self.assertEqual(response.status_code, 200)

    def test_authed_user_can_view_active_ad(self):
        response = self.get('classifieds_browse_ad_view', pk=18)
        self.assertEqual(response.status_code, 200)

    def test_category_overview_uses_template(self):
        response = self.get('classifieds_browse_categories')
        self.assertTemplateUsed(response, 'classifieds/category_overview.html')

    def test_search_initial_uses_search_template(self):
        response = self.get('classifieds_browse_category_search', slug='test')
        self.assertTemplateUsed(response, 'classifieds/search.html')

    def test_search_redirects_to_results(self):
        post = {}
        response = self.post('classifieds_browse_category_search',
                params=post, slug='test')
        self.assertRedirects(response, reverse('classifieds_browse_search_results',
            kwargs=dict(slug='test')))

    def test_search_uses_list_template(self):
        post = {'Test Field': 'test',
                'Test Text Field': 'test'}
        self.post('classifieds_browse_category_search',
                params=post, slug='test')
        response = self.get('classifieds_browse_search_results',
                slug='test')
        print response
        self.assertTemplateUsed(response, 'classifieds/list.html')
