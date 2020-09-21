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
    """Отображение главной страницы."""

    tags_values = request.GET.getlist('filters')

    if tags_values:
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
    """Создание нового рецепта."""

    if request.method == 'POST':
        form = RecipeForm(request.POST or None, files=request.FILES or None)
        ingredients = get_ingredients(request)
        
        if not ingredients:
            form.add_error(None, 'Добавьте ингредиенты')

        elif form.is_valid():
            recipe = form.save(commit=False)
            recipe.author = request.user
            recipe.save()

            # это нужно для нормального заполнения БД ингредиентами
            for item in ingredients:
                Amount.objects.create(
                    units=ingredients[item],
                    ingredient=Ingredient.objects.get(title=f'{item}'),
                    recipe=recipe)

            form.save_m2m()  # это нужно для нормального заполнения тегами
            return redirect('recipes:index')

    else:
        form = RecipeForm(request.POST or None, files=request.FILES or None)

    return render(request, 'new_recipe.html', {'form': form, })


class Ingredients(View):
    """Класс для автозаполнения поля ингридиента.
    Общается по API.js с фронтом и ищет совпадения 
    введенного текста с базой.
    """
    
    def get(self, request):
        text = request.GET['query']

        # Обертка в list() нужна что бы api.js переварил
        # формат ответа

        ingredients = list(Ingredient.objects.filter(
            title__icontains=text).values('title', 'dimension'))

        return JsonResponse(ingredients, safe=False)




@login_required
def recipe_edit(request, recipe_id):
    """Изменение рецепта."""

    recipe = get_object_or_404(Recipe, id=recipe_id)

    if request.user != recipe.author:
        return redirect('recipes:index')

    if request.method == "POST":
        form = RecipeForm(request.POST or None,
            files=request.FILES or None, instance=recipe)
        ingredients = get_ingredients(request)
        if form.is_valid():
            # удаляем все записи об ингредиентах из базы
            Amount.objects.filter(recipe=recipe).delete()

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
    """Просмотр рецепта."""

    recipe = get_object_or_404(Recipe, id=recipe_id)
    profile = get_object_or_404(User, username=username)

    if request.user.is_authenticated:

        return render(request, 'recipe.html',
        {'profile': profile, 'recipe': recipe,})

    else:
        return render(request, 'recipe.html',
            {'profile': profile, 'recipe': recipe, })


@login_required
def recipe_delete(request, recipe_id):
    """Удаление рецепта."""

    recipe = get_object_or_404(Recipe, id=recipe_id)
    if request.user != recipe.author:
        return redirect('recipes:index')
    else:
        recipe.delete()
        return redirect('recipes:index')


def profile(request, username):
    """Профиль пользователя."""

    profile = get_object_or_404(User, username=username)
    tags_values = request.GET.getlist('filters')
    
    if tags_values:
        recipe_list = Recipe.objects.filter(
            tag__value__in=tags_values, author=profile.pk).all()

    else:
        recipe_list = Recipe.objects.filter(
            author=profile.pk).all()

    paginator = Paginator(recipe_list, 6)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    if request.user.is_authenticated:

        return render(request, 'profile.html',
            {'profile': profile, 'recipe_list': recipe_list,
            'page': page, 'paginator': paginator,})

    else:
        return render(request, 'profile.html',
            {'profile': profile, 'recipe_list': recipe_list,
            'page': page, 'paginator': paginator, })


class Favorites(View):
    """Добавление и удаление рецепта в избранные."""

    def post(self, request):
        recipe_id = json.loads(request.body)['id']
        recipe = get_object_or_404(Recipe, id=recipe_id)
        
        try:
            Favors.objects.get_or_create(
                user=request.user, recipe=recipe)
            return JsonResponse({'success': True})
        
        except:
            return JsonResponse({'success': False})

    def delete(self, request, recipe_id):
        recipe = get_object_or_404(Recipe, id=recipe_id)
        user = get_object_or_404(User, username=request.user.username)
        obj = get_object_or_404(Favors, user=user, recipe=recipe)
        try:
            obj.delete()
            return JsonResponse({'success': True})
        
        except:
            return JsonResponse({'success': False})


class Purchases(View):
    """Добавление и удаление рецепта в список покупок."""

    def post(self, request):
        recipe_id = json.loads(request.body)['id']
        recipe = get_object_or_404(Recipe, id=recipe_id)
        
        try:
            ShopList.objects.get_or_create(
                user=request.user, recipe=recipe)
            return JsonResponse({'success': True})
        
        except:
            return JsonResponse({'success': False})

    def delete(self, request, recipe_id):
        recipe = get_object_or_404(Recipe, id=recipe_id)
        user = get_object_or_404(User, username=request.user.username)
        obj = get_object_or_404(ShopList, user=user, recipe=recipe)
        
        try:
            obj.delete()
            return JsonResponse({'success': True})
        
        except:
            return JsonResponse({'success': False})


class Subscription(View):
    """Добавление и удаление профиля в подписки."""

    def post(self, request):
        author_id = json.loads(request.body)['id']
        author = get_object_or_404(User, id=author_id)
        
        try:
            Follow.objects.get_or_create(
                user=request.user, author=author)
            
            return JsonResponse({'success': True})
        
        except:
            return JsonResponse({'success': False})

    def delete(self, request, author_id):
        user = get_object_or_404(User, username=request.user.username)
        author = get_object_or_404(User, id=author_id)
        obj = get_object_or_404(Follow, user=user, author=author)
        
        try:
            obj.delete()
            return JsonResponse({'success': True})
        
        except:
            return JsonResponse({'success': False})


@login_required
def favors_view(request, username):
    """Просмотр избранных рецептов."""

    tags_values = request.GET.getlist('filters')

    if tags_values:
        recipe_list = Recipe.objects.filter(
            favor__user__id=request.user.id,
            tag__value__in=tags_values).distinct().all()

    else:
        recipe_list = Recipe.objects.filter(
            favor__user__id=request.user.id).all()

    paginator = Paginator(recipe_list, 6)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
 
    return render(request, 'favorite.html',
        {'page': page, 'paginator': paginator, })




@login_required
def subs_view(request, username):
    """Просмотр списка подписок."""

    who_user = get_object_or_404(User, username=username)

    subs_list = who_user.follower.values('author').all()
    authors_list = User.objects.filter(
        id__in=subs_list).all()

    paginator = Paginator(authors_list, 6)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(request, 'my_subs.html',
        {'page': page, 'paginator': paginator, 'authors':authors_list})


def shop(request):
    """Просмотр списка покупок."""

    shop_list = ShopList.objects.filter(user=request.user).all()
    return render(request, 'shop_list.html', {'shop_list': shop_list})


@login_required
def download(request):
    """Скачивание списка покупок."""
    
    result = generate_shop_list(request)  # вызов скрипта на составление файла
    filename = 'ingredients.txt'  # именуем файл
    response = HttpResponse(result, content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename={0}'.format(filename)
    return response
