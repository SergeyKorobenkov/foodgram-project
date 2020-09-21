from .models import Recipe, Tag, Favors, ShopList


def counter(request):
    """Длина списка покупок для отображения счетчика."""
    
    if request.user.is_authenticated:
        count = ShopList.objects.filter(user=request.user).count()
    else:
        count = []
    return {'count': count}


def shop(request):
    """Изменение кнопки добавления в список покупок."""

    if request.user.is_authenticated:
        # кусок для изменения кнопки добавленности в список покупок
        shop_list = ShopList.objects.filter(
            user=request.user).values_list('recipe_id', flat=True)

    else:
        shop_list = []
    return {'shop_list': shop_list}


def all_tags(request):
    """Вывод всех тегов."""

    all_tags = Tag.objects.all()
    return {'all_tags': all_tags}


def url_parse(request):
    """Установка фильтров в урл страницы."""

    result_str = ''
    for item in request.GET.getlist('filters'):
        result_str += f'&filters={item}'
    return {'filters': result_str}
