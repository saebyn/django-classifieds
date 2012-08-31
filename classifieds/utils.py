"""
"""

from PIL import Image
import HTMLParser
import string
import re
import os.path

from django.utils.datastructures import SortedDict
from django.utils.translation import ugettext as _
from django.core.paginator import Paginator, InvalidPage
from django.template.loader import get_template
from django.template import TemplateDoesNotExist, RequestContext
from django.forms import ValidationError

from django import forms
from django.http import HttpResponse
from django.forms.fields import EMPTY_VALUES

from classifieds.conf import settings
from classifieds.search import SelectForm, searchForms
from classifieds.models import Ad, Field, Category, Pricing, PricingOptions


def category_template_name(category, page):
    return os.path.join(u'classifieds/category',
                        category.template_prefix, page)


def render_category_page(request, category, page, context):
    template_name = category_template_name(category, page)
    try:
        template = get_template(template_name)
    except TemplateDoesNotExist:
        template = get_template('classifieds/category/base/%s' % page)

    context = RequestContext(request, context)
    return HttpResponse(template.render(context))


def clean_adimageformset(self):
    max_size = self.instance.category.images_max_size
    for form in self.forms:
        try:
            if not hasattr(form.cleaned_data['full_photo'], 'file'):
                continue
        except:
            continue

        if form.cleaned_data['full_photo'].size > max_size:
            raise forms.ValidationError(_(u'Maximum image size is %s KB') % \
                    str(max_size / 1024))

        im = Image.open(form.cleaned_data['full_photo'].file)
        allowed = self.instance.catoegy.images_allowed_formats
        if allowed_formats.filter(format=im.format).count() == 0:
            raise forms.ValidationError(
                    _(u'Your image must be in one of the following formats: ')\
                    + ', '.join(allowed_formats.values_list('format',
                                                            flat=True)))


def context_sortable(request, ads, perpage=settings.ADS_PER_PAGE):
    order = '-'
    sort = 'expires_on'
    page = 1

    if 'perpage' in request.GET and request.GET['perpage'] != '':
        perpage = int(request.GET['perpage'])

    if 'order' in request.GET and request.GET['order'] != '':
        if request.GET['order'] == 'desc':
            order = '-'
        elif request.GET['order'] == 'asc':
            order = ''

    if 'page' in request.GET:
        page = int(request.GET['page'])

    if 'sort' in request.GET and request.GET['sort'] != '':
        sort = request.GET['sort']

    if sort in ['created_on', 'expires_on', 'category', 'title']:
        ads_sorted = ads.extra(select={'featured': """SELECT 1
FROM `classifieds_payment_options`
LEFT JOIN `classifieds_payment` ON `classifieds_payment_options`.`payment_id` = `classifieds_payment`.`id`
LEFT JOIN `classifieds_pricing` ON `classifieds_pricing`.`id` = `classifieds_payment`.`pricing_id`
LEFT JOIN `classifieds_pricingoptions` ON `classifieds_payment_options`.`pricingoptions_id` = `classifieds_pricingoptions`.`id`
WHERE `classifieds_pricingoptions`.`name` = %s
AND `classifieds_payment`.`ad_id` = `classifieds_ad`.`id`
AND `classifieds_payment`.`paid` =1
AND `classifieds_payment`.`paid_on` < NOW()
AND DATE_ADD( `classifieds_payment`.`paid_on` , INTERVAL `classifieds_pricing`.`length`
DAY ) > NOW()"""}, select_params=[PricingOptions.FEATURED_LISTING]).extra(order_by=['-featured', order + sort])
    else:
        ads_sorted = ads.extra(select=SortedDict([('fvorder', 'select value from classifieds_fieldvalue LEFT JOIN classifieds_field on classifieds_fieldvalue.field_id = classifieds_field.id where classifieds_field.name = %s and classifieds_fieldvalue.ad_id = classifieds_ad.id'), ('featured', """SELECT 1
FROM `classifieds_payment_options`
LEFT JOIN `classifieds_payment` ON `classifieds_payment_options`.`payment_id` = `classifieds_payment`.`id`
LEFT JOIN `classifieds_pricing` ON `classifieds_pricing`.`id` = `classifieds_payment`.`pricing_id`
LEFT JOIN `classifieds_pricingoptions` ON `classifieds_payment_options`.`pricingoptions_id` = `classifieds_pricingoptions`.`id`
WHERE `classifieds_pricingoptions`.`name` = %s
AND `classifieds_payment`.`ad_id` = `classifieds_ad`.`id`
AND `classifieds_payment`.`paid` =1
AND `classifieds_payment`.`paid_on` < NOW()
AND DATE_ADD( `classifieds_payment`.`paid_on` , INTERVAL `classifieds_pricing`.`length`
DAY ) > NOW()""")]), select_params=[sort, PricingOptions.FEATURED_LISTING]).extra(order_by=['-featured', order + 'fvorder'])

    pager = Paginator(ads_sorted, perpage)

    try:
        page = pager.page(page)
    except InvalidPage:
        page = {'object_list': False}

    can_sortby_list = []
    sortby_list = ['created_on']
    for category in Category.objects.filter(ad__in=ads.values('pk').query).distinct():
        can_sortby_list += category.sortby_fields.split(',')

    for category in Category.objects.filter(ad__in=ads.values('pk').query).distinct():
        for fieldname, in category.field_set.values_list('name'):
            if fieldname not in sortby_list and fieldname in can_sortby_list:
                sortby_list.append(fieldname)

    for fieldname, in Field.objects.filter(category=None).values_list('name'):
        if fieldname not in sortby_list and fieldname in can_sortby_list:
            sortby_list.append(fieldname)

    return {'page': page, 'sortfields': sortby_list, 'no_results': False,
            'perpage': perpage}


