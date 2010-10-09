"""
  $Id$
"""

from django.template import Context, loader
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User

from django.core.mail import send_mass_mail

from django.contrib.sites.models import Site

from classifieds.models import Ad

from options import from_email, notice_posting_new, notice_posting_expires

import datetime

def run():
	yesterday = datetime.datetime.today() - datetime.timedelta(days=int(notice_posting_new()))
	postings = Ad.objects.filter(created_on__gt=yesterday)
	
	# get subscriber list
	subscribers = User.objects.filter(userprofile__receives_new_posting_notices=True)
	
	emails = []
	
	for subscriber in subscribers:
		# 1. render context to email template
		email_template = loader.get_template('classifieds/email/newpostings.txt')
		context = Context({'postings': postings, 'user': subscriber, 'site': Site.objects.get_current()})
		email_contents = email_template.render(context)
		emails.append( (_('New ads posted on ') + Site.objects.get_current().name,
		                email_contents,
		                from_email(),
		                [subscriber.email],
		               )
		             )

	# 2. send emails
	send_mass_mail(emails)
	
	tomorrow = datetime.datetime.today() + datetime.timedelta(days=int(notice_posting_expires()))
	expiring_postings = Ad.objects.filter(expires_on__lt=tomorrow)
	emails = []
	
	for posting in expiring_postings:
		# 1. render context to email template
		email_template = loader.get_template('classifieds/email/expiring.txt')
		context = Context({'posting': posting, 'user': posting.user, 'site': Site.objects.get_current()})
		email_contents = email_template.render(context)
		emails.append( (_('Your ad on ') + Site.objects.get_current().name + _(' is about to expire.'),
		                email_contents,
		                from_email(),
		                [posting.user.email],
		               )
		             )

	# 2. send emails
	send_mass_mail(emails)
	
	# delete old ads
	yesterday = datetime.datetime.today() - datetime.timedelta(days=int(notice_posting_expires()))
	Ad.objects.filter(expires_on__lt=yesterday).delete()

if __name__ == '__main__':
	run()

