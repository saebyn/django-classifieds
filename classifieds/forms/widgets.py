
from django.forms import Textarea

class TinyMCEWidget(Textarea):
    def __init__(self, *args, **kwargs):
        attrs = kwargs.setdefault('attrs',{})
        if 'class' not in attrs:
            attrs['class'] = 'tinymce'
        else:
            attrs['class'] += ' tinymce'
        
        super(TinyMCEWidget, self).__init__(*args, **kwargs)
    
    class Media:
        js = ('js/tiny_mce/tiny_mce.js','js/tinymce_forms.js',)
