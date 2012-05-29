"""
"""

from django.db import models
from django.contrib.sites.models import Site
from django.contrib.auth.models import User

# next four lines are for sending the payment email
from django.template import Context, loader
from django.utils.translation import ugettext as _
from django.core.mail import send_mail

from sorl.thumbnail import ImageField

from classifieds.conf import settings

import datetime


class ImageFormat(models.Model):
    format = models.CharField(max_length=10)

    def __unicode__(self):
        return self.format


class Category(models.Model):
    site = models.ForeignKey(Site)
    template_prefix = models.CharField(max_length=200, blank=True)
    name = models.CharField(max_length=200)
    slug = models.SlugField()
    enable_contact_form_upload = models.BooleanField(default=False)
    contact_form_upload_max_size = models.IntegerField(default=2 ** 20)
    contact_form_upload_file_extensions = models.CharField(max_length=200,
                                                     default="txt,doc,odf,pdf")
    images_max_count = models.IntegerField(default=0)
    images_max_width = models.IntegerField(help_text=_(u'Maximum width in pixels.'),
                                           default=1024)
    images_max_height = models.IntegerField(help_text=_(u'Maximum height in pixels.'),
                                            default=1024)
    images_max_size = models.IntegerField(help_text=_(u'Maximum size in bytes.'),
                                          default=2 ** 20)
    images_allowed_formats = models.ManyToManyField(ImageFormat, blank=True)
    description = models.TextField(default='')
    sortby_fields = models.CharField(max_length=200,
                                     help_text=_(u'A comma separated list of field names that should show up as sorting options.'),
                                     blank=True)
    sort_order = models.PositiveIntegerField(default=0)

    def __unicode__(self):
        return self.name + u' Category'

    class Meta:
        verbose_name_plural = u'categories'


class Field(models.Model):
    BOOLEAN_FIELD = 1
    CHAR_FIELD = 2
    DATE_FIELD = 3
    DATETIME_FIELD = 4
    EMAIL_FIELD = 5
    FILE_FIELD = 6
    FLOAT_FIELD = 7
    IMAGE_FIELD = 8
    INTEGER_FIELD = 9
    TIME_FIELD = 10
    URL_FIELD = 11
    TEXT_FIELD = 12
    SELECT_FIELD = 13
    FIELD_CHOICES = (
     (BOOLEAN_FIELD, 'Checkbox'),
     (CHAR_FIELD, 'Text Input (one line)'),
     (DATE_FIELD, 'Date Selector'),
     (DATETIME_FIELD, 'Date and Time Selector'),
     (EMAIL_FIELD, 'Email Address'),
     (FILE_FIELD, 'File Upload'),
     (FLOAT_FIELD, 'Decimal Number'),
     (IMAGE_FIELD, 'Image Upload'),
     (INTEGER_FIELD, 'Integer Number'),
     (TIME_FIELD, 'Time Selector'),
     (URL_FIELD, 'URL Input'),
     (TEXT_FIELD, 'Text Input (multi-line)'),
     (SELECT_FIELD, 'Dropdown List of Options'),
    )
    category = models.ForeignKey(Category, null=True, blank=True)
    name = models.CharField(max_length=100)
    label = models.CharField(max_length=200)
    field_type = models.IntegerField(choices=FIELD_CHOICES)
    help_text = models.TextField(blank=True)
    max_length = models.IntegerField(null=True, blank=True)
    enable_counter = models.BooleanField(help_text=_(u'This enabled the javascript counter script for text fields.'))
    enable_wysiwyg = models.BooleanField(help_text=_(u'This enables the text formatting javascript widget for text fields.'))
    required = models.BooleanField()
    options = models.TextField(help_text=_(u'A comma separated list of options [only for the dropdown list field]'),
                               blank=True)

    def __unicode__(self):
        return self.name + u' field for ' + self.category.name


