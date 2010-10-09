"""
  $Id$


"""

from paypal.standard.ipn.signals import payment_was_successful
from models import Payment
        
def make_payment(sender, **kwargs):
  payment = Payment.objects.get(pk=sender.item_number)
  payment.complete(amount=sender.mc_gross)

payment_was_successful.connect(make_payment)
