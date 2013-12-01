from django import template
from django.conf import settings

from django.template import *

register = template.Library()


@register.simple_tag
def analytics():
    analytics_id = getattr(settings, 'ANALYTICS_ID', None)
    if analytics_id.strip() != '':
        t = loader.get_template('ga_snippet.html')
        c = Context({
            'analytics_code': analytics_id,
        })
        return t.render(c)

    else:
        return ""