from .models import ShopList
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model


User = get_user_model()


def generate_shop_list(request):
    ''' скрипт для генерации списка покупок'''
    # получаем список покупок для юзера
    buyer = get_object_or_404(User, username=request.user.username)
    shop_list = buyer.buyer.all()
    ingredients_dict = {}

    # формируем словарь что бы можно было удобно суммировать повторения
    for item in shop_list:
        for amount in item.recipe.amount_set.all():

            name = f'{amount.ingredient.title} ({amount.ingredient.dimension})'
            units = amount.units

            # наполняем словарь
            if name in ingredients_dict.keys():
                ingredients_dict[name] += units
            else:
                ingredients_dict[name] = units

    ingredients_list = []  # список на выгрузку

    # формируем из словаря список что бы функция нормально переварила данные
    for key, units in ingredients_dict.items():
        ingredients_list.append(f'{key} - {units}, ')

    return ingredients_list  # и отдаем на выгрузку


def get_ingredients(request):
    ''' Скрипт для генерации списка ингредиентов на передачу в БД
    при создании/редактировании рецепта'''

    ingredients = {}
    for key in request.POST:
        if key.startswith('nameIngredient'):
            value_ingredient = key[15:]
            ingredients[request.POST[key]] = request.POST[
                'valueIngredient_' + value_ingredient
            ]
    return ingredients
