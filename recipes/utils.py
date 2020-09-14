from .models import Recipe, Ingrindient, Amount, User, ShopList


# скрипт для генерации списка покупок

def generate_shop_list(request):
    shop_list = ShopList.objects.filter(user=request.user).all() # получаем список покупок для юзера
    
    pre_ings = [] # здесь кверисеты с ингридиентами пользователя
    total_ings_names = [] # здесь лежат названия ингредиентов 
    total_ings_dimensions = [] # здесь лежат размерности ингредиентов
    
    pre_units = [] # здесь лежат кверисеты модели Amount
    units = [] # здесь лежит количество ингредиентов по моделям 

    for item in shop_list: # наполняем кверисетами
        pre_ings.append(item.recipe.ingrindient.all())
    for item in pre_ings: # наполняем объектами класса Ingrindient
        for obj in item:
            total_ings_names.append(obj.name)
            total_ings_dimensions.append(obj.dimension)

    for item in shop_list: # наполняем кверисетами
        pre_units.append(item.recipe.amount_set.all())
    for item in pre_units: # наполняем количеством ингредиентов
        for obj in item:
            units.append(obj.units)

    counter = 0 # счетчик что бы не уйти в вечный цикл
    limit = len(units) - 1 # предел счетчика
    total_ings = [] # результирующий список

    while counter <= limit: # наполнение результирующего списка
        total_ings.append(total_ings_names[counter])
        total_ings.append(' - ')
        total_ings.append(units[counter])
        total_ings.append(' ')
        total_ings.append(total_ings_dimensions[counter])
        total_ings.append('; ')
        counter += 1 

    return total_ings # и отдаем на выгрузку

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