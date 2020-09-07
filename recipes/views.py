from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.http import JsonResponse
from django.views.generic import View
from django.core.cache import cache

from .models import Recipe, Tag, Ingrindient, Amount, User
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
    return render(request, 'formRecipe.html', {'form': form})
    

# Класс для автозаполнения поля ингридиента.
# Общается по API.js с фронтом и ищет совпадения введенного текста с базой.

class Ingrindients(View):
    def get(self, request):
        text = request.GET['query']
        print(text)

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
    return render(request, 'formChangeRecipe.html', {'form': form}) 


# Просмотр рецепта

def recipe_view(request, recipe_id, username):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    form = RecipeForm()
    profile = get_object_or_404(User, username=username)
    return render(request, 'recipe.html', {'profile':profile, 'form':form, 'recipe':recipe, })


# Профиль пользователя

def profile(request, username):
    profile = get_object_or_404(User, username=username)
    recipe_list = Recipe.objects.filter(author=profile.pk).order_by("-pub_date")
    form = RecipeForm(request.POST or None, files=request.FILES or None)
    recipe_all = Recipe.objects.filter(author=profile.pk).order_by("-pub_date").all()
    recipe_count = recipe_all.count() # а надо ли?
    return render(request, 'profile.html', {'profile':profile, 'recipe_list':recipe_list, 'form':form})
