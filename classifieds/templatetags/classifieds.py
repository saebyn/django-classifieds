"""
"""

from django import template


register = template.Library()

# TODO thumbnail related tags (show first thumbnail, show all thumbnails,
# get count of thumbnails), ad location output tag


@register.inclusion_tag('classifieds/utils/post_ad_progress.html')
def post_ad_progress(step):
    return {'step': step}
