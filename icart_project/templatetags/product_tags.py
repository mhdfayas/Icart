# Create a file named templatetags/product_tags.py in your app folder

from django import template

register = template.Library()

@register.filter
def filter_by_index(queryset, index):
    """
    Get a non-primary product image by index
    """
    # Filter only non-primary images
    non_primary_images = [img for img in queryset if not img.is_primary]
    
    # Convert from 1-based to 0-based indexing and check bounds
    index = int(index) - 1
    if 0 <= index < len(non_primary_images):
        return non_primary_images[index]
    return None