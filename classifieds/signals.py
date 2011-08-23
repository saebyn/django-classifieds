"""
"""

from django.db.models.signals import post_save
from django.contrib.auth.models import User

from paypal.standard.ipn.signals import payment_was_successful

from classifieds.models import Payment, UserProfile


def create_profile(sender, **kw):
    user = kw["instance"]
    if kw["created"]:
        profile = UserProfile(user=user)
        profile.save()


def make_payment(sender, **kwargs):
    payment = Payment.objects.get(pk=sender.item_number)
    payment.complete(amount=sender.mc_gross)


post_save.connect(create_profile, sender=User, dispatch_uid="users-profilecreation-signal")
payment_was_successful.connect(make_payment)
