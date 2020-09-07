from django.urls import path

from . import views
app_name="recipes"

urlpatterns = [
    path("", views.index, name="index"), # отображение главной страницы
    path("recipe/<username>", views.profile, name='profile'), # профиль пользователя

    path('new-recipe/', views.new_recipe, name='new_recipe'), # добавление нового рецепта
    path('recipe/<int:recipe_id>/edit', views.recipe_edit, name='recipe_edit'), # редактирование рецепта
    #path('recipe/<int:recipe_id>/delete', views.recipe_delete, name='recipe_delete'), # удаление рецепта
    path('recipe/<username>/<int:recipe_id>', views.recipe_view, name='recipe_view'), # просмотр рецепта


    path('api/ingredients', views.Ingrindients.as_view(), name='ingredients'), # запрос на урл для автозаполнения поля ингридиентов


]


# {% url 'recipes:recipe_view' recipe.author.username recipe.id %}
# {% url 'recipes:profile' recipe.author.username %}