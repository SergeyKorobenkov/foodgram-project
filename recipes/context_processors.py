from .models import Recipe, Tag, Favors, ShopList


def counter(request):
    ''' длина списка покупок для отображения счетчика'''
    
    if request.user.is_authenticated:
        count = ShopList.objects.filter(user=request.user).all().count()
    else:
        count = []
    return {'count': count}


def shop(request):
    ''' изменение кнопки добавления в список покупок'''

    if request.user.is_authenticated:
        # кусок для изменения кнопки добавленности в список покупок
        pre_shop_list = ShopList.objects.filter(user=request.user).all()
        shop_list = []
        for item in pre_shop_list:
            shop_list.append(item.recipe.id)
    else:
        shop_list = []
    return {'shop_list': shop_list}


def all_tags(request):
    ''' вывод всех тегов'''

    all_tags = Tag.objects.all()
    return {'all_tags': all_tags}


def is_favor(request):
    ''' заполнение звездочки'''

    if request.user.is_authenticated:
        recipe_list = Recipe.objects.all()
        # нужно что бы заполнить звездочку
        favor_list = Favors.objects.filter(user=request.user).all()
        total_favor = []  # нужно что бы сравнить элементы в шаблоне
        for item in recipe_list:  # для элементов из списка рецептов
            for fitem in favor_list:  # для элемента из списка избранного
                # сравниваем title каждого элемента
                if item.title == fitem.recipe.title:
                    total_favor.append(item.title)
    else:
        total_favor = []
    return {'favor_list': total_favor}


def url_parse(request):
    ''' установка фильтров в урл страницы'''

    result_str = ''
    for item in request.GET.getlist('filters'):
        result_str += f'&filters={item}'
    return {'filters': result_str}
