from django import template
register = template.Library()

@register.filter
def get_item(queryset, index):
    """
    Get a non-primary product image by index, handling both primary and non-primary images
    """
    try:
        
        non_primary_images = [img for img in queryset if not img.is_primary]
        return non_primary_images[int(index)]
    except (IndexError, TypeError, ValueError):
        return None