def prepare_sforms(fields, fields_left, post=None):
    sforms = []
    select_fields = {}
    for field in fields:
        if field.field_type == Field.SELECT_FIELD:  # is select field
            # add select field
            options = field.options.split(',')
            choices = zip(options, options)
            choices.insert(0, ('', 'Any',))
            form_field = forms.ChoiceField(label=field.label, required=False, help_text=field.help_text + u'\nHold ctrl or command on Mac for multiple selections.', choices=choices, widget=forms.SelectMultiple)
            # remove this field from fields_list
            fields_left.remove(field.name)
            select_fields[field.name] = form_field

    sforms.append(SelectForm.create(select_fields, post))

    for sf in searchForms:
        f = sf.create(fields, fields_left, post)
        if f is not None:
            sforms.append(f)

    return sforms


class StrippingParser(HTMLParser.HTMLParser):
    # These are the HTML tags that we will leave intact
    valid_tags = ('b', 'i', 'br', 'p', 'strong', 'h1', 'h2', 'h3', 'em',
                  'span', 'ul', 'ol', 'li')

    from htmlentitydefs import entitydefs  # replace entitydefs from sgmllib

    def __init__(self):
        HTMLParser.HTMLParser.__init__(self)
        self.result = ""
        self.endTagList = []

    def handle_data(self, data):
        if data:
            self.result = self.result + data

    def handle_charref(self, name):
        self.result = "%s&#%s;" % (self.result, name)

    def handle_entityref(self, name):
        if name in self.entitydefs:
            x = ';'
        else:
            # this breaks unstandard entities that end with ';'
            x = ''
            self.result = "%s&%s%s" % (self.result, name, x)

    def handle_starttag(self, tag, attrs):
        """ Delete all tags except for legal ones """
        if tag in self.valid_tags:
            self.result = self.result + '<' + tag
            for k, v in attrs:
                if string.lower(k[0:2]) != 'on' and \
                   string.lower(v[0:10]) != 'javascript':
                    self.result = '%s %s="%s"' % (self.result, k, v)

            endTag = '</%s>' % tag
            self.endTagList.insert(0, endTag)
            self.result = self.result + '>'

    def handle_endtag(self, tag):
        if tag in self.valid_tags:
            self.result = "%s</%s>" % (self.result, tag)
            remTag = '</%s>' % tag
            self.endTagList.remove(remTag)

    def cleanup(self):
        """ Append missing closing tags """
        for j in range(len(self.endTagList)):
            self.result = self.result + self.endTagList[j]


def strip(s):
    """ Strip illegal HTML tags from string s """
    parser = StrippingParser()
    parser.feed(s)
    parser.close()
    parser.cleanup()
    return parser.result


class TinyMCEWidget(forms.Textarea):
    def __init__(self, *args, **kwargs):
        attrs = kwargs.setdefault('attrs', {})
        if 'class' not in attrs:
            attrs['class'] = 'tinymce'
        else:
            attrs['class'] += ' tinymce'

        super(TinyMCEWidget, self).__init__(*args, **kwargs)

    class Media:
        js = ('js/tiny_mce/tiny_mce.js', 'js/tinymce_forms.js',)


