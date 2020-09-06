from django.urls import path

from . import views
app_name="recipes"

urlpatterns = [
    path("", views.index, name="index"), # отображение главной страницы

    path('new-recipe/', views.new_recipe, name='new_recipe'), # добавление нового рецепта

    path('api/ingredients', views.Ingrindients.as_view(), name='ingredients'), # запрос на урл для автозаполнения поля ингридиентов


]