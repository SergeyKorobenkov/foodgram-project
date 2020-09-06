from django.contrib import admin

# Register your models here.
from .models import Recipe, Tag, Ingrindient, Amount


class AmountInLine(admin.TabularInline):
    model = Amount
    extra = 1


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('pk','title', 'author', 'duration', 'description','pub_date',)
    search_fields = ('title',)
    list_filter = ('pub_date',)
    inlines = (AmountInLine, )


class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'slug')
    search_fields = ('title',)
    list_filter = ('title',)
    empty_value_display = '-пусто-'


class IngreientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'dimension')
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'


class AmountAdmin(admin.ModelAdmin):
    fields = ('ingrindient', 'recipe', 'amount',)
    search_fields = ('ingrindient', 'recipe',)

admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Ingrindient, IngreientAdmin)
admin.site.register(Amount, AmountAdmin)