class TinyMCEField(forms.CharField):
    def clean(self, value):
        """Validates max_length and min_length. Returns a Unicode object."""
        if value in EMPTY_VALUES:
            return u''

        stripped_value = re.sub(r'<.*?>', '', value)
        stripped_value = string.replace(stripped_value, '&nbsp;', ' ')
        stripped_value = string.replace(stripped_value, '&lt;', '<')
        stripped_value = string.replace(stripped_value, '&gt;', '>')
        stripped_value = string.replace(stripped_value, '&amp;', '&')
        stripped_value = string.replace(stripped_value, '\n', '')
        stripped_value = string.replace(stripped_value, '\r', '')

        value_length = len(stripped_value)
        value_length -= 1
        if self.max_length is not None and value_length > self.max_length:
            raise forms.ValidationError(self.error_messages['max_length'] % {'max': self.max_length, 'length': value_length})
        if self.min_length is not None and value_length < self.min_length:
            raise forms.ValidationError(self.error_messages['min_length'] % {'min': self.min_length, 'length': value_length})

        return value


def field_list(instance):
    class MockField:
        def __init__(self, name, field_type, label, required, help_text, enable_wysiwyg, max_length):
            self.name = name
            self.field_type = field_type
            self.label = label
            self.required = required
            self.help_text = help_text
            self.enable_wysiwyg = enable_wysiwyg
            self.max_length = max_length

    title_field = MockField('title', Field.CHAR_FIELD, _('Title'), True, '', False, 100)

    fields = [title_field]  # all ads have titles
    fields += list(instance.category.field_set.all())
    fields += list(Field.objects.filter(category=None))
    return fields


def fields_for_ad(instance):
    # generate a sorted dict of fields corresponding to the Field model
    # for the Ad instance
    fields_dict = SortedDict()
    fields = field_list(instance)
    # this really, really should be refactored
    for field in fields:
        if field.field_type == Field.BOOLEAN_FIELD:
            fields_dict[field.name] = forms.BooleanField(label=field.label, required=False, help_text=field.help_text)
        elif field.field_type == Field.CHAR_FIELD:
            widget = forms.TextInput
            fields_dict[field.name] = forms.CharField(label=field.label, required=field.required, max_length=field.max_length, help_text=field.help_text, widget=widget)
        elif field.field_type == Field.DATE_FIELD:
            fields_dict[field.name] = forms.DateField(label=field.label, required=field.required, help_text=field.help_text)
        elif field.field_type == Field.DATETIME_FIELD:
            fields_dict[field.name] = forms.DateTimeField(label=field.label, required=field.required, help_text=field.help_text)
        elif field.field_type == Field.EMAIL_FIELD:
            fields_dict[field.name] = forms.EmailField(label=field.label, required=field.required, help_text=field.help_text)
        elif field.field_type == Field.FLOAT_FIELD:
            fields_dict[field.name] = forms.FloatField(label=field.label, required=field.required, help_text=field.help_text)
        elif field.field_type == Field.INTEGER_FIELD:
            fields_dict[field.name] = forms.IntegerField(label=field.label, required=field.required, help_text=field.help_text)
        elif field.field_type == Field.TIME_FIELD:
            fields_dict[field.name] = forms.TimeField(label=field.label, required=field.required, help_text=field.help_text)
        elif field.field_type == Field.URL_FIELD:
            fields_dict[field.name] = forms.URLField(label=field.label, required=field.required, help_text=field.help_text)
        elif field.field_type == Field.SELECT_FIELD:
            options = field.options.split(',')
            fields_dict[field.name] = forms.ChoiceField(label=field.label, required=field.required, help_text=field.help_text, choices=zip(options, options))
        elif field.field_type == Field.TEXT_FIELD:
            if field.enable_wysiwyg:
                widget = TinyMCEWidget
                field_type = TinyMCEField
            else:
                widget = forms.Textarea
                field_type = forms.CharField

            fields_dict[field.name] = field_type(label=field.label,
                                                 required=field.required,
                                                 help_text=field.help_text,
                                                 max_length=field.max_length,
                                                 widget=widget)
        else:
            raise NotImplementedError(u'Unknown field type "%s"' % field.get_field_type_display())

    return fields_dict
