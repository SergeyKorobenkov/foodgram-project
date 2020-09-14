from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model() 


class Tag(models.Model):
    value = models.CharField('Значение', max_length=255)
    style = models.CharField('Префикс для стиля шаблона', max_length=255, null=True)
    name = models.CharField('Имя тега в шаблоне', max_length=255, null=True)

    def __str__(self):
       return self.name

# Правильное название должно быть "Ingredient", но я уже и так много интима с этой моделью получил.
# Пусть останется так.
class Ingrindient(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    dimension = models.CharField(max_length=10, null=True, blank=True)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    title = models.CharField(max_length=100, verbose_name='Название рецепта')
    ingrindient = models.ManyToManyField(Ingrindient, through="Amount", through_fields=('recipe', 'ingrindient'))
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="recipe_author")
    tag = models.ManyToManyField(Tag)
    duration = models.IntegerField(default=1, verbose_name='Время приготовления')
    description = models.TextField()
    image = models.ImageField(upload_to='recipes/')
    pub_date = models.DateTimeField("date published", auto_now_add=True)
    slug = models.SlugField()
    
    
    def __str__(self):
        return self.title


class Amount(models.Model):
    units = models.IntegerField(default=1)
    ingrindient = models.ForeignKey(Ingrindient, on_delete=models.CASCADE, related_name='ingrindient')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    def __str__(self):
        return self.ingrindient.dimension



class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='follower') # тот который подписывается
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following') # тот на которого подписываются

    def __str__(self):
       return self.user.username


class Favors(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favor_by') # кто сохраняет
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='favor') # что сохраняет
    
    def __str__(self):
       return self.recipe.title


class ShopList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='buyer')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    def __str__(self):
       return self.recipe.title