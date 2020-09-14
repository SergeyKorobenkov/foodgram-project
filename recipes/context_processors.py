from .models import Recipe, Tag, Ingrindient, Amount, User, Follow, Favors, ShopList


# длина списка покупок для отображения счетчика
def counter(request):
    if request.user.is_authenticated:
        count = ShopList.objects.filter(user=request.user).all().count()
    else:
        count = []
    return {'count':count}


# изменение кнопки добавления в список покупок
def shop(request):
    if request.user.is_authenticated:
        pre_shop_list = ShopList.objects.filter(user=request.user).all() # кусок для изменения кнопки добавленности в список покупок
        shop_list = []
        for item in pre_shop_list:
            shop_list.append(item.recipe.id)
        
    else:
        shop_list = []
    return {'shop_list':shop_list}


# вывод всех тегов
def all_tags(request):
    all_tags = Tag.objects.all()
    return {'all_tags':all_tags}


# заполнение звездочки
def is_favor(request):
    if request.user.is_authenticated:
        recipe_list = Recipe.objects.all()
        favor_list = Favors.objects.filter(user=request.user).all() # нужно что бы заполнить звездочку
        total_favor = [] # нужно что бы сравнить элементы в шаблоне
        for item in recipe_list: # для элементов из списка рецептов
            for fitem in favor_list: # для элемента из списка избранного 
                if item.title == fitem.recipe.title: # сравниваем title каждого элемента
                    total_favor.append(item.title) 
    else:
        total_favor = []
    return {'favor_list':total_favor}