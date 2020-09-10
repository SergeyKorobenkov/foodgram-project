from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.http import JsonResponse
from django.views.generic import View
from django.core.cache import cache
import json

from .models import Recipe, Tag, Ingrindient, Amount, User, Follow, Favors
from .forms import RecipeForm


# Отображение главной страницы

def index(request):
    recipe_list = Recipe.objects.order_by('-pub_date').all()
    form = RecipeForm(request.POST or None, files=request.FILES or None)
    
    # дальше идет костыль, но по другому не работает =(
    favor_list = Favors.objects.filter(user=request.user).all() # нужно что бы заполнить звездочку
    total_favor = [] # нужно что бы сравнить элементы в шаблоне
    for item in recipe_list: # для элементов из списка рецептов
        for fitem in favor_list: # для элемента из списка избранного 
            if item.title == fitem.recipe.title: # сравниваем title каждого элемента
                total_favor.append(item.title) # и кладем в список если они одинаковые
    # конец костыля. Да, сложно, неоптимально и вообще некрасиво, фу таким быть. Однако работает же!
    
    paginator = Paginator(recipe_list, 6) # показывать по 6 записей на странице.
    page_number = request.GET.get('page') # переменная в URL с номером запрошенной страницы
    page = paginator.get_page(page_number)
    cache.clear()
    return render(request, 'index.html', {'form':form, 'page':page, 'paginator':paginator, 'favor_list':total_favor})


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
# вставить костыль для звездочки
def recipe_view(request, recipe_id, username):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    profile = get_object_or_404(User, username=username)

    # ну да, это тоже костыль, и что теперь?
    is_favor = Favors.objects.filter(user=request.user).filter(recipe=recipe_id)
        
    return render(request, 'recipe.html', {'profile':profile, 'recipe':recipe, 'favor':is_favor})


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
    
    paginator = Paginator(recipe_list, 6) # показывать по 6 записей на странице.
    page_number = request.GET.get('page') # переменная в URL с номером запрошенной страницы
    page = paginator.get_page(page_number)
    cache.clear()
    
    # дальше идет костыль, но по другому не работает =(
    favor_list = Favors.objects.filter(user=request.user).all() # нужно что бы заполнить звездочку
    total_favor = [] # нужно что бы сравнить элементы в шаблоне
    for item in recipe_list: # для элементов из списка рецептов
        for fitem in favor_list: # для элемента из списка избранного 
            if item.title == fitem.recipe.title: # сравниваем title каждого элемента
                total_favor.append(item.title) # и кладем в список если они одинаковые
    # конец костыля. Да, сложно, неоптимально и вообще некрасиво, фу таким быть. Однако работает же!
    
    author = User.objects.get(username=username)
    is_follow = Follow.objects.filter(user=request.user).filter(author=author.id)

    return render(request, 'profile.html', {'profile':profile, 'recipe_list':recipe_list, \
                                            'form':form, 'page':page, 'paginator':paginator, \
                                            'favor_list':total_favor, 'follow':is_follow,}
                    )


# добавление и удаление рецепта в избранные
# Очередная мутная шляпа с api.js, работает через пень-колоду.
# Но работает =)

class Favorites(View):
    
    def post(self, request):
        recipe_id = json.loads(request.body)['id']
        recipe = Recipe.objects.get(id=recipe_id)
        is_favor = Favors.objects.filter(user=request.user).filter(recipe=recipe_id)
        if is_favor:
            return JsonResponse({'recipe_id':'recipe'})
        else:
            Favors.objects.create(user=request.user, recipe=recipe)
            return JsonResponse({'recipe_id':'recipe'})

    def delete(self, request, recipe_id):
        recipe = Recipe.objects.get(id=recipe_id)
        Favors.objects.filter(user=request.user).filter(recipe=recipe).delete()
        return JsonResponse({'succes':'True'})


# добавление и удаление рецепта в список покупок

class Purchases(View):
    pass


# добавление и удаление профиля в подписки

class Subscription(View):
    
    def post(self, request):
        # небольшой костыль, так как из request приходит не author_id, a recipe_id
        # поэтому приходится извращаться и ходить по моделям доставая из рецепта id автора
        author_id = json.loads(request.body)['id']
        print(author_id)
        #recipe_item = Recipe.objects.get(id=recipe_id)
        #author_id = recipe_item.author.id
        author = User.objects.get(id=author_id)
        is_follow = Follow.objects.filter(user=request.user).filter(author=author_id)
        
        if is_follow:
            return JsonResponse({'succes':'True'})
        
        else:
            Follow.objects.create(user=request.user, author=author)
            return JsonResponse({'succes':'True'})

    def delete(self, request, recipe_id):
        # я без понятия почему он тут присылает переменную под названием recipe_id
        # но в ней он хранит id автора, как ни странно. Какого маракуйя я так и не понял.
        author = User.objects.get(id=recipe_id)
        Follow.objects.filter(user=request.user).filter(author=author).delete()
        return JsonResponse({'succes':'True'})


# Просмотр избранных рецептов

@login_required
def favors_view(request, username):
    recipe_list = Favors.objects.filter(user=request.user).all()
    form = RecipeForm()
    paginator = Paginator(recipe_list, 6) # показывать по 6 записей на странице.
    page_number = request.GET.get('page') # переменная в URL с номером запрошенной страницы
    page = paginator.get_page(page_number)
    cache.clear()
    
    # дальше идет костыль, но по другому не работает =(
    favor_list = Favors.objects.filter(user=request.user).all() # нужно что бы заполнить звездочку
    total_favor = [] # нужно что бы сравнить элементы в шаблоне
    for item in recipe_list: # для элементов из списка рецептов
        for fitem in favor_list: # для элемента из списка избранного 
            if item.recipe.title == fitem.recipe.title: # сравниваем title каждого элемента
                total_favor.append(item.recipe.title) # и кладем в список если они одинаковые
    # конец костыля. Да, сложно, неоптимально и вообще некрасиво, фу таким быть. Однако работает же!
    
    return render(request, 'favorite.html', {'recipe_list':recipe_list, 'form':form, 'favor_list':total_favor})


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