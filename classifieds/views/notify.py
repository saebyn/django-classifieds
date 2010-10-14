from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.http import HttpResponseRedirect

from classifieds.forms import SubscribeForm
from classifieds.models import UserProfile

def notify_complete(request):
  return render_to_response('classifieds/notify_complete.html', {}, context_instance=RequestContext(request))

def notify(request):
  if request.method == 'POST': #form was submitted
    form = SubscribeForm(request.POST)
    if form.is_valid():
      # TODO: don't do this if user is logged in...

      # create user profile
      user = User.objects.create_user(form.cleaned_data["email_address"], form.cleaned_data["email_address"])
      user.first_name = form.cleaned_data["first_name"]
      user.last_name = form.cleaned_data["last_name"]
      user.is_active = False
      user.save()
      profile = UserProfile.objects.create(user=user, receives_new_posting_notices=True, receives_newsletter=True)
      profile.save()
      
      return HttpResponseRedirect(reverse(notify_complete))
  else:
    form = SubscribeForm()

  return render_to_response('classifieds/notify.html', {'form': form}, context_instance=RequestContext(request))

