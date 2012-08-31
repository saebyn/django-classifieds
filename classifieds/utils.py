# vim: set fileencoding=utf-8 ft=python ff=unix nowrap tabstop=4 shiftwidth=4 softtabstop=4 smarttab shiftround expandtab :
"""
Various utility functions for django-classifieds.
"""

from PIL import Image
import os.path

from django.utils.datastructures import SortedDict
from django.utils.translation import ugettext as _
from django.core.paginator import Paginator, InvalidPage
from django.template.loader import get_template
from django.template import TemplateDoesNotExist, RequestContext

from django import forms
from django.http import HttpResponse

from sorl.thumbnail import ImageField

from classifieds.conf import settings
from classifieds.search import SelectForm, searchForms
from classifieds.models import Field, Category
from classifieds.forms.fields import TinyMCEField
from classifieds.forms.widgets import TinyMCEWidget


def category_template_name(category, page):
    return os.path.join(u'classifieds/category',
                        category.template_prefix, page)


# TODO consider moving this into a class based view base class?
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
        allowed_formats = self.instance.category.images_allowed_formats
        if not allowed_formats.filter(format=im.format).exists():
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
        ads_sorted = ads.sort_featured_ads(order + sort)
    else:
        ads_sorted = ads.sort_featured_ads().order_by_field(order + sort)

    pager = Paginator(ads_sorted, perpage)

    try:
        page = pager.page(page)
    except InvalidPage:
        page = {'object_list': False}

    can_sortby_fields = set()
    sortby_fields = set(['created_on'])
    # Use the simpler `ads` query here since we don't need the ordering.
    categories = Category.objects.filter(ad__in=ads.values('pk').query).distinct()
    for category in categories:
        can_sortby_fields.update(category.sortby_fields.split(','))

    for category in categories:
        for fieldname, in category.field_set.values_list('name'):
            if fieldname in can_sortby_fields:
                sortby_fields.add(fieldname)

    for fieldname, in Field.objects.filter(category=None).values_list('name'):
        if fieldname in can_sortby_fields:
            sortby_fields.append(fieldname)

    return {'page': page, 'sortfields': sortby_fields, 'no_results': False,
            'perpage': perpage}


def prepare_search_forms(fields, fields_left, post=None):
    # TODO refactor this
    sforms = []
    select_fields = {}
    for field in fields:
        if field.field_type == Field.SELECT_FIELD:  # is select field
            # add select field
            options = field.options.split(',')
            choices = zip(options, options)
            choices.insert(0, ('', 'Any',))
            form_field = forms.ChoiceField(label=field.label,
                    required=False,
                    help_text=field.help_text + _(u'\nHold ctrl or command on Mac for multiple selections.'),
                    choices=choices,
                    widget=forms.SelectMultiple)
            # remove this field from fields_list
            fields_left.remove(field.name)
            select_fields[field.name] = form_field

    sforms.append(SelectForm.create(select_fields, post))

    for sf in searchForms:
        f = sf.create(fields, fields_left, post)
        if f is not None:
            sforms.append(f)

    is_valid = all([f.is_valid() or f.is_empty() for f in sforms])

    return sforms, is_valid


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


def get_field(field):
    """
    >>> our_field = object()
    >>> our_field.field_type = Field.CHAR_FIELD
    >>> field, widget = get_field(our_field)
    >>> field.__class__.__name__
    'CharField'
    >>> widget.__class__.__name__
    'TextInput'
    """
    mapping = {
        Field.BOOLEAN_FIELD: (forms.BooleanField, None),
        Field.CHAR_FIELD: (forms.CharField, forms.TextInput),
        Field.DATE_FIELD: (forms.DateField, None),
        Field.DATETIME_FIELD: (forms.DateTimeField, None),
        Field.EMAIL_FIELD: (forms.EmailField, None),
        Field.FLOAT_FIELD: (forms.FloatField, None),
        Field.INTEGER_FIELD: (forms.IntegerField, None),
        Field.TIME_FIELD: (forms.TimeField, None),
        Field.URL_FIELD: (forms.URLField, None),
        Field.IMAGE_FIELD: (ImageField, None),
        Field.SELECT_FIELD: (forms.ChoiceField, None),
    }

    if field.field_type == Field.TEXT_FIELD:
        if field.enable_wysiwyg:
            return TinyMCEField, TinyMCEWidget
        else:
            return forms.CharField, forms.TextInput

    try:
        return mapping[field.field_type]
    except KeyError:
        raise NotImplementedError(u'Unknown field type "%s"' % field.get_field_type_display())


def fields_for_ad(instance):
    # generate a sorted dict of fields corresponding to the Field model
    # for the Ad instance
    fields_dict = SortedDict()
    fields = field_list(instance)
    for field in fields:
        field_type, widget = get_field(field)
        field_options = {
            'label': field.label,
            'help_text': field.help_text,
            'required': field.required
        }
        if widget is not None:
            field_options['widget'] = widget

        if field.field_type == Field.BOOLEAN_FIELD:
            field_options['required'] = False
        elif field.field_type in [Field.CHAR_FIELD, Field.TEXT_FIELD]:
            field_options['max_length'] = field.max_length
        elif field.field_type == Field.IMAGE_FIELD:
            field_options['upload_to'] = 'uploads/'
        elif field.field_type == Field.SELECT_FIELD:
            options = field.options.split(',')
            field_options['choices'] = zip(options, options)

        fields_dict[field.name] = field_type(**field_options)

    return fields_dict
