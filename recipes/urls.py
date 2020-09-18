from django.urls import path

from . import views


app_name = "recipes"

urlpatterns = [
    # Основные страницы
    # отображение главной страницы
    path("", views.index, name="index"),
    # профиль пользователя
    path("recipe/<username>/", views.profile, name='profile'),
    # просмотр подписок
    path("subs/<username>/", views.subs_view, name='subs'),
    # просмотр избранных рецептов
    path('favors/<username>/', views.favors_view, name='favors'),
    # просмотр листа покупок
    path('shop', views.shop, name='shop'),
    # скачивание списка покупок
    path('download', views.download, name='download'),
  
    # Блок работы с рецептами
    # добавление нового рецепта
    path('new-recipe', views.new_recipe, name='new_recipe'),
    # редактирование рецепта
    path('recipe/<int:recipe_id>/edit', views.recipe_edit, name='recipe_edit'),
    # удаление рецепта
    path('recipe/<int:recipe_id>/delete', views.recipe_delete, name='recipe_delete'),
    # просмотр рецепта
    path('recipe/<username>/<int:recipe_id>/', views.recipe_view, name='recipe_view'),

    # Блок с ебучим js
    # запрос на урл для автозаполнения поля ингридиентов
    path('api/ingredients', views.Ingredients.as_view(), name='ingredients'),
    # запрос по апи для добавления рецепта в избранное
    path('api/favorites', views.Favorites.as_view(), name='add_favor'),
    # удаление рецепта из избранного
    path('api/favorites/<int:recipe_id>', views.Favorites.as_view(), name='remove_favor'),
    # запрос на добавление подписки к автору
    path('api/subscriptions', views.Subscription.as_view(), name='add_subs'),
    # запрос на удаление подписки
    path('api/subscriptions/<int:author_id>', views.Subscription.as_view(), name='remove_subs'),
    # добавление в список покупок
    path('api/purchases', views.Purchases.as_view(), name='add_to_shop'),
    # удаление из списка покупок
    path('api/purchases/<int:recipe_id>', views.Purchases.as_view(), name='remove_from_shop'),


]
