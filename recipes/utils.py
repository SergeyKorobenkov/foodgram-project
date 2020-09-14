from .models import ShopList


# скрипт для генерации списка покупок

def generate_shop_list(request):
    # получаем список покупок для юзера
    shop_list = ShopList.objects.filter(user=request.user).all()
    ingredients_dict = {}

    # формируем словарь что бы можно было удобно суммировать повторения
    for item in shop_list:
        for amount in item.recipe.amount_set.all():

            name = f'{amount.ingrindient.name} ({amount.ingrindient.dimension})'
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


# Скрипт для генерации списка ингредиентов на передачу в БД
# при создании/редактировании рецепта

def get_ingrindients(request):
    ingrindients = {}
    for key in request.POST:
        if key.startswith('nameIngredient'):
            value_ingredient = key[15:]
            ingrindients[request.POST[key]] = request.POST[
                'valueIngredient_' + value_ingredient
            ]
    return ingrindients


def tags_converter(values):
    tags_id = []

    for value in values:
        if value == 'breakfast':
            tags_id.append(1)
        if value == 'lunch':
            tags_id.append(2)
        if value == 'dinner':
            tags_id.append(3)
    return tags_id
