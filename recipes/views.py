import json

from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, FileResponse, HttpResponse, HttpRequest
from django.views.generic import View
from django.core.cache import cache
from django.template.response import TemplateResponse
from django.conf import settings

from .models import Recipe, Tag, Ingrindient, Amount, User, Follow, Favors, ShopList
from .forms import RecipeForm
from .utils import generate_shop_list, get_ingrindients, tags_converter


# Отображение главной страницы

def index(request):
    stroka = HttpRequest.get_full_path(request)
    #print(stroka[0:9]=='/?filters')
    if stroka[0:9] == '/?filters':
    #if request.GET:
        if dict(request.GET)['filters']:
            
            tags_values = dict(request.GET)['filters'] # получаем названия тегов из запроса
            tags_id = tags_converter(tags_values) # преобразуем в список из id моделей
            recipe_list = Recipe.objects.filter(tag__in=tags_id).order_by('-pub_date').all()
        else:
            tags_id = [1, 2, 3]
            recipe_list = Recipe.objects.filter(tag__in=tags_id).order_by('-pub_date').all()    
    else:
        recipe_list = Recipe.objects.order_by('-pub_date').all()
    #print(request.get_full_path())
    paginator = Paginator(recipe_list, 6) # показывать по 6 рецептов на странице.
    page_number = request.GET.get('page') # переменная в URL с номером запрошенной страницы
    page = paginator.get_page(page_number)
    cache.clear()

    return render(request, 'index.html', { 'page':page,'paginator':paginator, 
                                            }) 

    
# Создание нового рецепта.

@login_required
def new_recipe(request):
    # костыль для отображения счетчика покупок
    shop_list = ShopList.objects.filter(user=request.user).all()
    
    if request.method == 'POST':
        form = RecipeForm(request.POST or None, files=request.FILES or None)
        ingrindients = get_ingrindients(request)
        
        if bool(ingrindients) is False:
            form.add_error(None, 'Добавьте ингредиенты')

        elif form.is_valid():
            recipe = form.save(commit=False)
            recipe.author = request.user
            recipe.save()
            
            for item in ingrindients: # это нужно для нормального заполнения БД ингредиентами
                Amount.objects.create(
                    units=ingrindients[item], 
                    ingrindient=Ingrindient.objects.filter(name=item).all()[0], 
                    recipe=recipe
                    )

            form.save_m2m() # это нужно для нормального заполнения тегами
            return redirect('recipes:index')
    
    else:
        form = RecipeForm(request.POST or None, files=request.FILES or None)
    
    return render(request, 'new_recipe.html', {'form': form, 'count':len(shop_list)})
    

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
    shop_list = ShopList.objects.filter(user=request.user).all()
    ingrindients = get_ingrindients(request)

    # удаляем все записи об ингредиентах из базы
    Amount.objects.filter(recipe=recipe).all().delete()

    if request.user != recipe.author:
        return redirect('recipes:index')
    
    if request.method == "POST":
        form = RecipeForm(request.POST or None, files=request.FILES or None, instance=recipe)
        
        if form.is_valid():
            recipe = form.save(commit=False)
            recipe.author = request.user
            recipe.save()
            
            for item in ingrindients: # это нужно для нормального заполнения БД ингредиентами
                Amount.objects.create(
                    units=ingrindients[item], 
                    ingrindient=Ingrindient.objects.filter(name=item).all()[0], 
                    recipe=recipe
                    )
            form.save_m2m() # это нужно для нормального заполнения тегами
            return redirect('recipes:index')

    form = RecipeForm(request.POST or None, files=request.FILES or None, instance=recipe)
    
    return render(request, 'change_recipe.html', {'form': form, 'recipe':recipe, 'count':len(shop_list),}) 


# Просмотр рецепта

