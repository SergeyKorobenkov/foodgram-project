from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model() 


class Tag(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)


class Ingrindient(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    dimension = models.CharField(max_length=10, null=True, blank=True)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    title = models.CharField(max_length=100, verbose_name='Название рецепта')
    ingrindient = models.ManyToManyField(Ingrindient, through="Amount", through_fields=('recipe', 'ingrindient'))
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="recipe_author")
    #tag = models.ManyToManyField(Tag, related_name='tag')
    duration = models.IntegerField(default=1, verbose_name='Время приготовления')
    description = models.TextField()
    image = models.ImageField(upload_to='recipes/', blank=True, null=True)
    pub_date = models.DateTimeField("date published", auto_now_add=True)
    slug = models.SlugField(null=True, blank=True)
    
    
    def __str__(self):
        return self.title


class Amount(models.Model):
    units = models.IntegerField(default=1)
    ingrindient = models.ForeignKey(Ingrindient, on_delete=models.CASCADE, related_name='ingrindient')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)



#class Follow(models.Model):
    #user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='follower') #тот который подписывается
    #author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following') #тот на которого подписываются#

#    def __str__(self):
#       return self.text
