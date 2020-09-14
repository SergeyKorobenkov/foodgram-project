import json

from django.core.cache import cache
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import View


from .forms import RecipeForm
from .models import Recipe, Ingrindient, Amount, User, Follow, Favors, ShopList
from .utils import generate_shop_list, get_ingrindients, tags_converter


# Отображение главной страницы

def index(request):
    if request.GET.getlist('filters'):
        tags_values = dict(request.GET)['filters']  # получаем названия тегов
        tags_id = tags_converter(tags_values)  # преобразуем названия в id
        recipe_list = Recipe.objects.filter(
            tag__in=tags_id).order_by('-pub_date').all()
    else:
        recipe_list = Recipe.objects.order_by('-pub_date').all()

    paginator = Paginator(recipe_list, 6)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    cache.clear()

    return render(request, 'index.html',
        {'page': page, 'paginator': paginator, })


# Создание нового рецепта.

@login_required
def new_recipe(request):

    if request.method == 'POST':
        form = RecipeForm(request.POST or None, files=request.FILES or None)
        ingrindients = get_ingrindients(request)

        if bool(ingrindients) is False:
            form.add_error(None, 'Добавьте ингредиенты')

        elif form.is_valid():
            recipe = form.save(commit=False)
            recipe.author = request.user
            recipe.save()

            # это нужно для нормального заполнения БД ингредиентами
            for item in ingrindients:
                Amount.objects.create(
                    units=ingrindients[item],
                    ingrindient=Ingrindient.objects.filter(name=item).all()[0],
                    recipe=recipe)

            form.save_m2m()  # это нужно для нормального заполнения тегами
            return redirect('recipes: index')

    else:
        form = RecipeForm(request.POST or None, files=request.FILES or None)

    return render(request, 'new_recipe.html', {'form': form, })


# Класс для автозаполнения поля ингридиента.
# Общается по API.js с фронтом и ищет совпадения введенного текста с базой.

class Ingrindients(View):
    def get(self, request):
        text = request.GET['query']

        ing_dict = Ingrindient.objects.filter(name__contains=text)
        ing_list = []

        for item in ing_dict:
            title = item.name
            dimension = item.dimension
            total = {
                'title': title,
                'dimension': dimension,
            }
            ing_list.append(total)

        return JsonResponse(ing_list, safe=False)


# Изменение рецепта

@login_required
def recipe_edit(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)

    if request.user != recipe.author:
        return redirect('recipes: index')

    # удаляем все записи об ингредиентах из базы
    Amount.objects.filter(recipe=recipe).all().delete()

    if request.method == "POST":
        form = RecipeForm(request.POST or None,
            files=request.FILES or None, instance=recipe)
        ingrindients = get_ingrindients(request)
        if form.is_valid():
            recipe = form.save(commit=False)
            recipe.author = request.user
            recipe.save()

            # это нужно для нормального заполнения БД ингредиентами
            for item in ingrindients:
                Amount.objects.create(
                    units=ingrindients[item],
                    ingrindient=Ingrindient.objects.filter(name=item).all()[0],
                    recipe=recipe)
            form.save_m2m()  # это нужно для нормального заполнения тегами
            return redirect('recipes: index')

    form = RecipeForm(request.POST or None,
        files=request.FILES or None, instance=recipe)

    return render(request, 'change_recipe.html',
        {'form': form, 'recipe': recipe, })


# Просмотр рецепта

def recipe_view(request, recipe_id, username):
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


# Удаление рецепта

@login_required
def recipe_delete(request, recipe_id):
    recipe = Recipe.objects.get(id=recipe_id)
    if request.user != recipe.author:
        return redirect('recipes: index')
    else:
        recipe.delete()
        return redirect('recipes: index')


# Профиль пользователя

def profile(request, username):
    profile = get_object_or_404(User, username=username)

    if request.GET.getlist('filters'):
        tags_values = dict(request.GET)['filters']  # получаем названия тегов
        tags_id = tags_converter(tags_values)  # преобразуем названия в id
        recipe_list = Recipe.objects.filter(
            tag__in=tags_id, author=profile.pk).order_by('-pub_date').all()

    else:
        recipe_list = Recipe.objects.filter(
            author=profile.pk).order_by("-pub_date").all()

    paginator = Paginator(recipe_list, 6)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    cache.clear()

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


