
from django.test import TestCase
from django.core.urlresolvers import reverse


class FancyTestCase(TestCase):
    def get(self, view_or_name, params={}, *args, **kwargs):
        return self.client.get(reverse(view_or_name, args=args, kwargs=kwargs), params)

    def post(self, view_or_name, params={}, *args, **kwargs):
        return self.client.post(reverse(view_or_name, args=args, kwargs=kwargs), params)
