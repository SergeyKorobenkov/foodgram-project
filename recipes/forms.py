from django import forms
from .models import Recipe
from django.forms import ModelForm


class RecipeForm(ModelForm):
    class Meta:
        model = Recipe
        fields = ('title', 'duration', 'description', 'image',)
        required = {'title':True, }
        
        