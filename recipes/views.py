from django.shortcuts import render
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.http import JsonResponse
from django.views.generic import View

from .models import Recipe, Tag, Ingrindient, Amount
from .forms import RecipeForm


def index(request):
    #recipe_list = Recipe.objects.order_by("-pub_date").all()
    #paginator = Paginator(post_list, 6) # показывать по 10 записей на странице.
    #page_number = request.GET.get('page') # переменная в URL с номером запрошенной страницы
    #age = paginator.get_page(page_number) # получить записи с нужным смещением
    #form = RecipeForm(request.POST or None, files=request.FILES or None)
    #cache.clear()
    #return render(request, 'index.html', {'page': page, 'paginator': paginator, 'form': form})
    return render(request, 'index.html')



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