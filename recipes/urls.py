from django.urls import path

from . import views


app_name="recipes"

urlpatterns = [
    path("", views.index, name="index"), # отображение главной страницы
    path("recipe/<username>/", views.profile, name='profile'), # профиль пользователя
    path("subs/<username>/", views.subs_view, name='subs'), # просмотр подписок
    path('favors/<username>/', views.favors_view, name='favors'), # просмотр избранных рецептов
    path('shop/<username>/', views.shop_list, name='shop'), # просмотр листа покупок

    path('new-recipe/', views.new_recipe, name='new_recipe'), # добавление нового рецепта
    path('recipe/<int:recipe_id>/edit/', views.recipe_edit, name='recipe_edit'), # редактирование рецепта
    path('recipe/<int:recipe_id>/delete', views.recipe_delete, name='recipe_delete'), # удаление рецепта
    path('recipe/<username>/<int:recipe_id>/', views.recipe_view, name='recipe_view'), # просмотр рецепта

    # Блок с ебучим js
    path('api/ingredients/', views.Ingrindients.as_view(), name='ingredients'), # запрос на урл для автозаполнения поля ингридиентов
    path('api/favorites/', views.Favorites.as_view(), name='add_favor'), # запрос по апи для добавления рецепта в избранное
    path('api/favorites/<int:recipe_id>/', views.Favorites.as_view(), name='remove_favor'), # удаление рецепта из избранного
    path('api/subscriptions/', views.Subscription.as_view(), name='add_subs'), # запрос на добавление подписки к автору
    path('api/subscriptions/${id}/', views.Subscription.as_view(), name='remove_subs'), # запрос на удаление подписки
    path('api/purchases/', views.Purchases.as_view(), name='add_to_shop'), # добавление в список покупок
    path('api/purchases/<int:recipe_id>/', views.Purchases.as_view(), name='remove_from_shop'), # удаление из списка покупок


]


# {% url 'recipes:recipe_view' recipe.author.username recipe.id %}
# {% url 'recipes:profile' recipe.author.username %}