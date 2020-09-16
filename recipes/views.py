import json

from django.core.cache import cache
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import View


from .forms import RecipeForm
from .models import Recipe, Ingredient, Amount, User, Follow, Favors, ShopList
from .utils import generate_shop_list, get_ingredients


def index(request):
    ''' Отображение главной страницы'''

    if request.GET.getlist('filters'):
        tags_values = dict(request.GET)['filters']  # получаем названия тегов
        recipe_list = Recipe.objects.filter(
            tag__value__in=tags_values).distinct().all()
    else:
        recipe_list = Recipe.objects.all()

    paginator = Paginator(recipe_list, 6)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(request, 'index.html',
        {'page': page, 'paginator': paginator, })




@login_required
def new_recipe(request):
    ''' Создание нового рецепта.'''

    if request.method == 'POST':
        form = RecipeForm(request.POST or None, files=request.FILES or None)
        ingredients = get_ingredients(request)
        
        if not bool(ingredients):
            form.add_error(None, 'Добавьте ингредиенты')

        elif form.is_valid():
            recipe = form.save(commit=False)
            recipe.author = request.user
            recipe.save()

            # это нужно для нормального заполнения БД ингредиентами
            for item in ingredients:
                Amount.objects.create(
                    units=ingredients[item],
                    ingredient=Ingredient.objects.get(name=f'{item}'),
                    recipe=recipe)

            form.save_m2m()  # это нужно для нормального заполнения тегами
            return redirect('recipes:index')

    else:
        form = RecipeForm(request.POST or None, files=request.FILES or None)

    return render(request, 'new_recipe.html', {'form': form, })


class Ingredients(View):
    ''' Класс для автозаполнения поля ингридиента.
    Общается по API.js с фронтом и ищет совпадения 
    введенного текста с базой.'''
    
    def get(self, request):
        text = request.GET['query']

        # Обертка в list() нужна что бы api.js переварил
        # формат ответа
        ingredients = list(Ingredient.objects.filter(
            title__contains=text).values('title', 'dimension'))

        return JsonResponse(ingredients, safe=False)




@login_required
def recipe_edit(request, recipe_id):
    ''' Изменение рецепта'''

    recipe = get_object_or_404(Recipe, id=recipe_id)

    if request.user != recipe.author:
        return redirect('recipes:index')

    if request.method == "POST":
        form = RecipeForm(request.POST or None,
            files=request.FILES or None, instance=recipe)
        ingredients = get_ingredients(request)
        if form.is_valid():
            # удаляем все записи об ингредиентах из базы
            Amount.objects.filter(recipe=recipe).all().delete()

            recipe = form.save(commit=False)
            recipe.author = request.user
            recipe.save()

            # Заполняем новыми ингредиентами
            for item in ingredients:
                Amount.objects.create(
                    units=ingredients[item],
                    ingredient=Ingredient.objects.get(name=f'{item}'),
                    recipe=recipe)
            form.save_m2m()  # это нужно для нормального заполнения тегами
            return redirect('recipes:index')

    form = RecipeForm(request.POST or None,
        files=request.FILES or None, instance=recipe)

    return render(request, 'change_recipe.html',
        {'form': form, 'recipe': recipe, })


def recipe_view(request, recipe_id, username):
    ''' Просмотр рецепта'''

    recipe = get_object_or_404(Recipe, id=recipe_id)
    profile = get_object_or_404(User, username=username)

    if request.user.is_authenticated:

        # костыль на меняющуюся кнопку подписки
        is_subs = Follow.objects.filter(
            user=request.user).filter(author=recipe.author.id)

        return render(request, 'recipe.html',
        {'profile': profile, 'recipe': recipe, 'subs': is_subs, })

    else:
        return render(request, 'recipe.html',
            {'profile': profile, 'recipe': recipe, })


@login_required
def recipe_delete(request, recipe_id):
    ''' Удаление рецепта'''

    recipe = get_object_or_404(Recipe, id=recipe_id)
    if request.user != recipe.author:
        return redirect('recipes:index')
    else:
        recipe.delete()
        return redirect('recipes:index')


