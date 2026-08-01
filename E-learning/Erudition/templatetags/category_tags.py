from django import template
from Erudition.models import Category

register = template.Library()

@register.inclusion_tag('Erudition/category_tabs.html', takes_context=True)
def category_tabs(context, active_slug=None):
    """Render category tabs.

    Usage:
      {% load category_tags %}
      {% category_tabs %}
      {% category_tabs active_slug=slug %}

    This inclusion tag queries the Category model so templates don't need to provide the
    category list in every view.
    """
    categories = Category.objects.order_by('name')
    request = context.get('request')
    request_path = request.path if request else ''

    return {
        'categories': categories,
        'active_slug': active_slug,
        'request_path': request_path,
    }