# добавление и удаление рецепта в избранные
# Очередная мутная шляпа с api.js, работает через пень-колоду.
# Но работает =)

class Favorites(View):

    def post(self, request):
        recipe_id = json.loads(request.body)['id']
        recipe = Recipe.objects.get(id=recipe_id)
        is_favor = Favors.objects.filter(
            user=request.user).filter(recipe=recipe_id)

        if is_favor:
            return JsonResponse({'recipe_id': 'recipe'})

        else:
            Favors.objects.create(user=request.user, recipe=recipe)
            return JsonResponse({'recipe_id': 'recipe'})

    def delete(self, request, recipe_id):
        recipe = Recipe.objects.get(id=recipe_id)
        Favors.objects.filter(user=request.user).filter(recipe=recipe).delete()
        return JsonResponse({'succes': 'True'})


# добавление и удаление рецепта в список покупок

class Purchases(View):
    def post(self, request):
        recipe_id = json.loads(request.body)['id']
        recipe = Recipe.objects.get(id=recipe_id)
        is_shop = ShopList.objects.filter(
            user=request.user).filter(recipe=recipe_id)

        if is_shop:
            return JsonResponse({'recipe_id': 'recipe'})

        else:
            ShopList.objects.create(user=request.user, recipe=recipe)
            print()
            return JsonResponse({'recipe_id': 'recipe'})

    def delete(self, request, recipe_id):
        recipe = Recipe.objects.get(id=recipe_id)
        ShopList.objects.filter(
            user=request.user).filter(recipe=recipe).delete()
        return JsonResponse({'succes': 'True'})


# добавление и удаление профиля в подписки

class Subscription(View):

    def post(self, request):
        author_id = json.loads(request.body)['id']
        author = User.objects.get(id=author_id)
        is_follow = Follow.objects.filter(
            user=request.user).filter(author=author_id)

        if is_follow:
            return JsonResponse({'succes': 'True'})

        else:
            Follow.objects.create(user=request.user, author=author)
            return JsonResponse({'succes': 'True'})

    def delete(self, request, recipe_id):
        # я без понятия почему он тут присылает переменную
        # под названием recipe_id, но в ней он хранит id автора.
        # Какого маракуйя я так и не понял.
        author = User.objects.get(id=recipe_id)
        Follow.objects.filter(user=request.user).filter(author=author).delete()
        return JsonResponse({'succes': 'True'})


# Просмотр избранных рецептов

@login_required
def favors_view(request, username):

    favor_list = Favors.objects.filter(user=request.user).all()
    recipes_titles = []
    for item in favor_list:
        recipes_titles.append(item.recipe.title)

    if request.GET.getlist('filters'):
        tags_values = dict(request.GET)['filters']  # получаем названия тегов
        tags_id = tags_converter(tags_values)  # преобразуем названия в id
        recipe_list = Recipe.objects.filter(
            title__in=recipes_titles, tag__in=tags_id).all()

    else:
        recipe_list = Recipe.objects.filter(title__in=recipes_titles).all()

    paginator = Paginator(recipe_list, 6)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    cache.clear()

    return render(request, 'favorite.html',
        {'page': page, 'paginator': paginator, })


# Просмотр списка подписок

@login_required
def subs_view(request, username):

    subs_list = Follow.objects.filter(user=request.user).all()

    paginator = Paginator(subs_list, 6)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    cache.clear()

    # Блок для передачи списка рецептов для отрисовки в карточках пользователей
    card_page = []
    for item in subs_list:
        author = item.author.id
        for_card = Recipe.objects.filter(author=author).all()
        card_page.append(for_card)

    return render(request, 'my_subs.html',
        {'card_page': card_page, 'page': page, 'paginator': paginator, })


# Просмотр списка покупок

def shop(request):
    shop_list = ShopList.objects.filter(user=request.user).all()
    return render(request, 'shopList.html', {'shop_list': shop_list})


# скачивание списка покупок

@login_required
def download(request):
    result = generate_shop_list(request)  # вызов скрипта на составление файла
    filename = 'ingredients.txt'  # именуем файл
    response = HttpResponse(result, content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename={0}'.format(filename)
    return response