def profile(request, username):
    ''' Профиль пользователя'''

    profile = get_object_or_404(User, username=username)

    if request.GET.getlist('filters'):
        tags_values = dict(request.GET)['filters']  # получаем названия тегов
        recipe_list = Recipe.objects.filter(
            tag__value__in=tags_values, author=profile.pk).all()

    else:
        recipe_list = Recipe.objects.filter(
            author=profile.pk).all()

    paginator = Paginator(recipe_list, 6)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    if request.user.is_authenticated:

        # костыль на меняющуюся кнопку подписки
        is_subs = Follow.objects.filter(
            user=request.user).filter(author=profile.id)

        return render(request, 'profile.html',
            {'profile': profile, 'recipe_list': recipe_list,
            'page': page, 'paginator': paginator, 'subs': is_subs, })

    else:
        return render(request, 'profile.html',
            {'profile': profile, 'recipe_list': recipe_list,
            'page': page, 'paginator': paginator, })


class Favorites(View):
    ''' добавление и удаление рецепта в избранные'''

    def post(self, request):
        recipe_id = json.loads(request.body)['id']
        recipe = get_object_or_404(Recipe, id=recipe_id)
        Favors.objects.get_or_create(
            user=request.user, recipe=recipe)

        return JsonResponse({'recipe_id': 'recipe'})

    def delete(self, request, recipe_id):
        recipe = get_object_or_404(Recipe, id=recipe_id)
        Favors.objects.get(
            user=request.user, recipe=recipe).delete()
        return JsonResponse({'succes': 'True'})


class Purchases(View):
    ''' добавление и удаление рецепта в список покупок '''

    def post(self, request):
        recipe_id = json.loads(request.body)['id']
        recipe = get_object_or_404(Recipe, id=recipe_id)
        ShopList.objects.get_or_create(
            user=request.user, recipe=recipe)

        return JsonResponse({'recipe_id': 'recipe'})

    def delete(self, request, recipe_id):
        recipe = get_object_or_404(Recipe, id=recipe_id)
        ShopList.objects.get(
            user=request.user, recipe=recipe).delete()
        return JsonResponse({'succes': 'True'})


class Subscription(View):
    ''' добавление и удаление профиля в подписки '''

    def post(self, request):
        author_id = json.loads(request.body)['id']
        author = get_object_or_404(User, id=author_id)
        Follow.objects.get_or_create(
            user=request.user, author=author_id)

        return JsonResponse({'succes': 'True'})

    def delete(self, request, recipe_id):
        # Он все еще шлет переменную под названием recipe_id,
        # но кладет туда id автора, а не рецепта.
        # Даже с учетом правок.
        author = get_object_or_404(User, id=recipe_id)
        Follow.objects.get(
            user=request.user, author=author).delete()
        return JsonResponse({'succes': 'True'})


@login_required
def favors_view(request, username):
    ''' Просмотр избранных рецептов'''

    favor_list = Favors.objects.filter(user=request.user).all()
    recipes_titles = []
    for item in favor_list:
        recipes_titles.append(item.recipe.title)
    if request.GET.getlist('filters'):
        tags_values = dict(request.GET)['filters']  # получаем названия тегов
        recipe_list = Recipe.objects.filter(
            title__in=recipes_titles, tag__value__in=tags_values).distinct().all()

    else:
        recipe_list = Recipe.objects.filter(title__in=recipes_titles).all()
    paginator = Paginator(recipe_list, 6)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
 
    return render(request, 'favorite.html',
        {'page': page, 'paginator': paginator, })




@login_required
def subs_view(request, username):
    ''' Просмотр списка подписок'''

    who_user = get_object_or_404(User, username=username)

    subs_list = who_user.follower.values('author').all()
    authors_list = User.objects.filter(
        id__in=subs_list).all()

    paginator = Paginator(authors_list, 6)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    # Блок для передачи списка рецептов для отрисовки в карточках пользователей
    card_page = Recipe.objects.filter(
        author__id__in=subs_list).all()

    return render(request, 'my_subs.html',
        {'card_page': card_page, 'page': page, 'paginator': paginator, 'authors':authors_list})


def shop(request):
    ''' Просмотр списка покупок'''

    shop_list = ShopList.objects.filter(user=request.user).all()
    return render(request, 'shopList.html', {'shop_list': shop_list})


@login_required
def download(request):
    ''' скачивание списка покупок'''
    
    result = generate_shop_list(request)  # вызов скрипта на составление файла
    filename = 'ingredients.txt'  # именуем файл
    response = HttpResponse(result, content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename={0}'.format(filename)
    return response
