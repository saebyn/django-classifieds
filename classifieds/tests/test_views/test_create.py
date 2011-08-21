from django.test import TestCase
from django.core.urlresolvers import reverse


class FancyTestCase(TestCase):
    def get(self, view_or_name, params={}, *args, **kwargs):
        return self.client.get(reverse(view_or_name, args=args, kwargs=kwargs), params)


class TestAdCreation(FancyTestCase):
    fixtures = ['users', 'categories']

    def setUp(self):
        self.client.login(username='user', password='user')

    def test_create_ad_redirects_users_to_select_category(self):
        response = self.get('classifieds_create_ad')
        self.assertRedirects(response, reverse('classifieds_create_ad_select_category'))

    def test_create_ad_renders_pricing_template_for_unauthenticated_users(self):
        self.client.logout()
        response = self.get('classifieds_create_ad')
        self.assertTemplateUsed(response, 'classifieds/index.html')

    def test_select_category_has_categories_context(self):
        response = self.get('classifieds_create_ad_select_category')
        self.assertIn('categories', response.context)

    def test_select_category_has_create_type_context(self):
        response = self.get('classifieds_create_ad_select_category')
        self.assertEqual(response.context['type'], 'create')

    def test_select_category_renders_correct_template(self):
        response = self.get('classifieds_create_ad_select_category')
        self.assertTemplateUsed(response, 'classifieds/category_choice.html')

    def test_create_in_category_creates_inactive_ad(self):
        response = self.get('classifieds_create_ad_in_category', slug='test')
        from classifieds.models import Ad
        ad = Ad.objects.get()  # There can be only one... right now anyway
        self.assertFalse(ad.active)

    def test_create_in_category_redirects_to_ad_edit(self):
        response = self.get('classifieds_create_ad_in_category', slug='test')
        from classifieds.models import Ad
        ad = Ad.objects.get()  # There can be only one... right now anyway
        self.assertRedirects(response, reverse('classifieds_create_ad_edit',
                                               kwargs={'pk': ad.pk}))


class TestAdCreationEditing(FancyTestCase):
    fixtures = ['users', 'categories', 'ads']

    def setUp(self):
        self.client.login(username='user', password='user')

    def test_ad_edit_redirects_to_manage_if_ad_is_active(self):
        from classifieds.models import Ad
        ad = Ad.objects.get(pk=18)  # an active ad

        response = self.get('classifieds_create_ad_edit', pk=ad.pk)
        self.assertRedirects(response, reverse('classifieds_manage_ad_edit',
                                               kwargs={'pk': ad.pk}))

    def test_ad_edit_nonauthed_user_cant_edit_ad(self):
        self.client.logout()
        response = self.get('classifieds_create_ad_edit', pk=1)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('auth_login'),
                              response['Location'])

    def test_ad_edit_other_user_cant_edit_ad(self):
        self.client.logout()
        self.client.login(username='other_user', password='user')
        response = self.get('classifieds_create_ad_edit', pk=1)
        self.assertEqual(response.status_code, 404)

    def test_ad_edit_has_form_context(self):
        response = self.get('classifieds_create_ad_edit', pk=1)
        self.assertIn('form', response.context)
        self.assertIn('imagesformset', response.context)

    def test_ad_edit_generates_thumbnails(self):
        self.fail()

    def test_ad_preview_redirects_to_browse_if_ad_is_active(self):
        from classifieds.models import Ad
        ad = Ad.objects.get(pk=18)  # an active ad

        response = self.get('classifieds_create_ad_preview', pk=ad.pk)
        self.assertRedirects(response, reverse('classifieds_browse_ad_view',
                                               kwargs={'pk': ad.pk}))

    def test_ad_preview_nonauthed_user_cant_see_ad(self):
        self.client.logout()
        response = self.get('classifieds_create_ad_preview', pk=1)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('auth_login'),
                              response['Location'])

    def test_ad_preview_other_user_cant_see_ad(self):
        self.client.logout()
        self.client.login(username='other_user', password='user')
        response = self.get('classifieds_create_ad_preview', pk=1)
        self.assertEqual(response.status_code, 404)
