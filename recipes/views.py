from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.http import JsonResponse
from django.views.generic import View
from django.core.cache import cache

from .models import Recipe, Tag, Ingrindient, Amount, User, Follow, Favors
from .forms import RecipeForm


# Отображение главной страницы

def index(request):
    recipe_list = Recipe.objects.order_by('-pub_date').all()
    form = RecipeForm(request.POST or None, files=request.FILES or None)
    paginator = Paginator(recipe_list, 6) # показывать по 6 записей на странице.
    page_number = request.GET.get('page') # переменная в URL с номером запрошенной страницы
    page = paginator.get_page(page_number)
    cache.clear()
    return render(request, 'index.html', {'form':form, 'page':page, 'paginator':paginator,})


# Создание нового рецепта.
# !!!!!!!
# Не работает добавление ингридиентов в рецепт если делать с фронта. 
# !!!!!!!

@login_required
def new_recipe(request):
    if request.method == 'POST':
        form = RecipeForm(request.POST or None, files=request.FILES or None)
        if form.is_valid():
            recipe = form.save(commit=False)
            recipe.author = request.user
            recipe.save()
            return redirect('recipes:index')
    form = RecipeForm(request.POST or None, files=request.FILES or None)
    return render(request, 'new_recipe.html', {'form': form})
    

# Класс для автозаполнения поля ингридиента.
# Общается по API.js с фронтом и ищет совпадения введенного текста с базой.

class Ingrindients(View):
    def get(self, request):
        text = request.GET['query']
        print(text) # артефакт. Мб оставить?

        ing_dict = Ingrindient.objects.filter(name__contains=text)
        ing_list = []

        for item in ing_dict:
            title = item.name
            dimension = item.dimension
            total = {
                'title':title,
                'dimension':dimension,
            }
            ing_list.append(total)
        
        return JsonResponse(ing_list, safe=False)


# Изменение рецепта

@login_required
def recipe_edit(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)

    if request.user != recipe.author:
        return redirect('recipes:index')
    
    if request.method == "POST":
        form = RecipeForm(request.POST or None, files=request.FILES or None, instance=recipe)
        if form.is_valid():
            recipe = form.save(commit=False)
            recipe.author = request.user
            recipe.save()
            return redirect('recipes:index')

    form = RecipeForm(request.POST or None, files=request.FILES or None, instance=recipe)
    return render(request, 'change_recipe.html', {'form': form, 'recipe':recipe}) 


# Просмотр рецепта

def recipe_view(request, recipe_id, username):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    form = RecipeForm() # зачем? хз, но работает, трогать не хочу
    profile = get_object_or_404(User, username=username)
    return render(request, 'recipe.html', {'profile':profile, 'form':form, 'recipe':recipe, })


# Удаление рецепта

@login_required
def recipe_delete(request, recipe_id):
    recipe = Recipe.objects.get(id=recipe_id)
    if request.user != recipe.author:
        return redirect('recipes:index')
    else:
        recipe.delete()
        return redirect('recipes:index')


# Профиль пользователя

def profile(request, username):
    profile = get_object_or_404(User, username=username)
    recipe_list = Recipe.objects.filter(author=profile.pk).order_by("-pub_date")
    form = RecipeForm(request.POST or None, files=request.FILES or None)
    recipe_all = Recipe.objects.filter(author=profile.pk).order_by("-pub_date").all()
    recipe_count = recipe_all.count() # а надо ли?
    paginator = Paginator(recipe_list, 6) # показывать по 6 записей на странице.
    page_number = request.GET.get('page') # переменная в URL с номером запрошенной страницы
    page = paginator.get_page(page_number)
    cache.clear()
    return render(request, 'profile.html', {'profile':profile, 'recipe_list':recipe_list, 'form':form, 'page':page, 'paginator':paginator,})


class Favorites(View):
    pass


class Purchases(View):
    pass


class Subscription(View):
    pass


# Просмотр избранных рецептов

@login_required
def favors_view(request, username):
    #profile = get_object_or_404(User, username=username)
    recipe_list = Favors.objects.filter(user=request.user).all()
    form = RecipeForm()
    paginator = Paginator(recipe_list, 6) # показывать по 6 записей на странице.
    page_number = request.GET.get('page') # переменная в URL с номером запрошенной страницы
    page = paginator.get_page(page_number)
    cache.clear()
    return render(request, 'favorite.html', {'recipe_list':recipe_list, 'form':form})


# Просмотр списка подписок

@login_required
def subs_view(request, username):
    profile = get_object_or_404(User, username=username)
    subs_list = Follow.objects.filter(user=request.user).all()
    paginator = Paginator(subs_list, 6) # показывать по 6 записей на странице.
    page_number = request.GET.get('page') # переменная в URL с номером запрошенной страницы
    page = paginator.get_page(page_number)
    cache.clear()
    return render(request, 'my_subs.html', {'subs_list':subs_list})


# Просмотр списка покупок

@login_required
def shop_list(request, username):
    return render(request, 'shopList.html')