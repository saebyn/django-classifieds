from django.test import TestCase
from django.core.urlresolvers import reverse

from classifieds.tests.test_views import FancyTestCase


class TestAdManage(FancyTestCase):
    fixtures = ['users', 'categories', 'ads']

    def setUp(self):
        self.client.login(username='user', password='user')

    def test_manange_view_all_requires_login(self):
        self.fail()

    def test_manage_delete_requires_login(self):
        self.fail()

    def test_manage_delete_get_renders_confirmation_template(self):
        self.fail()

    def test_manage_delete_post_deletes_ad(self):
        self.fail()

    def test_manage_edit_has_form_in_context(self):
        self.fail()

    def test_manage_edit_save_updates_thumbnails(self):
        self.fail()

    def test_manage_edit_save_redirects_to_view_all(self):
        self.fail()
