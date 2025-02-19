from .models import Category

def parent_categories(request):
    """
    Provide only parent categories to all templates.
    """
    categories = Category.objects.filter(parent__isnull=True)  # Only fetch top-level categories
    return {'categories': categories}
