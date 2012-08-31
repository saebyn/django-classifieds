from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.urlresolvers import reverse
from django.views.generic.edit import BaseUpdateView
from django.forms.models import inlineformset_factory

from classifieds.models import Ad, AdImage
from classifieds.adform import AdForm
from classifieds.utils import clean_adimageformset, render_category_page


class AdEditView(BaseUpdateView):
    model = Ad
    form_class = AdForm
    context_object_name = 'ad'
    page = 'edit.html'

    def get_category(self):
        return self.object.category

    def render_to_response(self, context, **response_kwargs):
        category = self.get_category()
        return render_category_page(self.request, category,
                                    self.page, context)

    def get_success_url(self):
        return reverse('classifieds_manage_view_all')

    def get_context_data(self, **kwargs):
        context = super(AdEditView, self).get_context_data(**kwargs)
        context['imagesformset'] = self.imagesformset
        return context

    def get_queryset(self):
        qs = super(AdEditView, self).get_queryset()
        return qs.filter(active=True, user=self.request.user)

    def build_imageupload_formset(self):
        image_count = self.object.category.images_max_count

        ImageUploadFormSet = inlineformset_factory(Ad, AdImage,
                                                   extra=image_count,
                                                   max_num=image_count,
                                                   fields=('full_photo',))
        # enforce max width & height on images
        ImageUploadFormSet.clean = clean_adimageformset
        return ImageUploadFormSet(self.request.POST or None,
                                  self.request.FILES or None,
                                  instance=self.object)

    def form_valid(self, form):
        if self.imagesformset.is_valid():
            self.imagesformset.save()

        return super(AdEditView, self).form_valid(form)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.imagesformset = self.build_imageupload_formset()
        return super(AdEditView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.imagesformset = self.build_imageupload_formset()
        return super(AdEditView, self).post(request, *args, **kwargs)

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(AdEditView, self).dispatch(request, *args, **kwargs)


class AdCreationEditView(AdEditView):
    def get_queryset(self):
        qs = super(AdEditView, self).get_queryset()
        return qs.filter(active=False, user=self.request.user)

    def get_success_url(self):
        return reverse('classifieds_create_ad_preview',
                       kwargs=dict(pk=self.object.pk))

    def get_context_data(self, **kwargs):
        context = super(AdCreationEditView, self).get_context_data(**kwargs)
        context['create'] = True
        return context
