from .models import Recipe, Ingrindient, Amount, User, ShopList


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

    counter = 0
    limit = len(units) - 1
    total_ings = [] # результирующий список

    while counter <= limit: # наполнение результирующего списка
        total_ings.append(total_ings_names[counter])
        total_ings.append(' - ')
        total_ings.append(units[counter])
        total_ings.append(' ')
        total_ings.append(total_ings_dimensions[counter])
        total_ings.append('; ')
        counter += 1

    return total_ings


