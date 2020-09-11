# Generated by Django 3.1.1 on 2020-09-11 18:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0008_shoplist'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tag',
            name='slug',
        ),
        migrations.RemoveField(
            model_name='tag',
            name='title',
        ),
        migrations.AddField(
            model_name='recipe',
            name='tag',
            field=models.ManyToManyField(to='recipes.Tag'),
        ),
        migrations.AddField(
            model_name='tag',
            name='name',
            field=models.CharField(max_length=255, null=True, verbose_name='Имя тега в шаблоне'),
        ),
        migrations.AddField(
            model_name='tag',
            name='style',
            field=models.CharField(max_length=255, null=True, verbose_name='Префикс для стиля шаблона'),
        ),
        migrations.AddField(
            model_name='tag',
            name='value',
            field=models.CharField(default=1, max_length=255, verbose_name='Значение'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='recipe',
            name='slug',
            field=models.SlugField(default=1),
            preserve_default=False,
        ),
    ]