from django.test import TestCase
from django.core.urlresolvers import reverse

from classifieds.tests.test_views import FancyTestCase


class TestAdManage(FancyTestCase):
    fixtures = ['users', 'categories', 'ads']

    def setUp(self):
        self.client.login(username='user', password='user')

    def test_manage_view_all_requires_login(self):
        self.client.logout()
        response = self.get('classifieds_manage_view_all')
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('auth_login'), response['Location'])

    def test_manage_delete_requires_login(self):
        self.client.logout()
        response = self.post('classifieds_manage_ad_delete', pk=18)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('auth_login'), response['Location'])

    def test_manage_delete_requires_post_to_complete(self):
        response = self.get('classifieds_manage_ad_delete', pk=18)
        from classifieds.models import Ad
        self.assertEqual(Ad.objects.filter(pk=18).count(), 1)

    def test_manage_delete_get_renders_confirmation_template(self):
        response = self.get('classifieds_manage_ad_delete', pk=18)
        self.assertTemplateUsed(response, 'classifieds/ad_confirm_delete.html')

    def test_manage_delete_post_deletes_ad(self):
        response = self.post('classifieds_manage_ad_delete', pk=18)
        from classifieds.models import Ad
        self.assertEqual(Ad.objects.filter(pk=18).count(), 0)

    def test_manage_edit_has_form_in_context(self):
        response = self.get('classifieds_manage_ad_edit', pk=18)
        self.assertIn('form', response.context)
        self.assertIn('imagesformset', response.context)

    def test_manage_edit_save_redirects_to_view_all(self):
        params = {'adimage_set-TOTAL_FORMS': u'3',
                  'adimage_set-INITIAL_FORMS': u'0',
                  'adimage_set-MAX_NUM_FORMS': u'3',
                  'title': 'Test Title',
                  'Test Field': '2011-08-22 08:00:00'}
        response = self.client.post(reverse("classifieds_manage_ad_edit",
                                    kwargs=dict(pk=18)), params)
        self.assertRedirects(response, reverse("classifieds_manage_view_all"))

    def test_manage_edit_save_saves_title(self):
        params = {'adimage_set-TOTAL_FORMS': u'3',
                  'adimage_set-INITIAL_FORMS': u'0',
                  'adimage_set-MAX_NUM_FORMS': u'3',
                  'title': 'Test Title',
                  'Test Field': '2011-08-22 08:00:00'}
        response = self.client.post(reverse("classifieds_manage_ad_edit",
                                    kwargs=dict(pk=18)), params)
        from classifieds.models import Ad
        self.assertEqual(Ad.objects.get(pk=18).title, 'Test Title')

    def test_ad_edit_save_saves_custom_field(self):
        params = {'adimage_set-TOTAL_FORMS': u'3',
                  'adimage_set-INITIAL_FORMS': u'0',
                  'adimage_set-MAX_NUM_FORMS': u'3',
                  'title': 'Test Title',
                  'Test Field': '2011-08-22 08:00:00'}
        response = self.client.post(reverse("classifieds_manage_ad_edit",
                                    kwargs=dict(pk=18)), params)
        from classifieds.models import Ad
        self.assertEqual(Ad.objects.get(pk=18).field('Test Field'),
                         '2011-08-22 08:00:00')