def recipe_view(request, recipe_id, username):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    profile = get_object_or_404(User, username=username)
    
    if request.user.is_authenticated: 
        is_subs = Follow.objects.filter(user=request.user).filter(author=recipe.author.id) # костыль на меняющуюся кнопку подписки

        return render(request, 'recipe.html', {'profile':profile, 'recipe':recipe, 'subs':is_subs, })

    else:
        return render(request, 'recipe.html', {'profile':profile, 'recipe':recipe, \
                                                })


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
    
    if request.GET:
        tags_values = dict(request.GET)['filters'] # получаем названия тегов из запроса
        tags_id = tags_converter(tags_values) # преобразуем в список из id моделей
        recipe_list = Recipe.objects.filter(tag__in=tags_id, author=profile.pk).order_by('-pub_date').all()

    else:
        recipe_list = Recipe.objects.filter(author=profile.pk).order_by("-pub_date")
    
    paginator = Paginator(recipe_list, 6) # показывать по 6 рецептов на странице.
    page_number = request.GET.get('page') # переменная в URL с номером запрошенной страницы
    page = paginator.get_page(page_number)
    cache.clear()
    
    if request.user.is_authenticated: 
        
        is_subs = Follow.objects.filter(user=request.user).filter(author=profile.id) # костыль на меняющуюся кнопку подписки

        return render(request, 'profile.html', {'profile':profile, 'recipe_list':recipe_list, \
                                                'page':page, 'paginator':paginator, 'subs':is_subs, \
                                               }
                        )
    
    else:
        return render(request, 'profile.html', {'profile':profile, 'recipe_list':recipe_list, \
                                                'page':page, 'paginator':paginator, }
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
    def post(self, request):
        recipe_id = json.loads(request.body)['id']
        recipe = Recipe.objects.get(id=recipe_id)
        is_shop = ShopList.objects.filter(user=request.user).filter(recipe=recipe_id)

        if is_shop:
            return JsonResponse({'recipe_id':'recipe'})

        else:
            ShopList.objects.create(user=request.user, recipe=recipe)
            print()
            return JsonResponse({'recipe_id':'recipe'})

    def delete(self, request, recipe_id):
        recipe = Recipe.objects.get(id=recipe_id)
        ShopList.objects.filter(user=request.user).filter(recipe=recipe).delete()
        return JsonResponse({'succes':'True'})


# добавление и удаление профиля в подписки

class Subscription(View):
    
    def post(self, request):
        author_id = json.loads(request.body)['id']
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
    
    if request.GET:
        tags_values = dict(request.GET)['filters'] # получаем названия тегов из запроса
        tags_id = tags_converter(tags_values) # преобразуем в список из id моделей
        pre_recipe_list = list(Recipe.objects.filter(tag__in=tags_id).order_by('-pub_date').all())
        recipe_list = Favors.objects.filter(recipe__in=pre_recipe_list).all()

    else:
        recipe_list = Favors.objects.filter(user=request.user).all()
    
    paginator = Paginator(recipe_list, 6) # показывать по 6 рецептов на странице.
    page_number = request.GET.get('page') # переменная в URL с номером запрошенной страницы
    page = paginator.get_page(page_number)
    cache.clear()
    
    return render(request, 'favorite.html', {'recipe_list':recipe_list, })


# Просмотр списка подписок

@login_required
def subs_view(request):
    subs_list = Follow.objects.filter(user=request.user).all()
    paginator = Paginator(subs_list, 6) # показывать по 6 профилей на странице.
    page_number = request.GET.get('page') # переменная в URL с номером запрошенной страницы
    page = paginator.get_page(page_number)
    cache.clear()
    
    shop_list = ShopList.objects.filter(user=request.user).all()

    # Блок для передачи списка рецептов для отрисовки в карточках пользователей
    card_page = []
    for item in subs_list:
        author = item.author.id
        for_card = Recipe.objects.filter(author=author).all()
        card_page.append(for_card)

    return render(request, 'my_subs.html', {'subs_list':subs_list, 'card_page':card_page, \
                                            'page':page, 'paginator':paginator,  \
                                            }
                    )


# Просмотр списка покупок

def shop(request):
    shop_list = ShopList.objects.filter(user=request.user).all()
    return render(request, 'shopList.html', {'shop_list':shop_list})


# скачивание списка покупок

@login_required
def download(request):
    result = generate_shop_list(request) # вызов скрипта на составление файла
    filename = 'ingredients.txt' # именуем файл
    response = HttpResponse(result, content_type='text/plain') # наполняем и отдаем
    response['Content-Disposition'] = 'attachment; filename={0}'.format(filename)
    return response
    