class Ad(models.Model):
    category = models.ForeignKey(Category)
    user = models.ForeignKey(User)
    created_on = models.DateTimeField(auto_now_add=True)
    expires_on = models.DateTimeField()
    # active means that the ad was actually created
    active = models.BooleanField()
    title = models.CharField(max_length=255)

    @models.permalink
    def get_absolute_url(self):
        return ('classifieds_browse_ad_view', (self.pk,))

    def __unicode__(self):
        return u'Ad #' + unicode(self.pk) + ' titled "' + self.title + u'" in category ' + self.category.name

    def expired(self):
        if self.expires_on <= datetime.datetime.now():
            return True
        else:
            return False

    def fields(self):
        fields_list = []
        fields = list(self.category.field_set.all())
        fields += list(Field.objects.filter(category=None))

        for field in fields:
            try:
                fields_list.append((field, field.fieldvalue_set.get(ad=self),))
            except FieldValue.DoesNotExist:
                pass  # If no value is associated with that field, skip it.

        return fields_list

    def field(self, name):
        if name == 'title':
            return self.title
        else:
            return FieldValue.objects.get(field__name=name, ad=self).value

    def fields_dict(self):
        fields_dict = {}
        fields_dict['title'] = self.title

        for key, value in self.fields():
            fields_dict[key.name] = value.value

        return fields_dict

    def is_featured(self):
        for payment in self.payment_set.all():
            if payment.paid_on <= datetime.datetime.now() and \
               payment.paid_on + datetime.timedelta(days=payment.pricing.length) >= datetime.datetime.now():
                for option in payment.options.all():
                    if option.name == PricingOptions.FEATURED_LISTING:
                        return True

        return False


class AdImage(models.Model):
    ad = models.ForeignKey(Ad)
    full_photo = ImageField(upload_to='uploads/', blank=True)


class FieldValue(models.Model):
    field = models.ForeignKey(Field)
    ad = models.ForeignKey(Ad)
    value = models.TextField()

    def __unicode__(self):
        return self.value


class Pricing(models.Model):
    length = models.IntegerField(help_text=_(u'Period being payed for in days'))
    price = models.DecimalField(max_digits=9, decimal_places=2)

    def __unicode__(self):
        return u'$' + unicode(self.price) + u' for ' + str(self.length) + u' days'

    class Meta:
        ordering = ['price']
        verbose_name_plural = u'prices'


class PricingOptions(models.Model):
    FEATURED_LISTING = 1
    PRICING_OPTIONS = (
      (FEATURED_LISTING, u'Featured Listing'),
    )
    name = models.IntegerField(choices=PRICING_OPTIONS)
    price = models.DecimalField(max_digits=9, decimal_places=2)

    def __unicode__(self):
        pricing = {}
        pricing.update(self.PRICING_OPTIONS)
        return u'%s for $%s' % (pricing[int(self.name)], self.price,)

    class Meta:
        ordering = ['price']
        verbose_name_plural = u'options'


class ZipCode(models.Model):
    zipcode = models.IntegerField(primary_key=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    city = models.CharField(max_length=30)
    state = models.CharField(max_length=2)

    def nearby(self, radius):
        radius = float(radius)
        rangeFactor = 0.014457
        # bounding box
        objs = self.get_queryset().filter(latitude__gte=self.latitude - (radius * rangeFactor),
                                          latitude__lte=self.latitude + (radius * rangeFactor),
                                          longitude__gte=self.longitude - (radius * rangeFactor),
                                          longitude__lte=self.longitude + (radius * rangeFactor))

        # if there are any results left, use GetDistance stored function to finish
        if objs.count() > 0:
            objs = objs.extra(where=['GetDistance(%s,%s,latitude,longitude) <= %s'],
                              params=[self.latitude, self.longitude, radius])

        return objs

    def __unicode__(self):
        return _(u'Zip: %s, City: %s, State: %s') % (unicode(self.zipcode),
                                                     self.city, self.state,)


class Payment(models.Model):
    ad = models.ForeignKey(Ad)
    paid = models.BooleanField(default=False)
    paid_on = models.DateTimeField(null=True)
    amount = models.DecimalField(max_digits=9, decimal_places=2)
    pricing = models.ForeignKey(Pricing)
    options = models.ManyToManyField(PricingOptions)

    def complete(self, amount=0.0):
        # clear payment
        if self.amount != amount:
            return False

        self.paid = True
        self.paid_on = datetime.datetime.now()
        self.save()

        # update ad
        self.ad.expires_on += datetime.timedelta(days=payment.pricing.length)
        self.ad.created_on = datetime.datetime.now()
        self.ad.active = True
        self.ad.save()

        # send email for payment
        # 1. render context to email template
        email_template = loader.get_template('classifieds/email/payment.txt')
        context = Context({'payment': self})
        email_contents = email_template.render(context)

        # 2. send email
        send_mail(_('Your payment has been processed.'),
                  email_contents, settings.FROM_EMAIL,
                  [self.ad.user.email], fail_silently=False)


from django.contrib.localflavor.us.models import USStateField, PhoneNumberField


class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True)
    receives_new_posting_notices = models.BooleanField(default=False)
    receives_newsletter = models.BooleanField(default=False)
    address = models.CharField(max_length=100, blank=True, default='')
    city = models.CharField(max_length=100, blank=True, default='')
    state = USStateField(blank=True, default='')
    zipcode = models.CharField(max_length=10, blank=True, default='')
    phone = PhoneNumberField(blank=True, default='')
