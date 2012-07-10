from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.template import Context, loader, RequestContext
from django.utils.translation import ugettext as _
from django.contrib import messages
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.conf import settings

from paypal.standard.forms import PayPalPaymentsForm

from classifieds.models import Ad, Pricing, PricingOptions, Payment
from classifieds.forms.misc import CheckoutForm
from classifieds.conf import settings as app_settings
from classifieds import views


@login_required
def checkout(request, pk):
    ad = get_object_or_404(Ad, pk=pk)
    form = CheckoutForm(request.POST or None)
    if form.is_valid():
        total = 0
        pricing = form.cleaned_data["pricing"]
        total += pricing.price
        pricing_options = []
        for option in form.cleaned_data["pricing_options"]:
            pricing_options.append(option)
            total += option.price

        # create Payment object
        payment = Payment.objects.create(ad=ad, pricing=pricing, amount=total)
        for option in pricing_options:
            payment.options.add(option)

        payment.save()

        # send email when done
        # 1. render context to email template
        email_template = loader.get_template('classifieds/email/posting.txt')
        context = Context({'ad': ad})
        email_contents = email_template.render(context)

        # 2. send email
        send_mail(_('Your ad will be posted shortly.'),
                  email_contents,
                  app_settings.FROM_EMAIL,
                  [ad.user.email],
                  fail_silently=False)

        item_name = _('Your ad on ') + Site.objects.get_current().name
        paypal_values = {'amount': total,
                         'item_name': item_name,
                         'item_number': payment.pk,
                         'quantity': 1}

        if settings.DEBUG:
            paypal_form = PayPalPaymentsForm(initial=paypal_values).sandbox()
        else:
            paypal_form = PayPalPaymentsForm(initial=paypal_values).render()

        return render_to_response('classifieds/paypal.html',
                                  {'form': paypal_form},
                                  context_instance=RequestContext(request))

    return render_to_response('classifieds/checkout.html',
                              {'ad': ad, 'form': form},
                              context_instance=RequestContext(request))


def pricing(request):
    return render_to_response('classifieds/pricing.js',
                              {'prices': Pricing.objects.all(),
                               'options': PricingOptions.objects.all()},
                              context_instance=RequestContext(request))


@login_required
def view_bought(request, pk):
    messages.success(_("""Your ad has been successfully posted.
    Thank You for Your Order!"""))
    return views.browse.view(request, pk)
