# Generated by Django 4.1 on 2022-09-05 15:07

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0019_alter_recipe_tags'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='favorite',
            options={
                'ordering': ['user'],
                'verbose_name': 'Избранное',
                'verbose_name_plural': 'Избранное',
            },
        ),
        migrations.AlterModelOptions(
            name='recipe',
            options={
                'ordering': ['pub_date'],
                'verbose_name': 'Рецепт',
                'verbose_name_plural': 'Рецепты',
            },
        ),
        migrations.AlterModelOptions(
            name='shoppingcart',
            options={
                'ordering': ['user'],
                'verbose_name': 'Список покупок',
                'verbose_name_plural': 'Списки покупок',
            },
        ),
        migrations.AddField(
            model_name='recipe',
            name='pub_date',
            field=models.DateTimeField(
                auto_now_add=True,
                default=django.utils.timezone.now,
                verbose_name='Дата публикации',
            ),
            preserve_default=False,
        ),
    ]
