from django.contrib import admin

# Register your models here.
from .models import Recipe, Tag, Ingredient, Amount, Follow, Favors, ShopList


class AmountInLine(admin.TabularInline):
    model = Amount
    extra = 1


class TagInLine(admin.TabularInline):
    model = Tag
    extra = 1


class RecipeAdmin(admin.ModelAdmin):
    def favor_count(self, obj):
        return Favors.objects.filter(recipe=obj).count()

    favor_count.short_description = 'Кол-во добавлений в избранное'

    list_display = ('pk', 'title', 'author', 'pub_date', 'favor_count')
    search_fields = ('title',)
    list_filter = ('pub_date',)
    inlines = (AmountInLine,)
    readonly_fields = ('favor_count', )


class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'value', 'name')
    empty_value_display = '-пусто-'


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'dimension')
    search_fields = ('title',)
    list_filter = ('title',)
    empty_value_display = '-пусто-'


class AmountAdmin(admin.ModelAdmin):
    fields = ('ingredient', 'recipe', 'units',)
    search_fields = ('ingredient', 'recipe',)


class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')
    fields = ('user', 'author')


class FavoritesAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    fields = ('user', 'recipe')


class ShopListAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    fields = ('user', 'recipe')


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Amount, AmountAdmin)
admin.site.register(Follow, FollowAdmin)
admin.site.register(Favors, FavoritesAdmin)
admin.site.register(ShopList, ShopListAdmin)
